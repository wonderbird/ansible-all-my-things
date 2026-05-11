---
name: molecule-testing
description: >
  Pull in information about the molecule testing setup for Ansible roles.
  Use when implementing or modifying an Ansible role to set up or maintain
  its Molecule test scenario.
---
# Molecule testing for Ansible roles

See constitution Principle II for applicability. Roles requiring a full VM
(desktop, display managers, hardware drivers) use `CONTRIBUTING.md` instead.

## Current Goal

$ARGUMENTS

## Ask when goal unclear

Ask me, if "Current Goal" section empty and context does not clearly identify goal.

## meta/main.yml — required fields

```yaml
galaxy_info:
  namespace: wonderbird
  role_name: <role-name>
```

## Creating a new role

**Always** use the scaffold script — never create role directories or files manually:

```shell
bash scripts/new-role.sh <role-name>
```

The script copies `role-template/` to `roles/<role-name>/` and substitutes the
`ROLE_NAME` placeholder throughout all files.

**After scaffolding, customize:**

- `meta/main.yml` — set `role_name` to the actual role name
- `converge.yml` — add required vars and update the role reference
- `verify.yml` — add assertions for observable outcomes

**Do NOT modify per-role:**

- `molecule.yml` — canonical; change only via this rule or `role-template/`
- `prepare.yml` — canonical; change only via this rule or `role-template/`

## Required scenario files

| File | Purpose |
| --- | --- |
| `molecule.yml` | Driver, platform, provisioner, verifier, test sequence |
| `prepare.yml` | Bootstrap the container before converge |
| `converge.yml` | Apply the role under test |
| `verify.yml` | Assert observable outcomes |

## molecule.yml

```yaml
dependency:
  name: galaxy
driver:
  name: podman
platforms:
  - name: instance
    image: docker.io/library/ubuntu:24.04
    pre_build_image: true
provisioner:
  name: ansible
  env:
    ANSIBLE_ROLES_PATH: "${MOLECULE_PROJECT_DIRECTORY}/../"
verifier:
  name: ansible
scenario:
  test_sequence:
    - destroy
    - syntax
    - create
    - prepare
    - converge
    - idempotence
    - verify
    - destroy
```

## prepare.yml

Bootstrap rules:

- Two **separate** `raw` tasks — do NOT chain with `&&` in a folded scalar
- Both MUST have `become: false` (sudo not yet installed)
- Further tasks after bootstrap may inherit play-level `become: true`

```yaml
- name: Prepare container
  hosts: all
  gather_facts: false
  become: true
  tasks:
    - name: Update apt cache
      ansible.builtin.raw: apt-get update
      become: false
      changed_when: true

    - name: Install python3 and sudo
      ansible.builtin.raw: apt-get install -y -qq python3 sudo
      become: false
      changed_when: true
```

## converge.yml

```yaml
- name: Converge
  hosts: all
  become: true
  vars:
    my_var: value
  roles:
    - role: <role-name>
```

## verify.yml

Use `ansible_facts['env']` — NOT `ansible_env` (deprecated, removed in 2.24).

```yaml
- name: Verify
  hosts: all
  become: true
  tasks:
    - name: Check outcome
      ansible.builtin.command: <command>
      register: result
      changed_when: false

    - name: Assert outcome
      ansible.builtin.assert:
        that:
          - "'expected' in result.stdout"
```

**Do not verify `.bashrc` exports via `ansible_facts['env']` or `ansible_env`.**
Ubuntu's default `.bashrc` contains `case $- in *i*) ;; *) return;; esac` —
it exits immediately in non-interactive shells. All Ansible connections are
non-interactive, so `.bashrc` is never sourced and environment variables
exported there are never visible to the module.

To assert that a `blockinfile`/`lineinfile` task correctly wrote an export
to `.bashrc`, grep the file directly:

```yaml
- name: Check VAR is configured in user's .bashrc
  ansible.builtin.shell: grep -q 'VAR=expected_value' /home/user/.bashrc
  changed_when: false
  failed_when: false
  register: bashrc_check

- name: Assert VAR is configured in .bashrc
  ansible.builtin.assert:
    that:
      - bashrc_check.rc == 0
    fail_msg: "VAR not found in user's .bashrc"
    success_msg: "VAR is configured in user's .bashrc"
```

## Idempotence pitfalls

- **Temporary files**: do not delete a downloaded file unconditionally; use a
  `when:` guard or omit the cleanup task
- **shell/command**: always add `creates:` or `changed_when:`
- **blockinfile `append_newline`/`prepend_newline`**: never use these
  parameters — they cause the task to report `changed` on every run

## Running the tests

```shell
cd roles/<role-name>
molecule test
```

All phases MUST pass before committing. The two podman schema warnings are
expected and acceptable.

## Troubleshooting: molecule not found

If `molecule` is not on PATH, the project `.venv` is missing or stale.
Set it up before running any molecule command:

```shell
# From project root
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy install -r requirements.yml
```

Then run molecule from inside the activated venv:

```shell
cd roles/<role-name>
molecule test
```

The `.venv/` directory is git-ignored. Re-create it whenever it is absent.
