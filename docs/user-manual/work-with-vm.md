# Work with a Virtual Machine

## Log in as the desktop user

The username of the desktop user is configured in `/inventories/group_vars/all/vars.yml`. Here, we assume it is `galadriel`.

The section [Important Concepts](./important-concepts.md) provides more information about the different users and their purposes.

Look up the VM's IP address with:

```shell
ansible-inventory --host <hostname>
```

Then use the following command to log in (replace `<ip>` with
`ansible_host` from the output):

```shell
# Connect to the server via SSH, forwarding the RDP port and the SSH port
ssh -L 3389:localhost:3389 -L 8022:localhost:22 galadriel@<ip>
```

Now you can open an RDP client like Remmina, Windows App or Remote Desktop to connect to the server at `localhost` with user `galadriel`.

## GNOME keyring password is login password

The GNOME keyring needs to be unlocked when you launch an application using it, e.g. Visual Studio Code. The password is configured in [/inventories/group_vars/all/vault.yml](../inventories/group_vars/all/vault.yml).

## Backup and restore

See [Backup and Restore](./backup-restore.md) for backing up the desktop
user's working directory and restoring it later.

---

Previous: [Create a Virtual Machine](./create-vm.md)
Next: [Backup and Restore](./backup-restore.md)
