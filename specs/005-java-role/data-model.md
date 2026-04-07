#SPDX-License-Identifier: MIT-0

# Data Model: Java Role (sdkman + Temurin JDK)

**Branch**: `005-java-role` | **Date**: 2026-04-07

This document describes the variables consumed by the role, the file-system
entities created on the managed host, and the idempotency guards that connect
them.

## Variables

### `java_sdkman_identifier` (role default)

| Attribute | Value |
|-----------|-------|
| Source | `roles/java/defaults/main.yml` |
| Type | String |
| Default | `"21.0.7-tem"` |
| Format | sdkman candidate identifier: `<version>-<vendor>` |
| Example values | `21.0.7-tem`, `17.0.11-tem`, `21.0.6-tem` |
| Override scope | Per-host or per-group via `host_vars`/`group_vars` |

**Validation rule**: must be a valid sdkman Java candidate identifier.
An invalid value causes `sdk install java` to exit non-zero, failing the
task with an informative error message.

### `desktop_user_names` (consumed from playbook)

| Attribute | Value |
|-----------|-------|
| Source | `configure-linux-roles.yml` → derived from `desktop_users` group var |
| Type | List of strings |
| Example | `["alice", "bob"]` |
| Edge case | Empty list → zero loop iterations; no tasks execute or fail |

## File-System Entities (per managed host)

### sdkman Installer Script (temporary)

| Attribute | Value |
|-----------|-------|
| Path | `/tmp/sdkman-install.sh` |
| Owner | root (Ansible connection user) |
| Created by | `ansible.builtin.get_url` task |
| Idempotency guard | `force: false` (default) — `get_url` skips the download if the destination file already exists; no `creates:` needed |
| Notes | Not cleaned up; harmless across runs |

### sdkman Installation (per user)

| Attribute | Value |
|-----------|-------|
| Root path | `/home/<user>/.sdkman/` |
| Owner | `<user>` |
| Created by | sdkman installer script |
| Idempotency guard | `creates: /home/<user>/.sdkman/bin/sdkman-init.sh` |
| Notes | Installer also appends `source ~/.sdkman/bin/sdkman-init.sh` to `.bashrc` and `.profile` |

### Temurin JDK Candidate (per user, per version)

| Attribute | Value |
|-----------|-------|
| Path | `/home/<user>/.sdkman/candidates/java/{{ java_sdkman_identifier }}/` |
| Binary | `/home/<user>/.sdkman/candidates/java/{{ java_sdkman_identifier }}/bin/java` |
| Owner | `<user>` |
| Created by | `sdk install java {{ java_sdkman_identifier }}` |
| Idempotency guard | `creates: /home/<user>/.sdkman/candidates/java/{{ java_sdkman_identifier }}/bin/java` |
| Notes | sdkman also creates `current/` symlink pointing to the active version |

## Task Sequence (per user in `desktop_user_names`)

```text
Task 1: Download sdkman installer
  module:       ansible.builtin.get_url
  dest:         /tmp/sdkman-install.sh
  idempotency:  force: false (default) — skips download if dest exists
  become_user:  (not needed — writes to /tmp as root via inherited become)

Task 2: Run sdkman installer
  module:       ansible.builtin.shell
  cmd:          bash /tmp/sdkman-install.sh
  creates:      /home/{{ item }}/.sdkman/bin/sdkman-init.sh
  become_user:  {{ item }}

Task 3: Install Temurin JDK
  module:       ansible.builtin.shell
  cmd:          bash -c 'source /home/{{ item }}/.sdkman/bin/sdkman-init.sh
                && sdk install java {{ java_sdkman_identifier }}'
  creates:      /home/{{ item }}/.sdkman/candidates/java/
                  {{ java_sdkman_identifier }}/bin/java
  become_user:  {{ item }}
```

## Idempotency State Transitions

```text
State: nothing installed
  → Task 1 runs (creates /tmp/sdkman-install.sh)
  → Task 2 runs (creates ~/.sdkman/bin/sdkman-init.sh)
  → Task 3 runs (creates ~/.sdkman/candidates/java/<id>/bin/java)
  Final state: sdkman + Temurin JDK installed

State: sdkman-install.sh already in /tmp, sdkman already installed,
       JDK already installed (same identifier)
  → Task 1 skipped (force: false — dest already exists)
  → Task 2 skipped (creates guard satisfied)
  → Task 3 skipped (creates guard satisfied)
  Final state: unchanged (zero changed tasks)

State: sdkman installed, but different JDK identifier requested
  → Task 1 skipped (force: false — dest already exists)
  → Task 2 skipped
  → Task 3 runs (creates guard for new identifier not satisfied)
  Final state: new JDK version installed alongside previous
```

## Role Files

| File | Purpose |
|------|---------|
| `roles/java/defaults/main.yml` | `java_sdkman_identifier` default |
| `roles/java/meta/main.yml` | `galaxy_info` block |
| `roles/java/tasks/main.yml` | All provisioning tasks |
| `roles/java/DESIGN.md` | Non-obvious design decisions |
