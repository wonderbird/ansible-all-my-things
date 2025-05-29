# Work with a VM

## Start a VM

Depending on your preferred provider, follow one of the following guides:

- [Start VM in Hetzner Cloud](./create-hetzner-vm.md)
- [Start VM using Vagrant with Docker](../test/docker/README.md)
- [Start VM using Vagrant with Tart](../test/tart/README.md)

## Log in as the desktop user

The username of the desktop user is set configured in
[../playbooks/vars-usernames.yml](../playbooks/vars-usernames.yml). Here, we
assume it is `galadriel`.

The section [Important Concepts](./important-concepts.md) provides more
information about the different users and their purposes.

Set the environment variable `IPV4_ADDRESS` as described in
[Obtain Remote IP Address](./obtain-remote-ip-address.md).

Then use the following command to log in:

```shell
# Connect to the server via SSH, forwarding the RDP port
ssh -L 3389:localhost:3389 galadriel@$IPV4_ADDRESS
```

Now you can open an RDP client like Remmina, Windows App or Remote Desktop to
connect to the server at `localhost` with user `galadriel`.

## GNOME keyring password is login password

The GNOME keyring needs to be unlocked when you launch an application using
it, e.g. Visual Studio Code. The password for the default keyring is the same
as the login password of the desktop user.

## Backup working directory of desktop user

To backup the working directory of the desktop user, use the following command:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./backup.yml
```

## Restore a backup of the desktop user

Restoring the backup is a part of the [../configure.yml](../configure.yml)
playbook.

To restore a backup of the desktop user later manually, use the following
command:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./restore.yml
```
