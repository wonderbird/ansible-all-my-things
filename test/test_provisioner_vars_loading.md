# Test Specification: Provisioner Variables Loading

## Purpose

Verify that provisioner playbooks work correctly with automatic group_vars loading after removing explicit `vars_files` sections.

## Background

This test validates the refactoring milestone where explicit `vars_files` sections were removed from all provisioner playbooks in favor of Ansible's automatic loading of `inventories/group_vars/all/` files.

## Test Steps

### Step 1: Basic Inventory Test

**Command:**

```bash
ansible-inventory --graph
```

**Expected Result:**

- No errors
- Shows inventory structure with groups
- May show warning about empty hosts list (this is normal for dynamic inventory)

### Step 2: Group Variables Loading Test

**Command:**

```bash
ansible-playbook --vault-password-file ansible-vault-password.txt ./test/test-group-vars-loading.yml 
```

**Expected Result:**

- All assertions pass
- Success messages for vars.yml and vault.yml loading
- Debug output showing variable values
- May show warning about empty hosts list (this is normal)

### Step 3: Provisioner Variables Access Test (Optional)

**Command:**

```bash
ansible-playbook --vault-password-file ansible-vault-password.txt ./provision-aws-linux.yml --check
```

**Expected Result:**

- **FAILURE IS EXPECTED** in check mode due to external API dependencies
- Error should be about undefined variable from external task (IP lookup)
- Error should NOT be about missing vault variables or group_vars variables

## Success Criteria

✅ **Milestone Complete** if:

- Step 1 passes without errors
- Step 2 passes all assertions
- Step 3 fails only due to external dependencies, not missing variables

❌ **Milestone Incomplete** if:

- Steps 1 or 2 show missing variable errors
- Step 3 fails due to undefined vault variables (e.g., `my_ssh_key_name`, `aws_default_region`)

## Notes

- Check mode (`--check`) cannot simulate external API calls (IP lookup), so Step 3 failure is expected
- The test validates that provisioners can access all required variables from automatic group_vars loading
- Actual provisioner runs (without `--check`) should work correctly after passing these tests