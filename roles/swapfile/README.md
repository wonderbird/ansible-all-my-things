<!-- SPDX-License-Identifier: MIT-0 -->
# swapfile

Ansible role that creates a swap file on a Linux VM, activates it now and at
every boot, and lowers the kernel's swappiness so swap is used only when
memory gets really tight.

See [DESIGN.md](DESIGN.md) for non-obvious decisions.

## Boundary

The role creates and activates one swap file of one size. It does not resize
an existing swap file, manage swap partitions or zram, or choose a size for
the host. It never deactivates swap: taking a host out of the `swapfile`
group leaves its swap file active. Check mode (`--check`) is not supported:
later steps inspect the file that the skipped allocation would create.

A host already configured by hand with the same path, size, `fstab` line and
`/etc/sysctl.d/99-swappiness.conf` is adopted. If the host has not applied
that swappiness yet, e.g. no reboot since the file was written, the role
applies it and reports one change.

## Requirements

- Ansible 2.19+ with the `ansible.posix` collection
- A Linux VM (not a container) whose filesystem holding the swap file has
  room for it plus 1 GiB

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `swapfile_size_gb` | *(required)* | Swap file size in whole gigabytes. Set per host by the `swapfile` inventory group. |
| `swapfile_path` | `/swapfile` | Path of the swap file. |
| `swapfile_swappiness` | `10` | Value of `vm.swappiness`. |

## Opting a Host In

The role runs on hosts in the `swapfile` group, which carries each host's
`swapfile_size_gb`. A new VM joins it at creation:

```shell
ansible-playbook playbooks/create-vm.yml -e provider=hcloud -e swap_size_gb=2
```

An existing VM joins it through `enable-swapfile.yml`, then gets its swap file
from `configure-profile.yml` or `./scripts/run-role.sh <name> swapfile`:

```shell
ansible-playbook playbooks/enable-swapfile.yml -e provider=hcloud -e hostname=<name> -e swap_size_gb=2
```

A host with 4 GB RAM running OpenClaw works well with 2 GB swap. Docker and
Windows VMs are refused.

## Removing Swap from a Host

On the host:

```shell
sudo swapoff /swapfile
sudo sed -i '\|^/swapfile\s|d' /etc/fstab
sudo rm /swapfile /etc/sysctl.d/99-swappiness.conf
sudo sysctl vm.swappiness=60
```

## Testing

There is no Molecule scenario: a container may not activate swap. Test on a
local VM as described in
[Testing concepts](../../docs/architecture/concepts/testing.md).

## Dependencies

None.

## Example Playbook

```yaml
- hosts: swapfile
  become: true
  roles:
    - role: swapfile
```

## License

MIT-0
