# Tech Context — feat.podman.role

## Technologies Used

- **Ansible 2.19+** — automation engine; all modules use `ansible.builtin.*`
  FQCNs; no Galaxy collections required for this role
- **Podman 4.x** — rootless container runtime; installed from Ubuntu apt
- **Ubuntu 22.04 LTS / 24.04 LTS** — primary target OS (24.04 ships
  Podman 4.x with native `--mount=type=cache` support)
- **buildah** (bundled with Podman) — OCI build backend; handles
  `RUN --mount=type=cache` without external BuildKit

## Development Setup

### Local Test VM

- Vagrant + Docker (Linux hosts) or Vagrant + Tart (macOS ARM64 hosts)
- SSH target configured for `vagrant` user
- `configure-linux-roles.yml` used to apply the role in isolation

### Acceptance Test (T020) — Actual Execution

T020 was run against the Hetzner Cloud VM `hobbiton` (Ubuntu, `galadriel`
user) instead of a local Vagrant VM. All four criteria passed:

- Podman 4.9.3 installed; `podman --version` succeeded
- `/etc/subuid` and `/etc/subgid` contain `galadriel:100000:65536`
- `podman build -t devcontainer .devcontainer/` succeeded
- `podman run --rm devcontainer ansible --version` → `ansible [core 2.20.4]`
- Second playbook run: zero `changed` tasks

Command used: `ansible-playbook configure-linux-roles.yml --limit hobbiton`
(no `-i` flag needed; `ansible.cfg` sets `inventory = ./inventories`)

### Test Procedure (from CONTRIBUTING.md)

1. Isolate the role: ensure only `podman` is active in
   `configure-linux-roles.yml`
2. Run: `ansible-playbook configure-linux-roles.yml --limit <target>`
3. Verify all four acceptance criteria (see `specs/006-podman-rootless-role/
   quickstart.md`)

## Spec Artifacts

All located at `specs/006-podman-rootless-role/`:

| File | Purpose |
| --- | --- |
| `spec.md` | Functional requirements, user stories, acceptance criteria |
| `plan.md` | Technical context, constitution check, source layout |
| `tasks.md` | 21 implementation tasks (T001–T021) |
| `research.md` | 6 resolved design decisions |
| `data-model.md` | Role variables, system file entities, task-flow diagram |
| `quickstart.md` | Local VM test procedure, acceptance test checklist |

## Constraints

- `become: true` must be set at play level (role does not set it per-task)
- `desktop_user_names` must contain valid system users; the role does not
  validate user existence (YAGNI) — an orphaned `/etc/subuid` entry is
  the failure mode for non-existent users
- Ansible Vault: not relevant for this role (no secrets)
- Architecture: the Ubuntu `podman` apt package supports AMD64 and ARM64
  natively — no architecture branching needed

## Molecule Testing

- **Versions**: `molecule>=24.0.0`, `molecule-plugins[podman]>=23.0.0`
- **Driver**: `podman` — requires `podman` binary in PATH (Ubuntu apt)
- **Test command**: `cd roles/<role-name> && molecule test`
- **Rule file**: `.cursor/rules/340-molecule-testing.mdc`
- **Key pitfalls**:
  - `&&` in YAML `>` folded scalars unreliable with Podman connection plugin
    → use separate `raw` tasks
  - `apt-get update -qq` fails in Ubuntu 24.04 apt 2.7.x → use `apt-get update`
  - `become: true` at play level tries sudo before sudo is installed → add
    `become: false` to bootstrap `raw` tasks
  - Unconditional file deletion (cleanup tasks) breaks idempotence
  - Use `ansible_facts['env']['PATH']` not `ansible_env.PATH` (removed 2.24)

## File Conventions

- YAML files: `#SPDX-License-Identifier: MIT-0` (no space after `#`)
- Markdown files: ATX headings, blank lines around lists, no trailing
  whitespace, one trailing newline, max 80 chars per line (MD013)
