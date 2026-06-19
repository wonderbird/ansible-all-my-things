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
- `Dockerfile` — canonical base; add role-specific packages only when needed
- `prepare.yml` — omit entirely when nothing remains after removing bootstrap tasks

## Required scenario files

| File | Purpose |
| --- | --- |
| `Dockerfile` | Pre-bake python3+sudo (and any role-specific packages) into the test image |
| `molecule.yml` | Driver, platform, provisioner, verifier, test sequence |
| `prepare.yml` | Role-specific container setup after image build (omit if nothing remains) |
| `converge.yml` | Apply the role under test |
| `verify.yml` | Assert observable outcomes |

## Dockerfile

Pre-bake python3 and sudo into the container image. This avoids rootless podman
killing the container during Ansible's pre-Python file-copy phase.

**Do NOT add `&& rm -rf /var/lib/apt/lists/*`** — the apt package index must
remain available so roles that use `update_cache: false` (or omit `update_cache`)
can install packages during converge without a fresh `apt-get update`.

Minimal Dockerfile (sufficient for most roles):

```dockerfile
FROM docker.io/library/ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends \
       python3 sudo python3-apt
```

**`python3-apt` is required** whenever the role uses `ansible.builtin.apt`
with `update_cache: false` (or no `update_cache` key). Without it the apt
module fails to auto-install its Python binding.

**`ca-certificates` is required** whenever the role downloads files from HTTPS
URLs via `ansible.builtin.get_url`. Add it to the Dockerfile for those roles.

Add other role-specific packages to the same `apt-get install` line when
required at container-build time (e.g. `git fontconfig unzip` for roles that
extract archives or manage fonts). Do NOT add packages that are installed by
the role itself.

## molecule.yml

```yaml
dependency:
  name: galaxy
driver:
  name: podman
platforms:
  - name: instance
    image: molecule_<rolename>_instance
    pre_build_image: false
    dockerfile: Dockerfile
provisioner:
  name: ansible
  env:
    ANSIBLE_ROLES_PATH: "${MOLECULE_PROJECT_DIRECTORY}/../"
    ANSIBLE_PODMAN_MOUNT_DETECTION: "false"
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

Replace `<rolename>` with the exact role directory name (e.g. `dolt_sql_server`,
`java`, `ruby`). The image name follows the pattern `molecule_<rolename>_instance`.

## prepare.yml

With python3 and sudo pre-baked in the Dockerfile, `prepare.yml` is only needed
for role-specific setup (e.g. creating a test user). If nothing remains after
removing the bootstrap tasks, **delete the file** (Principle XIII — no empty
artefacts).

When `prepare.yml` exists, it contains only role-specific tasks:

```yaml
- name: Prepare container
  hosts: all
  gather_facts: false
  become: true
  tasks:
    - name: Create testuser
      ansible.builtin.user:
        name: testuser
        state: present
        create_home: true
```

**Do NOT add raw apt bootstrap tasks to prepare.yml.** Those belong in the
Dockerfile.

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

## Concurrency

When multiple agent sessions might run `molecule test` concurrently on the
same host, all `molecule/*/molecule.yml` files hardcode the podman container
name `instance` — a single shared resource even across separate git worktrees.
Concurrent runs can collide. Use the wrapper script:

```shell
cd roles/<role-name>
../../scripts/with-molecule-lock.sh molecule test
```

The wrapper serializes molecule test runs host-wide, ensuring the shared
`instance` container is only in use by one session at a time.

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
