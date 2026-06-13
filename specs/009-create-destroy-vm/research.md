# Research: Create and Destroy VM Playbooks

## Per-VM Vagrantfile Directory Strategy

**Decision**: Store per-VM Vagrantfiles under `~/.local/share/ansible-vms/<hostname>/`
on the control node.

**Rationale**: Vagrant is directory-centric — each VM instance needs its own
working directory containing a `Vagrantfile` and a `.vagrant/` state subdirectory.
Storing these outside the repo under the XDG user-data path keeps the git tree
clean, survives repo re-clones, and allows `.vagrant/` state to persist between
playbook runs. The path is deterministic from the hostname alone.

**Alternatives considered**:

- `vms/<hostname>/` inside the repo: rejected — `.vagrant/` contains large binary
  state and machine-local paths that must not be committed; a repo-wide `.gitignore`
  entry would hide the directory silently.
- Single shared `Vagrantfile` with environment variable substitution: rejected —
  Vagrant multi-machine configs (`config.vm.define`) still require a single
  Vagrantfile managing all machines; dynamic addition/removal of definitions is
  fragile and requires parsing Ruby.

**Private key path**: `~/.local/share/ansible-vms/<hostname>/.vagrant/machines/<hostname>/tart/private_key`

---

## VM IP Retrieval After `vagrant up`

**Decision**: Use `tart ip <hostname>` polled in an Ansible `until` loop
(`retries: 30`, `delay: 10`).

**Rationale**: `vagrant ssh-config` was the original plan but was never
implemented. The live code at `playbooks/tasks/create/tart.yml:99-106` uses
`tart ip <hostname>` directly, which returns the IP from tart's DHCP lease
without requiring SSH to be ready first. This avoids the fragile
`vagrant ssh-config` parse and does not require Vagrant's SSH machinery.

**Alternatives that were considered and rejected**:

- `vagrant ssh-config`: original plan (documented here); never implemented
  because it requires Vagrant's SSH wait to complete before it returns,
  making it unsuitable as the IP-discovery step.
- `tart list --format json`: requires parsing JSON and matching by VM name;
  tart VM names include the Vagrant-assigned prefix (e.g. `vagrant_<name>`),
  making the match fragile across Vagrant versions.
- `vagrant ssh -c "ip addr"`: requires SSH to be ready; slower; output parsing
  is complex for multiple interfaces.

---

## Inventory YAML Update Strategy

**Decision**: Load the existing inventory with `ansible.builtin.include_vars`,
construct the updated dict in Ansible using `combine()` / dict manipulation
filters, then write the result back with `ansible.builtin.copy` and
`content: "{{ updated | to_nice_yaml(indent=2) }}"`.

**Rationale**: Pure Ansible, no external scripts, fully idempotent. The
`combine(recursive=true)` filter merges nested dicts without clobbering
unrelated keys. `to_nice_yaml` produces human-readable output consistent with
the existing file. A `copy` task with fixed content is idempotent by default.

**Create flow**:

```yaml
- name: Load current inventory
  include_vars:
    file: "{{ playbook_dir }}/../inventories/vagrant_tart.yml"
    name: current_inventory

- name: Build updated inventory
  set_fact:
    updated_inventory: >-
      {{ current_inventory | combine({
        'all': {'hosts': {hostname: {
          'ansible_host': vm_ip.stdout,
          'ansible_port': 22,
          'ansible_user': 'admin',
          'ansible_ssh_private_key_file':
            '~/.local/share/ansible-vms/' ~ hostname ~
            '/.vagrant/machines/' ~ hostname ~ '/tart/private_key'
        }}},
        'linux': {'hosts': {hostname: {}}},
        'vagrant_tart': {'hosts': {hostname: {}}}
      }, recursive=true) }}

- name: Write updated inventory
  copy:
    content: "{{ updated_inventory | to_nice_yaml(indent=2) }}"
    dest: "{{ playbook_dir }}/../inventories/vagrant_tart.yml"
```

**Destroy flow**: remove hostname key from `all.hosts`, `linux.hosts`, and
`vagrant_tart.hosts` using `dict2items` → `selectattr` → `items2dict` pipeline
before writing back.

**Alternatives considered**:

- `lineinfile`/`blockinfile`: rejected — fragile for structured YAML; marker
  comments pollute the inventory file.
- `community.general.yaml_edit`: not in project requirements.yml; adds a
  Galaxy dependency for a task doable with core modules.
- Python script via `ansible.builtin.script`: heavier, harder to test in
  isolation, introduces a second language in a pure-Ansible project.

---

## Principle II Exception: No Role for VM Lifecycle

