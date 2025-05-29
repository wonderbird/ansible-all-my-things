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
