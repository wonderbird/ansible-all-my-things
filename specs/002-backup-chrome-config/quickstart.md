# Quickstart: Google Chrome Backup and Restore

> **Note for implementers**: Keep this file updated as you implement the
> feature. If command syntax, paths, or test steps change during
> implementation, update this document in the same commit.

## Prerequisites

- Google Chrome is installed on the target host (AMD64 only — see tags below).
- The backup destination directory exists or `BACKUP_DIR` is set.
- The target host is `hobbiton`. Substitute your host name if different.

## Backup

Run the full backup (all applications):

```shell
ansible-playbook backup.yml -e backup_from_host=hobbiton
```

Run only the Google Chrome backup:

```shell
ansible-playbook playbooks/backup/google-chrome-settings.yml -e backup_from_host=hobbiton
```

## Restore

Run the full restore (all applications):

```shell
ansible-playbook restore.yml --limit hobbiton
```

Restore only Google Chrome:

```shell
ansible-playbook playbooks/restore/google-chrome-settings.yml --limit hobbiton
```

## Acceptance Test (manual, AMD64 only)

> This test must be performed on an AMD64 desktop host. It cannot run on
> Tart (ARM64) VMs or Docker-based Vagrant boxes.

1. Open Google Chrome and enable the home button:
   **Settings → Appearance → Show home button → On**.
2. Run the backup:

   ```shell
   ansible-playbook playbooks/backup/google-chrome-settings.yml -e backup_from_host=hobbiton
   ```

3. Verify the archive exists:

   ```shell
   ls -lh configuration/home/my_desktop_user/backup/google-chrome-backup.tar.gz
   ```

4. Remove the Chrome configuration from the host:

   ```shell
   rm -rf ~/.config/google-chrome/Default
   ```

5. Launch Google Chrome — confirm it shows the first-run configuration dialog
   (Chrome has no profile to load).
6. Close Google Chrome.
7. Remove the configuration again (Chrome recreated default files on launch):

   ```shell
   rm -rf ~/.config/google-chrome/Default
   ```

8. Run the restore:

   ```shell
   ansible-playbook playbooks/restore/google-chrome-settings.yml --limit hobbiton
   ```

9. Launch Google Chrome — confirm:
   - The first-run configuration dialog does **not** appear.
   - The home button is visible in the toolbar.

## Notes

- These playbooks carry the `not-supported-on-vagrant-docker` and
  `not-supported-on-vagrant-arm64` tags and are automatically skipped on
  Docker-based or ARM64 Vagrant VMs.
- `not-supported-on-vagrant-docker` applies because Docker Vagrant boxes do
  not include a desktop environment.
- `not-supported-on-vagrant-arm64` applies because Google Chrome has no ARM64
  Linux package.
- The backup excludes cache, history, and ephemeral storage. Saved passwords
  (`Login Data`) **are** included in the backup.
