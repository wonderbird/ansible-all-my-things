# Tasks

The following task list follows a simple kanban board approach. Each heading
represents a workflow step of the development proces. WiP targets are given
in parentheses at the end of the heading.

## Done

- [x] Add some additional users to the `desktop_users` list in `vars-secrets.yml`
- [x] Move the default desktop user into the `desktop_users` list
- [x] Change `setup-users.yml` so that it considers the new `desktop_users` array
- [x] Update all code tailored for the old `my_desktop_user` and `my_desktop_user_password` to use the new `desktop_users` array from `vars-secrets.yml`
- [x] Verify for all desktop users, that the restored backups work (especially, because the owner and group were changed after extracting)
- [x] Fix: Visual Studio Code Installation is broken. It seems as if the microsoft package repository has been integrated into the standard apt sources. Verify that assumption. Then fix the issue.
- [x] Update the template `vars-secrets-template.yml`
- [x] Update the documentation
- [ ] Keep `vars-usernames.yml` only when required in the changed backup/restore files

## Ongoing (1)

## Prioritized next (1-2)

- [ ] Setup a default GNOME keyring for all desktop users
- [ ] Use a separate, but same password for the default GNOME keyring, so that all desktop users can use the restored Cline Plugin configuration, including the API keys in the keyring

## Planned

- [ ] Rename the folder `configuration/home/my_desktop_user` to `.../backup_user`

## Backlog of ideas

- [ ] Reconsider backup concept. At the moment, the first desktop user is backed up, the others are ignored.
- [ ] Is it possible to reduce code duplication for determining the value of the `desktop_user_names` and `all_users`? (Important concept: Separate user names from passwords so that we can log them without accidentially logging the passwords)