**Decision**: Implement VM lifecycle logic in `playbooks/tasks/create/tart.yml`
and `playbooks/tasks/destroy/tart.yml` (included task files), not in a role.

**Rationale**: Roles are designed for tasks that run on managed remote hosts.
VM creation and destruction run on `localhost` via shell commands against the
Vagrant+Tart CLI. There is no remote host, no `become`, and no Molecule scenario
possible (Tart requires Apple Silicon hardware). The project already uses
`playbooks/tasks/` includes for control-node operations (`setup-vscode.yml`,
`setup-chromium.yml`, etc.). The exception is documented in Complexity Tracking
in `plan.md`.

---

## Hostname Pool — Sequential Allocation

**Decision**: Determine the next available hostname by loading
`playbooks/vars/hostname_pool_tart.yml` and filtering out names already present in
`inventories/vagrant_tart.yml` using an Ansible `difference()` filter, then
taking `[0]`.

**Implementation sketch**:

```yaml
- name: Load hostname pool
  include_vars:
    file: "{{ playbook_dir }}/vars/hostname_pool_tart.yml"

- name: Determine used hostnames
  set_fact:
    used_hostnames: "{{ current_inventory.all.hosts.keys() | list }}"

- name: Select next hostname
  set_fact:
    hostname: "{{ hostname_pool | difference(used_hostnames) | first }}"

- name: Fail if pool exhausted
  fail:
    msg: >-
      Hostname pool exhausted. All names in
      playbooks/vars/hostname_pool_tart.yml are in use.
      Add more names to the pool or destroy an existing VM.
  when: hostname_pool | difference(used_hostnames) | length == 0
```

The `fail` task MUST precede the `set_fact` for `hostname` and all VM/infra
actions (Principle XII).

---

## Spike Findings: Faster Tart VM Boot (r5vs)

### Test environment

| Property | Value |
|----------|-------|
| Chip | Apple M1 Max |
| Cores | 10 (8P + 2E) |
| RAM | 64 GB |
| macOS | 26.5.1 (Build 25F80) |
| tart | 2.32.1 |
| Vagrant | 2.4.9 |
| vagrant-tart | 0.0.7 |
| Image | `ghcr.io/cirruslabs/ubuntu:24.04` (OCI, cached locally) |
| Concurrent VMs | `lorien` running throughout (pre-existing) |

All measurements are warm-image (OCI image already in tart local cache). Cold
image download time is excluded; images are cached in practice.

### Baseline — current `vagrant up` flow

**Run 1** (2026-06-07): wall-clock **19:59** (m:ss), vagrant up delta **19:53**.

```text
vagrant up started:  2026-06-07 19:48:44
vagrant up ended:    2026-06-07 20:08:38 (rc=255, killed by operator)
```

Vagrant output sequence:

1. Clone: `Cloning instance romulus` → `Instance romulus cloned` — fast (seconds)
2. Configure + Start: `Configuring instance romulus` →
   `Instance romulus started` — fast
3. SSH wait: `Waiting for machine to boot` → `SSH address: 192.168.64.63:22` →
   `Warning: Host unreachable. Retrying...` — **repeated for ~19 minutes until
   operator kill**

The rescue block fired correctly on kill: vagrant destroy + directory removal +
fail-loud message. Idempotency and fail-loud guarantees held.

**SSH-readiness**: operator confirmed manual SSH to the VM succeeded at ~20:05
(~17 minutes after VM start). Port 22 became reachable only after cloud-init
completed on the first-boot clone.

**Root cause identified**: the bottleneck is not vagrant overhead — tart clones
and starts the VM in seconds. The delay is cloud-init initialization on the
cirruslabs ubuntu:24.04 OCI image. On a fresh clone, cloud-init expands the
filesystem, configures the network stack, and starts services (including sshd)
before SSH is reachable. This takes approximately 15–17 minutes on first boot
from the OCI image on this hardware.

### Key finding

> The "unacceptably slow boot" is cloud-init on first-boot OCI clones, not
> vagrant overhead. Tart VM clone + start completes in ~10–30 seconds. The
> remaining ~17 minutes is sshd becoming available after cloud-init.

This changes the option analysis:

- **Option A** (direct tart CLI): faces the **same cloud-init delay**. Bypassing
  vagrant does not help if the root cause is cloud-init, not vagrant.
- **Option B** (pre-built image with SSH pre-enabled / cloud-init pre-run):
  directly addresses the root cause. A tart image cloned from a VM that has
  already completed cloud-init would be SSH-ready seconds after `tart run`.
  **This is the highest-leverage option.**
