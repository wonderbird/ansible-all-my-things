# Phase 1 Data Model: Configure Basic Profile for Tart VMs

This feature introduces no application data model. The "Key Entities" from
[spec.md](spec.md) are configuration entities — Ansible inventory groups,
group variables, and role names. This document maps each entity to where it
is defined and how the entities relate.

## Entities

### Default Bootstrap Account

| Attribute | Value |
|-----------|-------|
| Definition | `admin_user_on_fresh_system` group variable |
| Defined in | `inventories/group_vars/tart/vars.yml` (NEW, this feature) |
| Value for `tart` group | `"admin"` |
| Consumed by | `playbooks/setup-users.yml` (sets `ansible_user: "{{ admin_user_on_fresh_system }}"` for its initial connection) |
| Precedent | `inventories/group_vars/vagrant_tart/vars.yml` defines the same key with the same value for the analogous `vagrant_tart` group; `windows`, `hcloud_linux`, `vagrant_docker`, `aws_ec2_linux` group_vars define the same key with platform-appropriate values |
| Lifecycle | Exists on the VM before this playbook runs (created by the cloud-image / `create-vm.yml`); this feature does not create or modify the account itself — only configures the variable used to connect to it |

### Admin User (`my_ansible_user`)

| Attribute | Value |
|-----------|-------|
| Definition | `my_ansible_user` group variable |
| Defined in | `inventories/group_vars/all/vars.yml` (existing, unmodified — value `"gandalf"`) |
| Relationships | Becomes a member of the `sudo` group (FR-003) and gains passwordless sudo (FR-004) via `playbooks/setup-users.yml`'s `console_users` list; receives an SSH public key (FR-005) from `my_ssh_public_key`; used as `ansible_user` for all subsequent plays after `setup-users.yml` (e.g. `configure-basic-profile-linux-roles.yml` sets `ansible_user: "{{ my_ansible_user }}"`) |
| Created by | `playbooks/setup-users.yml` (existing, unmodified) — this feature does not change how the admin user is created |

### Desktop User (`desktop_users`)

| Attribute | Value |
|-----------|-------|
| Definition | `desktop_users` list of `{name, password, ...}` objects |
| Defined in | `inventories/group_vars/all/vars.yml` (existing, unmodified — currently one entry, `galadriel`) |
| Relationships | Each entry becomes a member of the `sudo` group and receives an SSH public key (FR-003, FR-005) via `setup-users.yml`'s `all_users = console_users + desktop_users`; each entry's `.name` is extracted into `desktop_user_names` (a list of strings) by both `playbooks/setup-nodejs.yml` and `configure-basic-profile-linux-roles.yml` via `desktop_users \| map(attribute='name') \| list` |
| Receives | Node Version Manager, Node.js LTS (default version), and global npm tools `eslint`, `markdownlint-cli`, `prettier`, `typescript` (FR-010–FR-012) via `playbooks/setup-nodejs.yml` (existing, unmodified) |

### Development Tool Role

| Attribute | Value |
|-----------|-------|
| Definition | One of five existing Ansible roles under `roles/` |
| Members | `podman` (FR-013), `ruby` (FR-014), `python` (FR-015), `dolt_sql_server` (FR-016), `claude_code` (FR-017) |
| Applied by | `configure-basic-profile-linux-roles.yml` (NEW, this feature) — `roles:` list, `hosts: tart`, `become: true` |
| Test coverage | Each role already has a passing `molecule/default/` scenario under `roles/<role>/molecule/default/` (Constitution Principle II — already satisfied, no new Molecule work) |
| Excluded by FR-018 | `tmux`, `google_chrome` (both present in `configure-linux-roles.yml`'s role list but intentionally omitted here as desktop-only/no-desktop-environment tooling) |

## Relationships Diagram (informal)

```text
inventories/group_vars/tart/vars.yml          (NEW)
  └─ admin_user_on_fresh_system: "admin"  ──┐
                                             │ consumed as initial ansible_user by
inventories/group_vars/all/vars.yml         │
  ├─ my_ansible_user: "gandalf"        <────┘  playbooks/setup-users.yml
  ├─ my_ansible_user_password               (existing, unmodified)
  ├─ my_ssh_public_key                            │
  └─ desktop_users: [ {name, password, ...} ]     │
                                                   ▼
                              creates/configures Admin User + Desktop Users
                              (sudo group, passwordless sudo, SSH keys,
                               .bashrc loading, password auth disabled)
                                                   │
                                                   ▼
                              playbooks/setup-basics.yml (existing, unmodified)
                              → apt update/upgrade, Europe/Berlin timezone
                                                   │
                                                   ▼
                              playbooks/setup-nodejs.yml (existing, unmodified)
                              → NVM + Node LTS + global npm tools
                              for each name in desktop_user_names
                                                   │
                                                   ▼
                              configure-basic-profile-linux-roles.yml (NEW)
                              hosts: tart
                              roles: podman, ruby, python,
                                     dolt_sql_server, claude_code
                                                   │
                                                   ▼
                              playbooks/reboot-if-required.yml (existing, unmodified)
                              → reboot + wait if /var/run/reboot-required exists
```

All five layers above are chained by `configure-basic-profile.yml` (NEW) via
`import_playbook`, in the order shown.
