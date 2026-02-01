# Important concepts

<!-- Execute the following command to update the table of contents: -->
<!-- doctoc --maxlevel 2 ./docs/important-concepts.md -->

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Important concepts](#important-concepts)
  - [SSH Key Compatibility](#ssh-key-compatibility)
    - [AWS EC2 Key Requirements](#aws-ec2-key-requirements)
    - [Key Type Recommendations](#key-type-recommendations)
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

The ansible vault password is expected in the environment variable `ANSIBLE_VAULT_PASSWORD`. You can use [direnv](https://direnv.net) and a `.envrc` file to this up. The ansible configuration file [ansible.cfg](../ansible.cfg) will automatically use it by calling the script [echo-vault-password-environment-variable.sh](../scripts/echo-vault-password-environment-variable.sh). This way, the Vagrant provisioners in the [/test](../test/) folders can access it.

The files `/inventories/group_vars/all/vault.yml` and `.envrc` are excluded from git via [/.gitignore](../.gitignore), so that secrets are not accidentally committed to the repository.

Execute the following commands in the repository root to set up the secrets:

```shell
# Create a new ansible vault password file
echo -n "New ansible vault password: " \
  && read -s ANSIBLE_VAULT_PASSWORD \
  && echo "export ANSIBLE_VAULT_PASSWORD=$ANSIBLE_VAULT_PASSWORD" >> .envrc

# Load the environment
. .envrc

# Create a new vault.yml file from the template
cp -v ./inventories/group_vars/all/vault-template.yml ./inventories/group_vars/all/vault.yml \
  && ansible-vault encrypt ./inventories/group_vars/all/vault.yml

# Read public key of .pem file
ssh-keygen -y -f ~/.ssh/YOUR_KEY_FILE.pem

# Replace the placeholders with your secrets
ansible-vault edit ./inventories/group_vars/all/vault.yml
```

## Admin user on fresh system differs per provider

Different providers set up machines with different administrator users. Check the provider and system specific group variables in the [/inventories/group_vars/](../inventories/group_vars/) directory. For example for a Linux instance in Hetzner Cloud: [/inventories/group_vars/hcloud_linux/vars.yml](../inventories/group_vars/hcloud_linux/vars.yml).

The inventory files for each provider and platform must specify the variable `admin_user_on_fresh_system`. It contains the name of the admin user to be used by ansible for the initial setup of the system.

## Same ansible user is set up for each provider

The `root` user shall only be used for a very short time. Thus, the [/playbooks/setup-users.yml](../playbooks/setup-users.yml) playbook is run as early as possible to create a new user with sudo privileges.

This `my_ansible_user` is configured in [/inventories/group_vars/all/vars.yml](../inventories/group_vars/all/vars.yml).

## Desktop user accounts are used to log in

[/inventories/group_vars/all/vars.yml](../inventories/group_vars/all/vars.yml) defines user names and passwords for the `desktop_users`. These accounts are intended for logging into the (desktop) environment.

The corresponding template file shows the structure of the secrets file: [/inventories/group_vars/all/vault-template.yml](../inventories/group_vars/all/vault-template.yml).
