# Problem: Undefined group_vars/all/vars.yml in test/docker Configuration

## Problem Description

When trying to provision the test/docker configuration using `cd test/docker && vagrant up`, the system encountered an error: **"my_ansible_user variable is undefined"**.

The same problem occurs for the test/tart configuration.

This occurred because:

1. The Vagrantfile was calling `configure-linux.yml` directly
2. The playbooks in `configure-linux.yml` expect variables from `inventories/group_vars/all/vars.yml` to be automatically loaded
3. Vagrant's default inventory generation doesn't include the main project's group_vars structure
4. The `my_ansible_user` variable is defined in `inventories/group_vars/all/vars.yml` but wasn't being loaded

## Test to Reproduce the Problem

### Prerequisite: Enable Logging of Secrets

Enable logging of the "Setup accounts" task in the playbook [/playbooks/setup-users.yml](../../playbooks/setup-users.yml)

### Test Provisioning a VM

Execute the following test:

```shell
cd test/docker
vagrant up
```

Expected: Success

Actual: Fail with final message

```json
FAILED! => {"msg": "{{ console_users + desktop_users }}: [{'name': '{{ my_ansible_user }}', 'password': \"{{ my_ansible_user_password | default('my_ansible_user_password must be configured in inventory/group_vars/all/vault.yml') }}\"}]: 'my_ansible_user' is undefined"}
```

The same test results in a failure when executing it from the `test/tart` directory.

## Analysis

### Current Architecture

- **Main Project**: Uses dynamic inventory plugins (AWS EC2, Hetzner Cloud) with automatic group_vars loading
- **Test Environment**: Uses Vagrant with Docker provider, creating its own inventory
- **Variable Loading**: Group_vars are automatically loaded when using the main inventory, but not with Vagrant's generated inventory

### Root Cause

Vagrant creates its own inventory file (`.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory`) and the local `ansible.cfg` points to it, but this inventory doesn't include the group_vars from the main project structure.

## Test to Reproduce the Root Cause

Execute the following test:

```shell
cd test/docker
ansible-playbook ../test_group_vars_loading.yml --vault-password-file ../../ansible-vault-password.txt
```

Expected: Success

Actual: Fail with final message `Variables from group_vars/all/vars.yml are not automatically loaded`

The same test results in a failure when executing it from the `test/tart` directory.

## Solution

See commit `12dc4612` with headline **fix: undefined group_vars/all/vars.yml in test/docker configuration**.

## References

- [Vagrant: Ansible Provisioner](https://developer.hashicorp.com/vagrant/docs/provisioning/ansible)
- [Vagrant: Ansible and Vagrant Introduction](https://developer.hashicorp.com/vagrant/docs/provisioning/ansible_intro)
- [Vagrant: Common Ansible Options](https://developer.hashicorp.com/vagrant/docs/provisioning/ansible_common)
- [Ansible: Using inventory directories and multiple inventory sources](https://docs.ansible.com/ansible/latest/inventory_guide/intro_dynamic_inventory.html#using-inventory-directories-and-multiple-inventory-sources)
- [Ansible: Passing multiple inventory sources](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#using-multiple-inventory-sources)
- [Ansible: Ansible Configuration Settings](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#ansible-configuration-settings-locations)
