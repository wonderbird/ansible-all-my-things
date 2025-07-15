# Work with a Virtual Machine

## Log in as the desktop user

The username of the desktop user is set configured in `/playbooks/vars-secrets.yml`. Here, we assume it is `galadriel`.

The section [Important Concepts](./important-concepts.md) provides more information about the different users and their purposes.

Source the script [/configure.sh](../configure.sh) in order to set environment variables to work with the Virtual Machine:

```shell
source ./configure.sh
```

Then use the following command to log in:

```shell
# Connect to the server via SSH, forwarding the RDP port and the SSH port
ssh -L 3389:localhost:3389 -L 8022:localhost:22 galadriel@$IPV4_ADDRESS
```

Now you can open an RDP client like Remmina, Windows App or Remote Desktop to connect to the server at `localhost` with user `galadriel`.

## GNOME keyring password is login password

The GNOME keyring needs to be unlocked when you launch an application using it, e.g. Visual Studio Code. The password is configured in `/playbooks/vars-secrets.yml`.

## Backup working directory of desktop user

To backup the working directory of the first desktop user listed in `/playbooks/vars-secrets.yml`, use the following command:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./backup.yml
```

## Restore a backup of the desktop user

> [!ATTENTION]
> The same backup is restored for all users

Restoring the backup is a part of the [../configure.yml](../configure.yml) playbook.

To restore a backup later manually, use the following command:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./restore.yml
```

--

Previous: [Create a Virtual Machine](./create-vm.md)
