# Data Model: Create and Destroy VM Playbooks

## Entities

### HostnamePool

Ordered list of available VM hostnames. Defined once; shared by both playbooks.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `hostname_pool` | `list[str]` | `playbooks/vars/hostname_pool.yml` | Ordered; allocation is sequential (first unused) |

**Initial values**: `vulcan`, `romulus`, `betazed`, `qonos`, `risa`,
`cardassia`, `bajor`, `veridian`, `remus`, `baku`

**Validation rules**:

- List MUST be non-empty at playbook start (Principle XII — fail loud if pool
  file missing or empty)
- All names MUST be lowercase strings (Ansible inventory host keys are
  case-sensitive; lowercase avoids ambiguity)

**State**: Append-only. Names are never removed from the pool file; they are
allocated (in-use) or available based on inventory membership.

---

### InventoryEntry

Per-VM record in `inventories/vagrant_tart.yml`. A VM is "known" if and only
if its hostname appears in `all.hosts`.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `ansible_host` | `str` (IPv4) | Yes | Tart-assigned IP; retrieved via `vagrant ssh-config` after `vagrant up` |
| `ansible_port` | `int` | Yes | Always `22` |
| `ansible_user` | `str` | Yes | Always `admin` (Tart Ubuntu image default) |
| `ansible_ssh_private_key_file` | `str` (path) | Yes | `~/.local/share/ansible-vms/<hostname>/.vagrant/machines/<hostname>/tart/private_key` |

**Group membership** (all three groups updated on create/destroy):

| Group | Purpose |
|-------|---------|
| `all` | Root group; carries connection vars |
| `linux` | Selects Linux-targeted roles |
| `vagrant_tart` | Selects Tart-specific vars |

**Validation rules**:

- `destroy-vm.yml` MUST assert hostname is present in `all.hosts` before any
  action (FR-010, Principle XII)
- `create-vm.yml` MUST NOT create an entry for a hostname already in `all.hosts`
  (idempotency guard)

**State transitions**:

```text
[absent]  →  create-vm.yml  →  [present in all + linux + vagrant_tart]
[present] →  destroy-vm.yml →  [absent from all + linux + vagrant_tart]
```

---

### VMConfig

Ansible variables controlling VM resource allocation. Defined as defaults;
overridable via `--extra-vars`.

| Variable | Default | Type | Notes |
|----------|---------|------|-------|
| `vm_cpus` | `4` | `int` | vCPU count |
| `vm_memory_mb` | `8192` | `int` | RAM in MB |
| `vm_disk_gb` | `45` | `int` | Disk size in GB |

**Source**: `playbooks/vars/hostname_pool.yml` carries the pool; VMConfig
defaults are defined at the top of `create-vm.yml` (or a dedicated vars file
included by it).

---

### VagrantfileContext

Ephemeral data set assembled at create time; used to template the per-VM
Vagrantfile.

| Field | Type | Source |
|-------|------|--------|
| `hostname` | `str` | Selected from HostnamePool |
| `vm_cpus` | `int` | VMConfig |
| `vm_memory_mb` | `int` | VMConfig |
| `vm_disk_gb` | `int` | VMConfig |
| `vm_dir` | `str` (path) | `~/.local/share/ansible-vms/{{ hostname }}` |

The Vagrantfile is written to `vm_dir/Vagrantfile` using `ansible.builtin.template`.

---

## Relationships

```text
HostnamePool (ordered list)
    │  first unused name
    ▼
hostname (str)
    │  drives
    ├──▶  VagrantfileContext  ──template──▶  ~/.local/share/ansible-vms/<hostname>/Vagrantfile
    └──▶  InventoryEntry      ──written──▶   inventories/vagrant_tart.yml
```
