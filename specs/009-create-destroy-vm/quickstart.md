# Quickstart: Create and Destroy VM Playbooks

## Prerequisites

- macOS ARM64 host
- Vagrant installed (`brew install vagrant`)
- vagrant-tart plugin installed (`vagrant plugin install vagrant-tart`)
- Tart CLI installed (`brew install tart`)

## Create a VM

```bash
ansible-playbook playbooks/create-vm.yml
```

Prints the assigned hostname on completion. The VM is immediately reachable
via the inventory.

Override resources:

```bash
ansible-playbook playbooks/create-vm.yml -e vm_cpus=2 -e vm_memory_mb=4096
```

## Destroy a VM

```bash
ansible-playbook playbooks/destroy-vm.yml -e hostname=vulcan
```

## Check inventory

```bash
cat inventories/vagrant_tart.yml
```

## SSH into a VM

```bash
ansible vulcan -m ping
ssh -i ~/.local/share/ansible-vms/vulcan/.vagrant/machines/vulcan/tart/private_key \
    -p 22 admin@<ansible_host>
```

## Pool management

Available hostnames live in `playbooks/vars/hostname_pool.yml`. Append new
names to extend the pool. Names are allocated sequentially; no restart needed.
