# Product Context: feat.backup-chrome-config

## Why this project exists

`ansible-all-my-things` automates the provisioning and ongoing configuration of
the owner's personal infrastructure. Without it, setting up a new machine or
recovering from a disaster requires hours of manual work: installing software,
configuring preferences, restoring credentials and browser profiles.

## Problems this feature solves

After an OS reinstall or on a new machine, Google Chrome loses all bookmarks,
extensions, saved passwords, and preferences. The user must reconfigure
everything from scratch. This feature ensures Chrome's profile is included in the
same automated backup/restore cycle that already covers Chromium, VS Code, Cursor,
and Claude settings.

## How it should work

- Running `ansible-playbook backup.yml -e backup_from_host=hobbiton` backs up
  all applications including Chrome in one step.
- Running `ansible-playbook restore.yml --limit hobbiton` restores all
  applications including Chrome in one step.
- The user notices nothing special about Chrome — it behaves identically to
  Chromium backup/restore from the operator's perspective.

## User experience goals

- Zero extra commands: Chrome is part of the standard backup/restore run.
- Faithful restore: after restore, Chrome opens with the same settings, home
  button visible, no first-run configuration dialog.
- Clean restore: the old profile is removed before the backup is applied, so
  there is no config bleed from a previous state.
