# Solution Design: Create and Destroy VM Playbooks

## File Structure

```text
playbooks/
  create-vm.yml
  destroy-vm.yml
  vars/
    hostname_pool.yml
  tasks/
    create/
      tart.yml
    destroy/
      tart.yml
```

## Name Pool Design

The hostname pool is defined in `playbooks/vars/hostname_pool.yml` as a single
shared ordered list of Star Trek TNG planet names. Both playbooks include this
file.

At runtime, `create-vm.yml`:

1. Loads the pool from `playbooks/vars/hostname_pool.yml`.
2. Reads `inventories/vagrant_tart.yml` to determine which names are already
   in use.
3. Selects the first name not present in inventory.
4. Fails loud if no unused name remains (Principle XII).

## Inventory Strategy

`inventories/vagrant_tart.yml` is a static YAML file with groups `all`,
`linux`, and `vagrant_tart`.

On create, `create-vm.yml` appends a host entry:

```yaml
ansible_host: <VM IP>
ansible_port: 22
ansible_user: admin
ansible_ssh_private_key_file: <path to Tart-generated private key>
```

On destroy, `destroy-vm.yml` removes all group references to the hostname.

## VM Resource Defaults

Resource defaults are defined as Ansible variables so operators can override
them via extra-vars without modifying the Vagrantfile template:

| Variable | Default |
| -------- | ------- |
| `vm_cpus` | `4` |
| `vm_memory_mb` | `8192` |
| `vm_disk_gb` | `45` |

## Idempotency and Guards

- `playbooks/tasks/create/tart.yml` uses `creates:` guards on shell tasks or
  checks for existing `.vagrant/` state (Principle I).
- Pool-check logic ensures a hostname already present in inventory is never
  selected (FR-003).

## Definition of Done

- `create-vm.yml` creates a Tart VM (Ubuntu 24.04 LTS, macOS ARM64) with no
  extra-vars required for the common case.
- VM resources default to 4 vCPU / 8 GB RAM / 45 GB disk and are overridable
  via extra-vars.
- Assigned hostname is drawn from `playbooks/vars/hostname_pool.yml` (TNG
  planet names) and printed on completion.
- Pool exhaustion fails loud with an actionable error before any infrastructure
  action.
- `inventories/vagrant_tart.yml` is updated correctly on create and destroy.
- `destroy-vm.yml` fails loud when the specified hostname is not in inventory.
- All acceptance criteria in the spec pass.
