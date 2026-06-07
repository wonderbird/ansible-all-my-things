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

**Decision**: Parse `vagrant ssh-config <hostname>` output after `vagrant up`
completes, extracting the `HostName` field.

**Rationale**: `vagrant ssh-config` outputs stable, human-readable key-value
pairs (`HostName`, `Port`, `IdentityFile`) immediately after provisioning.
Parsing is a single `grep`/`awk` shell pipeline. No additional tooling required.

**Implementation sketch**:

```yaml
- name: Get VM connection details
  shell: vagrant ssh-config {{ hostname }} | grep HostName | awk '{print $2}'
  args:
    chdir: "~/.local/share/ansible-vms/{{ hostname }}"
  register: vm_ip
  changed_when: false
```

**Alternatives considered**:

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
