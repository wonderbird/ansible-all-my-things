# System Patterns: Java Role

## Role Structure

```text
roles/java/
├── defaults/main.yml    # java_sdkman_identifier: "21.0.7-tem"
├── meta/main.yml        # galaxy_info
├── tasks/main.yml       # Three-task per-user sequence
└── DESIGN.md            # Non-obvious design decisions
```

No `handlers/`, `templates/`, `files/`, or `vars/` directories — the role
is pure-task with one default variable.

## Task Sequence (per user in `desktop_user_names`)

```text
Task 1: Download sdkman installer (runs as root — no become_user)
  module: ansible.builtin.get_url
  url:    https://get.sdkman.io/download
  dest:   /tmp/sdkman-install.sh
  guard:  force: false (skips if dest already exists)

Task 2: Run sdkman installer per user
  module:      ansible.builtin.shell
  cmd:         bash /tmp/sdkman-install.sh
  creates:     /home/{{ item }}/.sdkman/bin/sdkman-init.sh
  become_user: {{ item }}
  loop:        desktop_user_names
  env:         SDKMAN_DIR: /home/{{ item }}/.sdkman

Task 3: Install Temurin JDK per user
  module:      ansible.builtin.shell
  cmd:         bash -c 'source /home/{{ item }}/.sdkman/bin/sdkman-init.sh
               && sdk install java {{ java_sdkman_identifier }}'
  creates:     /home/{{ item }}/.sdkman/candidates/java/
               {{ java_sdkman_identifier }}/bin/java
  become_user: {{ item }}
  loop:        desktop_user_names
```

## Key Design Decisions

### Version-Specific Idempotency Guard

The `creates:` path for Task 3 uses the version-specific path
`/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}/bin/java`,
NOT the `current/` symlink. This ensures that bumping `java_sdkman_identifier`
causes the new version to be installed (the old `creates:` guard is still
satisfied; only the new version's task runs).

### Inline sdkman Sourcing

Task 3 uses `bash -c 'source ... && sdk install ...'` because Ansible
`shell` tasks spawn a non-interactive shell that does not source `.bashrc`.
The `sdk` command is a shell function, not a binary, so sourcing
`sdkman-init.sh` inline is the only reliable approach.

### No Task-Level `become`

`configure-linux-roles.yml` sets `become: true` at play level. The role
inherits it. Per-user tasks use `become_user: "{{ item }}"` only (no
redundant `become: true` at task level). This matches the `android_studio`
and `flutter` reference roles.

### sdkman Handles PATH Automatically

The sdkman installer appends `source ~/.sdkman/bin/sdkman-init.sh` to
`~/.bashrc` and `~/.profile`. No `blockinfile` task is needed — unlike
the `flutter` role, which must modify PATH explicitly.

### No Architecture Branching

sdkman and Temurin both publish ARM64 artifacts and detect the host
architecture at runtime. The role needs no `when: ansible_architecture`
guards and carries no `not-supported-on-vagrant-arm64` tag.

## Playbook Integration

The `java` role is registered in `configure-linux-roles.yml` line 22
(after `flutter`) with no special tags — it runs on all architectures.

## Conventions (from Constitution)

- All YAML files begin with `#SPDX-License-Identifier: MIT-0`.
- All module references use FQCN (`ansible.builtin.*`).
- Commit prefix: `feat:` for implementation, `docs:` for documentation.
