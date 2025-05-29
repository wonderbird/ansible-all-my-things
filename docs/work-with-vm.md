# Work with a VM

## Log in to the desktop user

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
