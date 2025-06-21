# Ideas for improvements

- [ ] Rename the folder `configuration/home/my_desktop_user` to `.../backup_user`
- [ ] Reconsider backup concept. At the moment, the first desktop user is backed up, the others are ignored.
- [ ] Is it possible to reduce code duplication for determining the value of the `desktop_user_names` and `all_users`? (Important concept: Separate user names from passwords so that we can log them without accidentially logging the passwords)