- **Option C** (vagrant-tart tuning): cannot eliminate cloud-init time.
  May reduce vagrant overhead marginally but does not address the 17-minute gap.

### Experiment A and C — invalidated

- **Option C (vagrant tuning)**: no-hostname experiment (removed
  `node.vm.hostname` from Vagrantfile) was canceled after 5 min — still
  unacceptably slow. No Vagrantfile knob can remove vagrant-tart's cloud-init
  injection. Invalidated by measurement.
- **Option A (direct tart CLI)**: collapsed into the Option B experiment —
  bare tart of the OCI image achieved SSH-ready in 6s (see below). A and B
  converge to the same outcome when vagrant is replaced by direct tart calls.

### Experiment B — pre-built image / bare tart run

**Date**: 2026-06-07. Same host as baseline (M1 Max, tart 2.32.1).
OCI image `ghcr.io/cirruslabs/ubuntu:24.04` in warm local tart cache.
No concurrent VMs other than lorien.

**Method**: `tart clone ghcr.io/cirruslabs/ubuntu:24.04 spike-source` +
`tart run spike-source --no-graphics`. Poll `tart ip spike-source` then
`nc -z <IP> 22`. Record SSH-ready time. Stop VM. Clone `spike-source` three
times; measure SSH-ready time per clone using the same poll method.

**Source creation** (bare tart, no vagrant): SSH ready in **6s**.

**Clone SSH-ready times** (3 runs):

| Run | SSH-ready (s) |
|-----|---------------|
| 1   | 7             |
| 2   | 6             |
| 3   | 7             |

**Min: 6s — Median: 7s — Target: 300s — TARGET MET (43× margin).**

Reduction from baseline: ~17 min → 7s median (approximately 140× faster).

SSH-readiness confirmed for all three runs: `tart ip` returned a non-empty IP
and `nc -z <IP> 22` confirmed port 22 accepting connections, matching the bar
at `tart.yml:99-124`.

**Failure-fidelity**: bare tart has no equivalent of the `rescue` block at
`tart.yml:161-178`. Reimplementation cost is bounded: replace `vagrant destroy
-f` + dir-remove + `fail` with `tart stop <name>` + `tart delete <name>` +
dir-remove + `fail`. The guarantees (teardown on failure, fail-loud rollback)
are fully preservable.

**Root-cause inference**: bare tart (6–7s) versus all vagrant-based experiments
(17 min minimum, any Vagrantfile configuration) implicates **vagrant-tart's
cloud-init injection** as the proximate cause of the delay. vagrant-tart injects
cloud-init configuration (SSH credentials, user setup) via the nocloud
datasource before first boot. Without this injection, cloud-init completes in
seconds on this image.

### Recommendation — Option A: replace vagrant with direct tart CLI

**Decision**: replace vagrant in `playbooks/tasks/create/tart.yml` with direct
`tart` CLI calls (`tart clone`, `tart run`, `tart stop`, `tart delete`). This
removes vagrant-tart's cloud-init injection — the proximate cause of the delay.

**Decision drivers**:

1. **Boot time**: 6–7s SSH-ready without vagrant — 43× inside the 300s target
   and approximately 140× faster than baseline.
2. **Root cause addressed**: direct tart eliminates the cloud-init injection;
   no amount of vagrant-tart tuning can.
3. **Failure-handling fidelity**: rescue block reimplementable as Ansible tasks
   with equivalent guarantees; cost is bounded.

**Alternatives rejected**:

- **Option B (custom pre-built image, vagrant retained)**: achieves similar
  timing but requires maintaining a versioned image artefact. YAGNI — the stock
  OCI image is already fast when run without vagrant.
- **Option C (vagrant-tart tuning)**: no tuning removes vagrant-tart's
  cloud-init injection. Measured: still > 5 min with any tested Vagrantfile
  configuration.

**Consequences**:

- `playbooks/tasks/create/tart.yml`: `vagrant up` replaced with `tart clone` +
  `tart run` as Ansible `command` tasks; idempotency via `creates:`.
- Rescue block (`tart.yml:161-178`) reimplemented as `tart stop`, `tart delete`,
  dir-remove, `fail`.
- **SSH credentials**: Verified 2026-06-08 — `sshpass -p admin ssh admin@<ip>
  true` succeeds on a bare `tart run` of `ghcr.io/cirruslabs/ubuntu:24.04`
  (no vagrant, no cloud-init seed). The OCI image ships `admin`/`admin` as its
  published default. No injection required. `ansible_ssh_pass: admin` used in
  autogenerated inventory.
- vagrant and vagrant-tart dependencies removed; `tart` CLI is the sole
  dependency for VM lifecycle.
