# Research: Docker Provider for Create and Destroy VM Playbooks

## Provider Dispatch in `create-vm.yml` / `destroy-vm.yml`

**Decision**: Add a `provider` extra-var (default `tart`) at the top of both
playbooks. Use a single `include_tasks` whose `file:` path is templated with
`{{ provider }}`, e.g. `tasks/create/{{ provider }}.yml`.

**Rationale**: `ansible.builtin.include_tasks` accepts a templated path,
letting one task selects between `tart.yml` and `docker.yml` without an
`if`/`else` block. The Tart branch (`tasks/create/tart.yml`,
`tasks/destroy/tart.yml`) is byte-for-byte unchanged, which directly satisfies
FR-017 (no behavior change for the default/`tart` path) — there is no shared
conditional logic that could regress it.

**Validation**: `provider` MUST be validated against the allowed set
(`tart`, `docker`) with an `assert` before dispatch, per Principle XII —
an unrecognized provider value would otherwise produce a confusing
"file not found" error from `include_tasks`.

**Alternatives considered**:

- Separate top-level playbooks (`create-vm-docker.yml`): rejected — FR-001
  explicitly specifies a single `provider` extra-var on the existing
  playbooks; a second playbook would duplicate the pre/post structure
  (hostname assertion, resource-default vars) already in `create-vm.yml` /
  `destroy-vm.yml`.
- `when:`-guarded duplicate task lists inline in the playbook: rejected —
  violates Principle XI (DRY) and Principle II (playbooks must only
  orchestrate, not contain task implementation logic).

---

## Docker Image Build Guard (FR-013)

**Decision**: Check for the existence of `ansible-vm-docker:latest` via
`docker image inspect ansible-vm-docker:latest`, parsed with `failed_when:
false` and `changed_when: false`, then run `docker build` only `when: <image
not found>`.

**Implementation sketch**:

```yaml
- name: Check whether the Docker image already exists
  ansible.builtin.command:
    cmd: docker image inspect ansible-vm-docker:latest
  register: docker_image_check
  changed_when: false
  failed_when: false

- name: Build the Docker image if it does not exist
  ansible.builtin.command:
    cmd: >-
      docker build -t ansible-vm-docker:latest
      --build-arg DOCKER_ROOT_PASSWORD={{ docker_root_password }}
      {{ playbook_dir }}/files/docker
  when: docker_image_check.rc != 0
  changed_when: true
```

**Rationale**: `docker image inspect` returns rc=0 if the image exists and
non-zero otherwise — a clean idempotent existence check requiring no extra
tooling, mirroring the `creates:` guard on `tart clone` in
`playbooks/tasks/create/tart.yml:76-79`. This is the exact mechanism resolved
by the spec's clarification: build only if the tag is absent, never
auto-rebuild.

**Alternatives considered**:

- `community.docker.docker_image` module: rejected — not in
  `requirements.yml`; adds a Galaxy collection dependency for a one-line CLI
  check the project already does for Tart via `command` + `creates`/`rc`
  checks.
- `docker images -q ansible-vm-docker:latest` (returns empty string if
  absent): rejected — `docker image inspect` rc-based check is more direct
  and avoids parsing stdout for emptiness.

---

## Container Run, Port Discovery, and SSH Readiness (FR-005, FR-014)

**Decision**: Start the container with:

```bash
docker run -d --privileged --name <hostname> --hostname <hostname> \
  --cpus 2 --memory 4g -p 127.0.0.1::22 ansible-vm-docker:latest
```

Then discover the published host port with:

```bash
docker port <hostname> 22/tcp
```

which prints `127.0.0.1:<port>`. Parse the port with a regex/split filter,
assert it is non-empty, then poll SSH readiness with
`ansible.builtin.wait_for_connection` (or `wait_for: port=<port>
host=127.0.0.1`), mirroring the `tart ip` poll loop in
`playbooks/tasks/create/tart.yml:105-129`.

**Rationale**: `-p 127.0.0.1::22` (empty host port) tells Docker to pick a
free ephemeral port and bind it only to loopback, satisfying FR-005's
`ansible_host: 127.0.0.1` / dynamic `ansible_port` requirement and avoiding
exposing the SSH port on all interfaces. `docker port` is the canonical way
to query the resulting mapping. Systemd-as-PID-1 plus `--privileged` is the
documented pattern for running systemd inside Docker (cgroups access),
required so `sshd.service` starts under systemd as specified in FR-013.

**Validation**: the parsed port MUST be asserted non-empty/numeric before use
(Principle XII) — a malformed `docker port` response must fail loudly rather
than write a broken inventory entry.

**Alternatives considered**:

- Fixed host port (e.g. `-p 2222:22`): rejected — collides across multiple
  containers; FR-002 requires creating a new container per invocation, so a
  fixed port would fail on the second container.
- `docker inspect` with a Go-template / JSON path for
  `NetworkSettings.Ports`: equivalent to `docker port` but more verbose to
  parse in Ansible; `docker port` already returns the exact `host:port`
  string needed.

---

## Inventory YAML Update Strategy (Docker)

**Decision**: Reuse the exact pattern documented in
`specs/009-create-destroy-vm/research.md` ("Inventory YAML Update Strategy"):
`include_vars` to load `inventories/docker_autogenerated.yml` (or initialize
an empty `all`/`linux`/`docker` skeleton if absent, mirroring
`tasks/create/tart.yml:38-58`), `combine(recursive=true)` to merge in the new
host entry, `to_nice_yaml(indent=2)` + `copy` to write it back. Destroy
mirrors `tasks/destroy/tart.yml:70-99` (`dict2items` / `selectattr` /
`items2dict` to remove the hostname from all three groups).

