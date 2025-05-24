# My IT System

Automated setup and updates for my IT system.

- [./configuration/README.md](./configuration/README.md) describes the default configuration
- [./inventories/README.md](./inventories/README.md) describes the inventories
- [./playbooks/README.md](./playbooks/README.md) describes the playbooks
- [./test/README.md](./test/README.md) describes how to test the playbooks

## Notes

The GNOME keyring needs to be unlocked when you launch an application using
it, e.g. Visual Studio Code. The password for the default keyring is the same
as the login password of the desktop user.

## Important concepts

### Admin user on fresh system

Different providers set up machines with different administrator users:

- Hetzner Cloud: `root`, see [./inventories/hcloud/group_vars/dev/vars.yml](./inventories/hcloud/group_vars/dev/vars.yml),
- Vagrant with Tart: `admin`, see [./test/tart/Vagrantfile](./test/tart/Vagrantfile),
- Vagrant with Docker: `vagrant`, see [./test/docker/Vagrantfile](./test/docker/Vagrantfile) and [./test/docker/Dockerfile](./test/docker/Dockerfile),
- Vagrant with VirtualBox: `vagrant`.

The inventory files for each provider must specify the variable
`admin_user_on_fresh_system`. It contains the name of the admin user
to be used by ansible for the initial setup of the system.

### Ansible user

The `root` user shall only be used for a very short time. Thus, the
[./playbooks/setup-users.yml](./playbooks/setup-users.yml) playbook is run
as early as possible to create a new user with sudo privileges.

This `ansible_user` is configured in
[./playbooks/vars-usernames.yml](./playbooks/vars-usernames.yml) and in
the inventory files for the non-test systems.

### Desktop user

The desktop user is the user that is used to log in to the desktop environment.

This `my_desktop_user` is configured in
[./playbooks/vars-usernames.yml](./playbooks/vars-usernames.yml).

## Create a developer VM with Hetzner

### Prerequisites

You need a cloud project with [Hetzner](https://www.hetzner.com/).

Your SSH key must be registered, so that new servers can use it. This will
allow root login via SSH.

### Create the VM

First, configure the `hcloud_` properties for server size and SSH key ID in
[./provisioners/hcloud.yml](./provisioners/hcloud.yml).

Next, publish your API token to the HCLOUD_TOKEN environment variable, which
is used by default by the
[hetzner.hcloud ansible modules](https://docs.ansible.com/ansible/latest/collections/hetzner/hcloud/).

```shell
echo -n "hcloud API token: "; read -s HCLOUD_TOKEN; export HCLOUD_TOKEN
```

Then create the server using the following command:

```shell
ansible-playbook ./provision.yml
```

To verify the setup, execute the `mob moo` command on the server:

```shell
# Source .bash_profile to load the environment variables
ansible dev -m shell -a '. $HOME/.bash_profile; mob moo'
```

## Restore a backup of the desktop user

Restoring the backup is a part of the [./configure.yml](./configure.yml)
playbook.

To restore a backup of the desktop user later manually, use the following
command:

```shell
ansible-playbook ./restore.yml
```

## Backup working directory of desktop user

To backup the working directory of the desktop user, use the following command:

```shell
ansible-playbook ./backup.yml
```

## Delete the VM

To delete the VM, use the following command:

```shell
ansible-playbook ./destroy.yml
```

You can verify that the server is deleted in your [Hetzner console project](https://console.hetzner.cloud/projects/10607445/servers).

## References

[boos2025b] S. Boos, “wonderbird/ansible-for-devops: Exercises from the Book Jeff Geerling: ‘Ansible for DevOps’, 2nd Ed., Leanpub, 2023.” Accessed: May 03, 2025. [Online]. Available: [https://github.com/wonderbird/ansible-for-devops](https://github.com/wonderbird/ansible-for-devops)

[geerling2023] J. Geerling, _Ansible for DevOps_, 2nd ed. Leanpub, 2023. Accessed: Apr. 20, 2025. [Online]. Available: [https://www.ansiblefordevops.com/](https://www.ansiblefordevops.com/)

## Acknowledgements

This project uses code, documentation and ideas generated with the assistance of
large language models.
