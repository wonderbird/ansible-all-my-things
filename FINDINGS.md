# Review Findings

Scope: commits after `8d104259a9d2f5852dd720ef4d4e049b482a674f`  
All findings must be fixed.

**Fix order:** F-001 before F-004 (F-001 moves the file F-004 edits). F-003 informs F-002 (template must include `-qq`).

| ID | Title |
|----|-------|
| F-001 | Static file in `templates/`, wrong module |
| F-002 | No role scaffold template |
| F-003 | `-qq` missing from rule template |
| F-004 | tmux-battery plugin irrelevant on VMs |

---

## F-001 — Static file in templates/, wrong module

`roles/tmux/templates/tmux.conf.j2` has no Jinja2 expressions. Static content must use `files/` + `copy`, not `templates/` + `template`.

**Fix:**
1. Move `roles/tmux/templates/tmux.conf.j2` → `roles/tmux/files/tmux.conf`
2. In `roles/tmux/tasks/configure.yml`, task "Deploy .tmux.conf for each user":
   - Change module `ansible.builtin.template` → `ansible.builtin.copy`
   - Change `src: tmux.conf.j2` → `src: tmux.conf`

**Verify:** `roles/tmux/templates/` is empty; configure.yml uses `ansible.builtin.copy`.

---

## F-002 — No role scaffold template

5+ roles planned. `molecule/default/molecule.yml` and `prepare.yml` are manually duplicated across roles, causing drift (see F-003).

**Fix:** Create `role-template/` at repo root and `scripts/new-role.sh`:

```
role-template/
  defaults/main.yml          # empty vars file with SPDX header
  files/.gitkeep
  templates/.gitkeep
  tasks/main.yml             # stub with SPDX header
  meta/main.yml              # galaxy_info: namespace: wonderbird, role_name: ROLE_NAME
  molecule/default/
    molecule.yml             # canonical config (see below)
    prepare.yml              # see below — must include -qq (F-003)
    converge.yml             # stub applying role ROLE_NAME
    verify.yml               # stub
```

Canonical `molecule.yml`:
```yaml
#SPDX-License-Identifier: MIT-0
---
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

Canonical `prepare.yml`:
```yaml
#SPDX-License-Identifier: MIT-0
---
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

`scripts/new-role.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
ROLE_NAME="${1:?Usage: new-role.sh <role-name>}"
cp -r role-template "roles/${ROLE_NAME}"
find "roles/${ROLE_NAME}" -type f | xargs sed -i "s/ROLE_NAME/${ROLE_NAME}/g"
echo "Created roles/${ROLE_NAME}"
```

**Verify:** `bash scripts/new-role.sh test-role` creates `roles/test-role/` with all required files; `molecule.yml` matches canonical; `prepare.yml` uses `-y -qq`; delete `roles/test-role/` after verify.

---

## F-003 — -qq missing from rule template in 340-molecule-testing.mdc

`.cursor/rules/340-molecule-testing.mdc` prepare.yml template shows `apt-get install -y python3 sudo`. All existing roles use `-y -qq`. New roles from this rule will omit `-qq`, suppressing apt noise in molecule logs.

**Fix:** In `.cursor/rules/340-molecule-testing.mdc`, in the `prepare.yml` code block, change:
```
ansible.builtin.raw: apt-get install -y python3 sudo
```
to:
```
ansible.builtin.raw: apt-get install -y -qq python3 sudo
```

**Verify:** `grep "apt-get install" .cursor/rules/340-molecule-testing.mdc` shows `-qq` on every match.

---

## F-004 — tmux-battery plugin installed but irrelevant on VMs

Battery status is meaningless on VMs. Remove entirely.

**Fix — apply after F-001 (file has moved):**

`roles/tmux/defaults/main.yml`: remove the `tmux_plugin_battery_repo` line.

`roles/tmux/tasks/install-plugins.yml`: remove the entire "Clone tmux-battery plugin for each user" task block.

`roles/tmux/files/tmux.conf` (was `tmux.conf.j2` before F-001): remove these two lines:
```
run-shell ~/.tmux/plugins/tmux-battery/battery.tmux
```
```
set -g @plugin 'tmux-plugins/tmux-battery'
```

`roles/tmux/molecule/default/verify.yml`: remove both tasks:
- "Check tmux-battery plugin is cloned" (stat task)
- "Assert tmux-battery plugin is cloned" (assert task)

**Verify:** `grep -r battery roles/tmux/` returns no results.
