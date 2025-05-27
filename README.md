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

### Secrets are encrypted with Ansible Vault

The playbooks create user accounts and register SSH keys for passwordless login.

The required secrets are stored in the
[./playbooks/vars-secrets.yml](./playbooks/vars-secrets.yml) file, which is
encrypted with Ansible Vault.

This repository contains an initial version, which you should replace with
your own secrets after checking out the repository.

The file is excluded from git via [.gitignore](./.gitignore), so that your
actual secrets are not accidentally committed to the repository.

The password for the file in this repository is stored in
[./ansible-vault-password.txt](./ansible-vault-password.txt), so that
the vagrant provisioners in [./test/](./test/) can access it.

You can decrypt the file and show it to the console with the following command:

```shell
ansible-vault view ./playbooks/vars-secrets.yml
```

After checking out this repository you should change the vault password and the
stored secrets:

```shell
# Change the vault password
echo -n "New ansible vault password: " \
  && read -s ANSIBLE_VAULT_PASSWORD \
  && echo "$ANSIBLE_VAULT_PASSWORD" > ./new-ansible-vault-password.txt \
  && ansible-vault rekey --vault-password-file ansible-vault-password.txt --new-vault-password-file new-ansible-vault-password.txt ./playbooks/vars-secrets.yml \
  && cp ./new-ansible-vault-password.txt ./ansible-vault-password.txt \
  && rm ./new-ansible-vault-password.txt

# Change the secrets
ansible-vault edit --vault-password-file ansible-vault-password.txt ./playbooks/vars-secrets.yml
```

### Admin user on fresh system differs per provider

Different providers set up machines with different administrator users:

- Hetzner Cloud: `root`, see [./inventories/hcloud/group_vars/dev/vars.yml](./inventories/hcloud/group_vars/dev/vars.yml),
- Vagrant with Tart: `admin`, see [./test/tart/Vagrantfile](./test/tart/Vagrantfile),
- Vagrant with Docker: `vagrant`, see [./test/docker/Vagrantfile](./test/docker/Vagrantfile) and [./test/docker/Dockerfile](./test/docker/Dockerfile),
- Vagrant with VirtualBox: `vagrant`.

The inventory files for each provider must specify the variable
`admin_user_on_fresh_system`. It contains the name of the admin user
to be used by ansible for the initial setup of the system.

### Same ansible user is set up for each provider

The `root` user shall only be used for a very short time. Thus, the
[./playbooks/setup-users.yml](./playbooks/setup-users.yml) playbook is run
as early as possible to create a new user with sudo privileges.

This `ansible_user` is configured in
[./playbooks/vars-usernames.yml](./playbooks/vars-usernames.yml) and in
the inventory files for the non-test systems.

### Desktop user is used to log in

The desktop user is the user that is used to log in to the (desktop)
environment.

The user name is set by the variable `my_desktop_user` in
[./playbooks/vars-usernames.yml](./playbooks/vars-usernames.yml).

## Create a developer VM with Hetzner

### Prerequisites

You need a cloud project with [Hetzner](https://www.hetzner.com/).

Your SSH key must be registered in the cloud project, so that new servers can
use it. This will allow `root` login via SSH.

Now configure the `hcloud_` properties for **server size** and the
**SSH key ID** in [./provisioners/hcloud.yml](./provisioners/hcloud.yml).

Next, publish your API token to the HCLOUD_TOKEN environment variable, which
is used by default by the
[hetzner.hcloud ansible modules](https://docs.ansible.com/ansible/latest/collections/hetzner/hcloud/).

```shell
echo -n "hcloud API token: "; read -s HCLOUD_TOKEN; export HCLOUD_TOKEN
```

Finally, follow the instructions in section [Important concepts](#important-concepts)
to update your secrets in
[./ansible-vault-password.txt](./ansible-vault-password.txt) and in
[./playbooks/vars-secrets.yml](./playbooks/vars-secrets.yml).

### Create the VM

Create the server using the following command:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./provision.yml
```

You will be asked to add the SSH key of the new server to your local
`~/.ssh/known_hosts` file.

After that, the setup will take some 10 - 15 minutes.

To verify the setup, execute the `mob moo` command on the server:

```shell
ansible dev -m shell -a 'whoami'

# Source .bash_profile to load the environment variables
ansible dev -m shell -a '. $HOME/.bash_profile; mob moo'
```

>[!IMPORTANT]
> Add additional SSH keys to the `authorized_keys` files on the server.

## Log in to the desktop user

The username of the desktop user is set configured in
[./playbooks/vars-usernames.yml](./playbooks/vars-usernames.yml). Here, we
assume it is `galadriel`.

To log in to the desktop user, use the following command:

```shell
# Receive the IP address of the server from the Hetzner API
export IPV4_ADDRESS=$(hcloud server list -o json | jq '.[0].public_net.ipv4.ip' | tr -d '"'); echo "IPv4 address: \"$IPV4_ADDRESS\""

# Connect to the server via SSH, forwarding the RDP port
ssh -L 3389:localhost:3389 galadriel@$IPV4_ADDRESS
```

Now you can open an RDP client like Remmina, Windows App or Remote Desktop to
connect to the server at `localhost` with user `galadriel`.

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
