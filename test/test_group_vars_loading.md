# Test: Group Vars Loading

## Purpose

Make sure Ansible playbooks can automatically use both regular and encrypted (vault) variables from inventories/group_vars/all/—without needing to list them in vars_files. This test checks that all needed variables are available when running playbooks on localhost, just like in real provisioning.

## Manual Test Instructions

### Step 1: Run the Test Playbook

Execute the following command from the project root:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./test/test_group_vars_loading.yml
```

### Step 2: Review the Output

- The playbook will run several assertions and print debug output.
- **Expected output:**
  - Success messages for loading variables from `vars.yml` and `vault.yml`
  - Success message for correct vault variable referencing
  - Debug output showing the values of key variables (e.g., `my_ansible_user`, `my_ssh_key_name`)
  - A final message confirming that all group_vars/all/ files are loaded

**Example output:**

```text
TASK [Verify that vars.yml variables are loaded automatically] ***
ok: [localhost] => {
    "msg": "✅ Variables from group_vars/all/vars.yml loaded successfully"
}

TASK [Verify that vault.yml variables are loaded automatically] ***
ok: [localhost] => {
    "msg": "✅ Variables from group_vars/all/vault.yml loaded successfully"
}

TASK [Verify that vault variables are properly referenced] ***
ok: [localhost] => {
    "msg": "✅ Vault variable references working correctly"
}

TASK [Display test results] ***
ok: [localhost] => {
    "msg": "🎯 Test Results:\n- my_ansible_user: ...\n- SSH key name: ...\n- Password reference works: Yes\n\n✅ All group_vars/all/ files are automatically loaded for localhost plays!"
}
```

### Step 3: Success Criteria

- All assertions pass (no failed tasks)
- Output matches the example above (variable values may differ)
- No errors about missing variables or missing vault files

### Step 4: Troubleshooting

- If you see errors about missing variables, check that your `inventories/group_vars/all/vars.yml` and `vault.yml` files exist and are correctly populated.
- Ensure you provide the correct vault password file with `--vault-password-file`.

## Notes

- This test does not require any cloud provider credentials or external dependencies.
- It is safe to run on any system with Ansible installed and the correct group_vars files in place.
