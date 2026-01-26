# Configuration for new virtual machines

This folder contains the default configuration by user in the folder
`./home`.

The [/backup.yml](../backup.yml) playbook will copy backup files to the
home/backup directory for the corresponding user.

You can link the backup directory to some permanent storage:

```shell
ln -s /some/other/location/ansible-all-my-things configuration/home/my_desktop_user/backup
```

Note that the backup files are excluded from git in
[../.gitignore](../.gitignore).
