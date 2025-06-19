# Important concepts

## Secrets are encrypted with Ansible Vault

The playbooks create user accounts and register SSH keys for passwordless login.

The required secrets are expected in `/playbooks/vars-secrets.yml`. This file
shall be encrypted with ansible vault.

The ansible vault password is expected in `/ansible-vault-password.txt`. This
way, the Vagrant provisioners in the [/test](../test/) folders can access it.

Both files are excluded from git via [/.gitignore](../.gitignore), so that
secrets are not accidentally committed to the repository.

Execute the following commands in the repository root to set up the secrets:

```shell
# Create a new ansible vault password file
echo -n "New ansible vault password: " \
  && read -s ANSIBLE_VAULT_PASSWORD \
  && echo "$ANSIBLE_VAULT_PASSWORD" > ./ansible-vault-password.txt

# Create a new vars-secrets.yml file from the template
cp -v ./playbooks/vars-secrets-template.yml ./playbooks/vars-secrets.yml \
  && ansible-vault encrypt --vault-password-file ./ansible-vault-password.txt ./playbooks/vars-secrets.yml

# Replace the placeholders with your secrets
ansible-vault edit --vault-password-file ./ansible-vault-password.txt ./playbooks/vars-secrets.yml
```

## Admin user on fresh system differs per provider

Different providers set up machines with different administrator users:

- Hetzner Cloud: `root`, see [/inventories/hcloud/group_vars/dev/vars.yml](../inventories/hcloud/group_vars/dev/vars.yml),
- Vagrant with Tart: `admin`, see [/test/tart/Vagrantfile](../test/tart/Vagrantfile),
- Vagrant with Docker: `vagrant`, see [/test/docker/Vagrantfile](../test/docker/Vagrantfile) and [/test/docker/Dockerfile](../test/docker/Dockerfile),
- Vagrant with VirtualBox: `vagrant`.

The inventory files for each provider must specify the variable
`admin_user_on_fresh_system`. It contains the name of the admin user
to be used by ansible for the initial setup of the system.

## Same ansible user is set up for each provider

The `root` user shall only be used for a very short time. Thus, the
[/playbooks/setup-users.yml](../playbooks/setup-users.yml) playbook is run
as early as possible to create a new user with sudo privileges.

This `ansible_user` is configured in
[/playbooks/vars-usernames.yml](../playbooks/vars-usernames.yml) and in
the inventory files for the non-test systems.

## Desktop user accounts are used to log in

[/playbooks/vars-secrets.yml](../playbooks/vars-secrets.yml) defines user names
and passwords for the `desktop_users`. These accounts are intended for logging
into the (desktop) environment.

The corresponding template file shows the structure of the secrets file:
[/playbooks/vars-secrets-template.yml](../playbooks/vars-secrets-template.yml).
