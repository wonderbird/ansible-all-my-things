# Playbooks

Playbooks to setup and update my computers and virtual machines.

To run these playbooks, either start the test system as described in
([../test/README.md](../test/README.md)) or run them with your own inventory. My inventory is defined in [../inventory/](../inventory/).

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
cd inventory## Adding a developer vm with Hetzner

### Prerequisites

You need a cloud project with [Hetzner](https://www.hetzner.com/). The project
should contain a firewall definition, which allows inbound SSH connections.

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
ansible dev -a "hostname"
```

### Run the playbook

The playbook will install the development server including an XFCE desktop.

If the playbook is executed for the first time and the destkop user does not
exist, then provide the password for the new user via the --extra-vars option:

```bash
cd inventory
ansible-playbook ../playbooks/developer-vm.yml --extra-vars 'desktop_user_password=yourpassword'
```

Now you can log in either via SSH as `root` or via Remote Desktop as the
desktop_user_name user specified in the playbook.

ansible dev -a "hostname"
```

### Run the playbook

The playbook will install the development server including an XFCE desktop.

If the playbook is executed for the first time and the destkop user does not
exist, then provide the password for the new user via the --extra-vars option:

```bash
cd inventory
ansible-playbook ../playbooks/developer-vm.yml --extra-vars 'desktop_user_password=yourpassword'
```

Now you can log in either via SSH as `root` or via Remote Desktop as the
desktop_user_name user specified in the playbook.
