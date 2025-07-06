# Ideas for improvements

- [ ] Rename the folder `configuration/home/my_desktop_user` to `.../backup_user`
- [ ] Reconsider backup concept. At the moment, the first desktop user is backed up, the others are ignored.
- [ ] Is it possible to reduce code duplication for determining the value of the `desktop_user_names` and `all_users`? (Important concept: Separate user names from passwords so that we can log them without accidentially logging the passwords)
- [ ] Updates auf der AWS Windows Instanz installieren und System Reboot durchführen, falls nötig
- [ ] Ermögliche es, Instanzen bei Bedarf hinzuzufügen - die Anzahl der Instanzen soll irgendwie einfach zu ändern sein.
  - [ ] Ist es sinnvoll, die Instanzen anhand Ihrer festen Namen unterscheidbar zu machen? Benenne lorien-windows um in moria; Benenne lorien (aws, linux) um in ...
- [ ] The shell scripts in the scripts folder should be python scripts, so that they are more compatible with other platforms and so that they can be integrated into a real application later
- [ ] Vereinfache "admin_user_on_fresh_system" Konzept - Der admin_user_on_fresh_system kann im Inventory in der jeweiligen vars.yml definiert werden. Will ich den gandalf beibehalten?
