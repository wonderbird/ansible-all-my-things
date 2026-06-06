# Contract: create-vm.yml

## Invocation

```bash
ansible-playbook playbooks/create-vm.yml
ansible-playbook playbooks/create-vm.yml -e vm_cpus=2 -e vm_memory_mb=4096 -e vm_disk_gb=30
```

## Parameters

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `vm_cpus` | No | `4` | vCPU count for the new VM |
| `vm_memory_mb` | No | `8192` | RAM in MB |
| `vm_disk_gb` | No | `45` | Disk size in GB |

No extra-vars are required for the common case (SC-001).

## Preconditions

- At least one hostname in `playbooks/vars/hostname_pool.yml` is not present
  in `inventories/vagrant_tart.yml` (otherwise fails before any VM action)
- Vagrant and the vagrant-tart plugin are installed on the control node
- Tart CLI is installed and authenticated on the macOS ARM64 control node

## Postconditions (on success)

- A new Tart VM is running with the assigned hostname
- `inventories/vagrant_tart.yml` contains an entry for the new VM in groups
  `all`, `linux`, and `vagrant_tart`
- A Vagrantfile exists at `~/.local/share/ansible-vms/<hostname>/Vagrantfile`
- The assigned hostname is printed as a debug message on completion

## Failure modes

| Condition | Behaviour |
|-----------|-----------|
| Pool exhausted | Fails immediately with error naming `playbooks/vars/hostname_pool.yml`; no VM or infra action taken |
| Vagrant/Tart unavailable | Shell task fails explicitly; no inventory entry written |
| IP retrieval fails | Task fails with error; inventory write does not proceed |

## Idempotency

Not idempotent by design — each invocation creates one new VM (FR-001).
Re-running against an existing VM is prevented by the pool-check: a hostname
already in inventory is never re-selected.
