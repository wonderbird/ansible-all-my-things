# Important concepts

<!-- Execute the following command to update the table of contents: -->
<!-- doctoc --maxlevel 2 ./docs/important-concepts.md -->

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [SSH Key Compatibility](#ssh-key-compatibility)
- [Secrets are encrypted with Ansible Vault](#secrets-are-encrypted-with-ansible-vault)
- [Admin user on fresh system differs per provider](#admin-user-on-fresh-system-differs-per-provider)
- [Same ansible user is set up for each provider](#same-ansible-user-is-set-up-for-each-provider)
- [Desktop user accounts are used to log in](#desktop-user-accounts-are-used-to-log-in)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## SSH Key Compatibility

Different cloud providers and operating systems have varying SSH key type support:

### AWS EC2 Key Requirements

- **Linux AMIs**: Support all key types (RSA, ECDSA, ED25519)
- **Windows AMIs**: Only support RSA (minimum 2048-bit) and ECDSA keys
- **Important**: ED25519 keys are **not supported** for Windows AMIs

### Key Type Recommendations

- **For mixed environments**: Use RSA 2048-bit or higher for maximum compatibility
- **For Linux-only**: ED25519 keys are recommended for security and performance
- **For Windows Server**: Must use RSA or ECDSA keys

## Secrets are encrypted with Ansible Vault

The playbooks create user accounts and register SSH keys for passwordless login.

The required secrets are expected in `/inventories/group_vars/all/vault.yml`. This file shall be encrypted with ansible vault.

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

# Create a new vault.yml file from the template
cp -v ./inventories/group_vars/all/vault-template.yml ./inventories/group_vars/all/vault.yml \
&& ansible-vault encrypt --vault-password-file ./ansible-vault-password.txt ./inventories/group_vars/all/vault.yml

# Replace the placeholders with your secrets
ansible-vault edit --vault-password-file ./ansible-vault-password.txt ./inventories/group_vars/all/vault.yml
```

### Work in progress: Apply idiomatic Ansible for secrets

This is a pending refactoring: **Transition from encrypted playbook/vars-secrets.yml to encrypted inventories/group_vars/all/vars.yml**

When setting up this project, I did not know how variables and secrets are handled in Ansible. Thus, I put encrypted variables into playbooks/vars-secrets.yml and excluded that file from git.

Meanwhile I have learned that idiomatic ansible expects encrypted variables in inventory group variables. Thus, I want to move the playbooks/vars-secrets.yml file to inventories/group_vars/all/vars.yml.

The steps required to achieve this goal are:

- [x] refactor: remove vars.yml (The existing vars.yml can safely be deleted, because there are no variables inside)
- [x] refactor: move vars-secrets.yml to vars.yml (exclude vars.yml from git and move the vars-secrets.yml file to inventories/group_vars/all)
- [x] refactor: playbooks do not need to load vars-secrets.yml explicitly
- [ ] fix: test/tart configuration must consider changed secret handling

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

[/inventories/group_vars/all/vars.yml](../inventories/group_vars/all/vars.yml) defines user names
and passwords for the `desktop_users`. These accounts are intended for logging
into the (desktop) environment.

The corresponding template file shows the structure of the secrets file:
[/playbooks/vars-secrets-template.yml](../playbooks/vars-secrets-template.yml).
