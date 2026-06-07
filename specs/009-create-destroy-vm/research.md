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

**Decision** (superseded — see live implementation): Use `tart ip <hostname>`
polled in an Ansible `until` loop (`retries: 30`, `delay: 10`).

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
`playbooks/vars/hostname_pool.yml` and filtering out names already present in
`inventories/vagrant_tart.yml` using an Ansible `difference()` filter, then
taking `[0]`.

**Implementation sketch**:

```yaml
- name: Load hostname pool
  include_vars:
    file: "{{ playbook_dir }}/vars/hostname_pool.yml"

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
      playbooks/vars/hostname_pool.yml are in use.
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

```
vagrant up started:  2026-06-07 19:48:44
vagrant up ended:    2026-06-07 20:08:38 (rc=255, killed by operator)
```

Vagrant output sequence:

1. Clone: `Cloning instance romulus` → `Instance romulus cloned` — fast (seconds)
2. Configure + Start: `Configuring instance romulus` → `Instance romulus started` — fast
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

### Remaining experiments

Experiments A and C are deprioritised given the root-cause finding. Option B
(pre-built image) is the recommended path to investigate next.

Concrete approach for Option B:
1. Run a fresh clone to completion (let cloud-init finish, ~17 min).
2. Stop the VM (`tart stop <name>`).
3. Export/snapshot it as a new local tart image (`tart export` or copy the
   stopped VM directory under a new name in `~/.tart/vms/`).
4. Measure: `tart clone <pre-built-image> <new-name>` + `tart run` + time to
   SSH-ready. Expected: seconds, not minutes.
5. If confirmed fast: evaluate whether to maintain this pre-built image as a
   versioned artefact (triggers Principle II version-update wiring) or rebuild
   it on demand.

### Failure-fidelity note

Any Option B implementation must preserve the rescue/cleanup/fail-loud
guarantees of `playbooks/tasks/create/tart.yml:161-178`. If Vagrant is retained
(wrapping the pre-built image), the rescue block is unchanged. If Vagrant is
dropped (direct tart CLI), the rescue block must be re-implemented in shell or
Ansible tasks: `tart stop <name>`, `tart delete <name>`, remove VM dir, fail
with message.

### Recommendation (preliminary — Option B experiment pending)

Pursue a pre-built tart image with cloud-init already completed as the
implementation approach. This is the only option that addresses the measured
root cause. A full Option B experiment should confirm SSH-ready time is under
the 300-second target before committing to the approach.
