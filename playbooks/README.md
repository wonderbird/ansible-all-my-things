# Playbooks

This folder contains only the playbooks to setup and update my computers and
virtual machines.

The ansible configuration and inventory files are in the
[../inventory/](../inventory/) folder.

To run these playbooks, either start the test system as described in
([../test/README.md](../test/README.md)) or run them with your own inventory.

## Add a developer vm with Hetzner

### Prerequisites

You need a cloud project with [Hetzner](https://www.hetzner.com/). The project
should contain a firewall definition, which allows

- inbound ICMP requests,
- inbound SSH connections on port 22,
- inbound RDP connections on port 3389.
- any outbound connections.

Your SSH key must be registered, so that new servers can use it. This will
allow root login via SSH.

### Create the VM

Create a new server using the
[Server](https://console.hetzner.cloud/projects/10607445/servers) menu.

Select the following options:

- Location: Helsinki
- Image: Ubuntu 24.04
- Type: Shared vCPU / x86 (Intel/AMD) - CX32
- Networking
  - IPv4 disabled
  - IPv6 enabled
  - no private network
- SSH Key: Select your SSH key
- Volumes: none
- Firewall: Select your firewall
- Backups: none
- Placement groups: none
- Labels: none
- Cloud config: none
- Name: `<pick a name and add it to your inventory>`

When the server is created, its IPv6 network is displayed. The server address is
the first address in the network range, i.e. replace `::/64` by `::1` to get
the address.

Update the inventory file [../inventory/hosts.ini](../inventory/hosts.ini) with
the new server's IP address.

Verify that the server is reachable via SSH:

```bash
cd inventory
ansible dev -a "hostname" --extra-vars 'ansible_user=root'
```

### Configure access and secure SSH

The following playbook must be executed first, so that the ansible user can
use sudo. It must be executed as root, because no other users exist yet.

```bash
cd inventory
ansible-playbook ../playbooks/configure-access.yml --extra-vars 'ansible_user=root'
```

### Install other playbooks

The sequence of installation for the other playbooks is irrelevant. However, I
recommend to start with `setup-basics.yml`.

Adapt the command to install playbooks as needed:

```bash
cd inventory

# Basic configuration: Timezone, Install updates
ansible-playbook ../playbooks/setup-basics.yml

# Install Homebrew and homebrew packages
ansible-playbook ../playbooks/setup-homebrew.yml

# Enable remote desktop and install desktop environment
ansible-playbook ../playbooks/setup-desktop.yml

ansible-playbook ../playbooks/<playbook>.yml
```
