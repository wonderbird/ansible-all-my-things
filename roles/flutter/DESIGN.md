# Flutter Role — Design

This document captures the non-obvious design decisions and technical
constraints of the `flutter` role. For requirements and user stories, see
`specs/004-flutter-role/spec.md`.

## Overview

The role performs three jobs:

1. **apt prerequisites** — installs `clang`, `cmake`, `ninja-build`,
   `pkg-config`, `libgtk-3-dev`, `mesa-utils` system-wide.
2. **Per-user SDK extraction** — downloads and extracts the Flutter SDK
   tarball to `/home/{{ item }}/flutter` for each user in `desktop_user_names`.
3. **PATH configuration** — inserts `export PATH="$HOME/flutter/bin:$PATH"`
   into each user's `~/.bashrc` via `ansible.builtin.blockinfile`.

AMD64 Ubuntu only; ARM64 hosts are skipped via the
`not-supported-on-vagrant-arm64` tag applied in `configure-linux-roles.yml`.

## Version-File Idempotency

**Decision**: Read `/home/{{ item }}/flutter/version` with
`ansible.builtin.slurp`, compare the decoded content to `flutter_version`,
and skip download and extraction when they match.

**Rationale**: The Flutter SDK ships a plain-text `version` file at
`<sdk_root>/version` containing only the version string (e.g. `3.41.6`).
Reading this file is simpler and more reliable than running
`flutter --version`, which requires Dart runtime initialisation (a
first-run compilation step that is slow and may fail in a headless
provisioning environment).

**Implementation sequence per user**:

1. `ansible.builtin.stat` — check whether `/home/{{ item }}/flutter/version`
   exists.
2. `ansible.builtin.slurp` — read the file content when it exists; set
   `flutter_installed_version` via `ansible.builtin.set_fact`.
3. `ansible.builtin.get_url` — download the tarball when
   `flutter_installed_version != flutter_version` (or the version file is
   absent).
4. `ansible.builtin.file` (state=absent) — remove the old SDK directory when
   the version differs, so the unarchive task starts clean.
5. `ansible.builtin.unarchive` — extract the archive when the version differs.

The `sha256` checksum on `get_url` (FR-019) is used for **download integrity
verification**, not for idempotency decisions. The `version` file is the sole
idempotency signal.

**Upgrade trigger**: bump `flutter_version` (and `flutter_sha256`) in
`defaults/main.yml` and re-run the playbook. No other change is required.

## Tag Placement — Role Entry Level Only

**Decision**: Apply `not-supported-on-vagrant-arm64` at the role entry level
in `configure-linux-roles.yml`, not on individual tasks inside the role.

**Rationale**: FR-007 and the `android_studio`/`google_chrome` role pattern.
Applying the tag only at the entry level means:

- The role file is clean and does not repeat tag logic on every task.
- The skip behaviour is visible at a glance in `configure-linux-roles.yml`.
- Adding `apply: tags:` to any future `ansible.builtin.include_role` caller
  is the documented extension point (FR-008; the comment already exists in
  `configure-linux-roles.yml` at the `android_studio` entry).

## `meta/main.yml` — Empty Dependencies

**Decision**: Keep `dependencies: []` in `meta/main.yml`. Document
`java`, `android_studio`, and `google_chrome` as prerequisites in
`README.md` only.

**Rationale**: Meta-level dependencies are invisible to playbook readers,
break tag filtering (the skip tag on `android_studio` would be bypassed if
`flutter` declared it as a meta dependency), and are designed for
redistributed Galaxy roles — not private single-playbook provisioners. This
is consistent with all other roles in this project (Q5 clarification).

## PATH via `blockinfile`

**Decision**: Use `ansible.builtin.blockinfile` to add
`export PATH="$HOME/flutter/bin:$PATH"` to each user's `~/.bashrc`, with
marker `# {mark} ANSIBLE MANAGED BLOCK - Flutter PATH`.

**Rationale**: This is the same pattern as the `claude_code` role
(`roles/claude_code/tasks/main.yml`). `blockinfile` is idempotent: the
unique marker ensures re-runs do not duplicate the block. Per-user
`~/.bashrc` is used (not `/etc/profile.d/`) for consistency with other roles.

## `become_user` on `unarchive`

**Decision**: Set `become_user: "{{ item }}"` on the `unarchive` task.

**Rationale**: FR-015 requires that files under `/home/{{ item }}/flutter`
are owned by `{{ item }}:{{ item }}`. Using `become_user` on the extraction
task ensures the untarred files inherit the correct ownership without a
separate `chown` step. The play-level `become: true` in
`configure-linux-roles.yml` is inherited; task-level `become: true` is
therefore not repeated.

## Code Conventions

- All YAML files begin with `#SPDX-License-Identifier: MIT-0`.
- Task-level `become: true` is not used (play-level `become` is inherited).
- FQCN (`ansible.builtin.*`) is used throughout.
- The `blockinfile` task uses `ansible.builtin.blockinfile` FQCN for
  consistency, even though `blockinfile` also works without the prefix.
