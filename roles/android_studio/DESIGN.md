# Android Studio Role — Design

This document captures the non-obvious design decisions and technical
constraints of the `android_studio` role. For requirements and user
stories, see `specs/003-android-studio-role/spec.md`.

## Overview

The role performs two distinct jobs:

1. **Snap install** — installs Android Studio system-wide via
   `community.general.snap`.
2. **SDK pre-provisioning** — bootstraps the Android SDK for every user
   listed in `desktop_user_names` so the first-launch wizard completes
   within 30 seconds without downloading anything.

AMD64 Ubuntu only; ARM64 hosts are skipped via the
`not-supported-on-vagrant-arm64` tag applied in
`configure-linux-roles.yml`.

## Why cmdline-tools Must Be Bootstrapped Separately

The Android Studio snap bundles JetBrains Runtime (JBR) but does **not**
expose `sdkmanager` at a known path. There is no way to call `sdkmanager`
without first installing the Android command-line tools separately.

The bootstrap sequence for each user is therefore:

1. Download the cmdline-tools ZIP from Google (`ansible.builtin.get_url`).
2. Extract and rename it into the user's `ANDROID_HOME`
   (`ansible.builtin.unarchive` + `ansible.builtin.command`).
3. Use `community.general.android_sdk` to install the remaining SDK
   components declaratively, with license acceptance.

`community.general.android_sdk` was chosen over raw `shell` calls to
`sdkmanager` because it handles idempotency and license acceptance
(`accept_licenses: true`) without custom guards.

## Non-Obvious Technical Constraints

### JAVA_HOME

`sdkmanager` requires Java 17+. The `java` role installs the Eclipse Temurin
JDK via sdkman for each user in `desktop_user_names`. Tasks that invoke
`sdkmanager` (directly or via `community.general.android_sdk`) must set
`JAVA_HOME` to the versioned sdkman candidate path:

```text
/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}
```

The versioned path (using the `java_sdkman_identifier` variable from
`roles/java/defaults/main.yml`) is used in preference to the `current/`
symlink. The symlink is updated by `sdk default java` and may point to a
different version if the user changes their default; the versioned path is
always stable.

### sdkmanager Must Be Added to PATH

`community.general.android_sdk` locates `sdkmanager` via `PATH`. The
module does not accept an explicit path. Tasks must export:

```text
PATH: "{{ ansible_env.PATH }}:{{ android_home }}/cmdline-tools/latest/bin"
```

### cmdline-tools ZIP Extract-and-Rename

The cmdline-tools ZIP contains a top-level `cmdline-tools/` directory.
Extracting directly to `~/Android/Sdk/cmdline-tools/latest/` produces
unwanted double-nesting (`…/latest/cmdline-tools/`). The correct sequence:

1. Extract to `~/Android/Sdk/cmdline-tools/` — creates
   `~/Android/Sdk/cmdline-tools/cmdline-tools/`.
2. Rename `cmdline-tools/cmdline-tools/` to `cmdline-tools/latest/`.

The rename task uses `creates: ~/Android/Sdk/cmdline-tools/latest/bin/sdkmanager`
as an idempotency guard.

### No `latest` Token in android_sdk Module

`community.general.android_sdk` requires explicit version strings such as
`platforms;android-37` or `build-tools;35.0.0`. There is no symbolic
`latest` token. The role detects the current latest versions at runtime
by parsing `sdkmanager --list --channel=0` output.

### SHA-1 Checksum Only

Google publishes SHA-1 checksums (not SHA-256) for cmdline-tools ZIPs.
The download task uses `checksum: "sha1:{{ android_cmdlinetools_sha1 }}"`.
See TD-009 in the technical debt register for the accepted risk.

## Per-User Provisioning

`ANDROID_HOME` is per-user (`~/Android/Sdk`), not system-wide. The role
loops over `desktop_user_names` and runs each SDK task with
`become_user: "{{ item }}"` to ensure correct file ownership. The play
in `configure-linux-roles.yml` sets `become: true`; individual tasks
must not repeat it.

## Code Conventions

- All YAML files begin with `#SPDX-License-Identifier: MIT-0`.
- Task-level `become: true` is not used (play-level `become` is inherited).
- FQCN (`ansible.builtin.*`, `community.general.*`) is used throughout.