**Rationale**: Identical mechanism already validated and in production for
the Tart provider; reusing it keeps the two providers structurally
consistent (Principle XI) and avoids introducing a new YAML-manipulation
technique for a near-identical problem.

**Groups**: `all`, `linux`, `docker` (FR-004) — parallel to the Tart
provider's `all`, `linux`, `tart`.

---

## Rescue Block on Creation Failure (FR-015)

**Decision**: Wrap the container-run-through-inventory-write sequence in a
`block`/`rescue`, where `rescue` runs `docker stop <hostname>` and
`docker rm <hostname>` (both `failed_when: false`, since the container may
not have reached a running state) before `ansible.builtin.fail`.

**Rationale**: Directly mirrors `playbooks/tasks/create/tart.yml:170-186`
(`tart stop` + `tart delete` + fail-loud message). `docker stop` on a
container that was never started, or `docker rm` on one that doesn't exist,
both exit non-zero — `failed_when: false` allows the rescue to proceed
regardless of how far creation got, matching the Tart rescue's tolerance.

---

## Destroy Flow: Stale Inventory / Stale Container Handling (FR-009, FR-010)

**Decision**: Mirror `playbooks/tasks/destroy/tart.yml` exactly, substituting
the Tart existence check (`stat` on `~/.tart/vms/<hostname>`) with
`docker container inspect <hostname>` (`failed_when: false`,
`changed_when: false`, rc==0 means it exists).

- Hostname not in `inventories/docker_autogenerated.yml` → `assert`/`fail`
  before any Docker action (FR-010), matching
  `tasks/destroy/tart.yml:8-13`'s hostname-assertion pattern but checking
  inventory presence rather than the `hostname` var's mere definedness.
- Hostname in inventory but container absent from Docker → warn (`debug`),
  skip `docker stop`/`docker rm`, still clean inventory (FR-009), matching
  `tasks/destroy/tart.yml:50-68`.

**Rationale**: Identical shape to the proven Tart destroy flow; only the
existence-check command differs (`docker container inspect` vs `stat` on the
Tart VM directory). This satisfies FR-009/FR-010/FR-016's edge case
requirements with no novel logic.

---

## Dockerfile: systemd + sshd + root/password auth (FR-013)

**Decision**: Base on `ubuntu:24.04`. Install `systemd`, `openssh-server`,
`sudo` (and any package needed for `--privileged` systemd boot, e.g.
`dbus`). Set `PermitRootLogin yes` and `PasswordAuthentication yes` in
`/etc/ssh/sshd_config` (or a drop-in under `/etc/ssh/sshd_config.d/`). Set
the root password at build time via `ARG DOCKER_ROOT_PASSWORD` →
`RUN echo "root:$DOCKER_ROOT_PASSWORD" | chpasswd`. `ENTRYPOINT
["/sbin/init"]` (systemd as PID 1), with `sshd.service` enabled
(`systemctl enable ssh`).

**Build-arg vs runtime secret**: `docker_root_password` (from
`playbooks/vars/docker_credentials.yml`) is passed as a `--build-arg` at
image-build time, since FR-013 specifies the password is "set at build time
via `chpasswd`". Because the image is built once and reused (FR-013), the
password is baked into the image layer for the lifetime of
`ansible-vm-docker:latest` — rebuilding (deleting the image tag) is required
to rotate it. This is consistent with FR-013's "no automatic rebuild"
constraint and the Tart provider's equivalent (`tart_credentials.yml` /
`tart_admin_password` is also a fixed, non-rotated default).

**Rationale**: This is the standard documented approach for running systemd
under Docker with `--privileged` (used widely for systemd-based test/CI
images). `ubuntu:24.04` is an LTS release, giving the longest support window
of any currently-available Ubuntu base image, and aligns the Docker
provider's base OS with the Tart provider's image (also Ubuntu 24.04),
keeping both providers on the same guest OS version. Password auth mirrors
the Tart provider's `ansible_ssh_pass` mechanism (FR-005), keeping `sshpass`
as the sole new-dependency-free auth path (per Assumptions).

**Alternatives considered**:

- SSH key-based auth: rejected — FR-005 and FR-013 explicitly specify
  password auth via `ansible_ssh_pass` / `chpasswd`, mirroring the Tart
  provider; introducing keys would be a second auth mechanism for no stated
  benefit (YAGNI).
- Non-systemd entrypoint running `sshd` directly (e.g.
  `CMD ["/usr/sbin/sshd", "-D"]`): rejected — FR-013 explicitly requires
  "systemd as the container entrypoint and `sshd` enabled [via systemd]".

---

## Principle II Exception: No Role for Docker Provider Lifecycle

**Decision**: Implement Docker provider lifecycle logic in
`playbooks/tasks/create/docker.yml` and `playbooks/tasks/destroy/docker.yml`
(included task files), not in a role — same exception already accepted and
documented for the Tart provider in `specs/009-create-destroy-vm/research.md`
("Principle II Exception: No Role for VM Lifecycle") and
`specs/009-create-destroy-vm/plan.md` (Complexity Tracking).

**Rationale**: The Docker provider, like the Tart provider, runs entirely on
`localhost`, orchestrating a local VM-provider CLI (`docker`) — it provisions
infrastructure that Molecule itself could target, rather than being a role
that Molecule could test. No new exception category is introduced; this is
the same accepted pattern extended to a second provider.
