# Work with a VM

## Log in to the desktop user

The username of the desktop user is set configured in
[../playbooks/vars-usernames.yml](../playbooks/vars-usernames.yml). Here, we
assume it is `galadriel`.

The section [Important Concepts](./important-concepts.md) provides more
information about the different users and their purposes.

To log in, use the following command:

```shell
# Receive the IP address of the server from the Hetzner API
export IPV4_ADDRESS=$(hcloud server list -o json | jq '.[0].public_net.ipv4.ip' | tr -d '"'); echo "IPv4 address: \"$IPV4_ADDRESS\""

# Receive the IP address from Tart
export IPV4_ADDRESS=$(tart ip lorien); echo "IPv4 address: \"$IPV4_ADDRESS\""

# Use the IP address of localhost for Docker provisioner
export IPV4_ADDRESS=127.0.0.1

# Connect to the server via SSH, forwarding the RDP port
ssh -L 3389:localhost:3389 galadriel@$IPV4_ADDRESS
```

Now you can open an RDP client like Remmina, Windows App or Remote Desktop to
connect to the server at `localhost` with user `galadriel`.

## Restore a backup of the desktop user

Restoring the backup is a part of the [../configure.yml](../configure.yml)
playbook.

To restore a backup of the desktop user later manually, use the following
command:

```shell
ansible-playbook ./restore.yml
```

## Backup working directory of desktop user

To backup the working directory of the desktop user, use the following command:

```shell
ansible-playbook ./backup.yml
```
