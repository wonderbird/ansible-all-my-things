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

## Stamp-File Idempotency

**Decision**: Use an Ansible-written stamp file
(`/home/{{ item }}/flutter/.ansible_installed_version`) as the idempotency
signal, not a file shipped by the SDK.

**Rationale**: Flutter 3.x does **not** ship a `version` file at the SDK
root. Relying on `flutter/version` (the original plan) meant `stat.exists`
was always `False`, causing a remove-and-re-extract on every playbook run.
Running `flutter --version` was also rejected because it requires Dart
runtime initialisation — a slow first-run compilation step that may fail in a
headless provisioning environment.

The stamp file is written by Ansible immediately after extraction and contains
only the version string (e.g. `3.41.6\n`). It is the sole idempotency signal.

**Implementation sequence per user**:

1. `ansible.builtin.stat` — check whether
   `/home/{{ item }}/flutter/.ansible_installed_version` exists.
2. `ansible.builtin.slurp` — read the file content when it exists.
3. `ansible.builtin.set_fact` — build a `flutter_installed_versions` dict
   keyed by username.
4. `ansible.builtin.file` (state=absent) — remove the old SDK directory when
   the installed version differs from `flutter_version`.
5. `ansible.builtin.unarchive` — extract the archive when the version differs.
6. `ansible.builtin.copy` — write `flutter_version` to the stamp file after
   extraction.

The `sha256` checksum on `get_url` is used for **download integrity
verification**, not for idempotency decisions.

**Upgrade trigger**: bump `flutter_version` (and `flutter_sha256`) in
`defaults/main.yml` and re-run the playbook. No other change is required.

## Tarball Download Optimisation

**Decision**: Skip `get_url` entirely when every user in
`desktop_user_names` already has the target version installed.

**Rationale**: Downloading a ~1.4 GB archive on every run — even if the
SDK is already installed — wastes time and bandwidth. A single `when:`
condition on the `get_url` task checks whether any user still needs the
update before initiating the download.

**Implementation**: The condition uses Jinja2 set arithmetic:

```yaml
when: >
  desktop_user_names | difference(
    (flutter_installed_versions | default({}))
    | dict2items
    | selectattr('value', 'equalto', flutter_version)
    | map(attribute='key')
    | list
  ) | length > 0
```

This computes the set of users whose installed version does not match
`flutter_version`. If that set is empty (all users are current), the
download is skipped for the entire play. The downstream `file`,
`unarchive`, `copy`, and `blockinfile` tasks each carry their own
per-user `when:` guards and are similarly skipped.

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

## Android SDK Components: NDK and CMake Excluded

**Decision**: Do not install NDK (Side by Side), Android SDK CMake, or any
additional `platforms;android-N` package beyond what the `android_studio`
role already provisions.

**Rationale**: The declared use case is **Chrome/web only**.

- `flutter build web` compiles Dart to JavaScript/WebAssembly via
  `dart2js`/`dart2wasm`. No native Android toolchain is invoked.
- `flutter doctor`'s Chrome check verifies only that a `google-chrome`
  binary is executable. NDK and Android SDK CMake are invisible to it.
- The Android toolchain check in `flutter doctor` validates
  `platform-tools`, `build-tools`, `platforms`, `cmdline-tools/latest`,
  and a JDK — all satisfied by the `android_studio` and `java` roles.
- `platforms;android-N` is already handled dynamically by `android_studio`
  (via `sdkmanager --list --channel=0`); installing it again here would be
  redundant.

**Cost of including them**: NDK alone is ~500 MB–1 GB. Each component adds
provisioning time, version-tracking, checksum maintenance, and a
troubleshooting surface — all with no benefit for the Chrome/web target.

**Alternatives considered**: Installing NDK and Android SDK CMake —
rejected because they provide no benefit for this use case and impose
non-trivial provisioning and maintenance cost.

## Code Conventions

- All YAML files begin with `#SPDX-License-Identifier: MIT-0`.
- Task-level `become: true` is not used (play-level `become` is inherited).
- FQCN (`ansible.builtin.*`) is used throughout.
- The `blockinfile` task uses `ansible.builtin.blockinfile` FQCN for
  consistency, even though `blockinfile` also works without the prefix.
