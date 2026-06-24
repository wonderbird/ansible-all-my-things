# Backup and Restore

## Backup the working directory of the desktop user

`backup.yml` backs up the working directory and application settings of the
first desktop user listed in
[/inventories/group_vars/all/vars.yml](../../inventories/group_vars/all/vars.yml).

The backup source host has no default — it must always be passed explicitly
with `-e backup_from_host=<host>`:

```shell
ansible-playbook ./backup.yml -e backup_from_host=hobbiton
```

See [/backup.yml](../../backup.yml) for why no default exists, and
[/playbooks/backup/](../../playbooks/backup/) for the per-application
playbooks it imports (Chromium, VS Code, RTK, keyring, and more).

## Restore a backup of the desktop user

> [!ATTENTION]
> The same backup is restored for all users

Restoring the backup is part of the
[/configure-linux.yml](../../configure-linux.yml) playbook and runs
automatically during `provision.yml`.

To restore a backup later manually, use the following command. Unlike
backup, restore always targets the `linux` host group, so no `-e` flag is
required:

```shell
ansible-playbook ./restore.yml
```

See [/playbooks/restore/](../../playbooks/restore/) for the per-application
playbooks it imports.

## After Restore

Two steps cannot be automated and must be done manually afterward:

```shell
claude login
```

```shell
omc setup
```

---

Previous: [Work with a Virtual Machine](./work-with-vm.md)
