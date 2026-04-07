# Java Role — Design

This document captures the non-obvious design decisions and technical
constraints of the `java` role. For requirements and user stories, see
`specs/005-java-role/spec.md`.

## Overview

The role performs two jobs per user in `desktop_user_names`:

1. **sdkman installation** — downloads the sdkman installer to `/tmp` and runs
   it as each user, placing sdkman in `~/.sdkman/`.
2. **Temurin JDK installation** — sources `~/.sdkman/bin/sdkman-init.sh` and
   runs `sdk install java {{ java_sdkman_identifier }}` for each user.

The installer download (Task 1) runs once as root (no `become_user`), writing
to `/tmp/sdkman-install.sh`, which is world-readable. Tasks 2 and 3 loop over
`desktop_user_names` using `become_user: "{{ item }}"`.

## Version-Specific Idempotency Guard Path

**Decision**: The `creates:` guard for the JDK install task uses the
version-specific path
`/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}/bin/java`,
not the `current/` symlink path.

**Rationale**: Using the version-specific path means that bumping
`java_sdkman_identifier` in `defaults/main.yml` causes the new version to be
installed on the next run, while the `creates:` guard for the previous version
remains satisfied, so the old install is not re-executed. Using `current/`
would mean the guard is always satisfied once any version is installed,
preventing controlled upgrades.

## sdkman `init.sh` Inline Sourcing

**Decision**: The JDK install task uses
`bash -c 'source /home/{{ item }}/.sdkman/bin/sdkman-init.sh &&
sdk install java ...'`
to source the sdkman init script inline within the shell command.

**Rationale**: `ansible.builtin.shell` spawns a non-interactive, non-login
shell. The sdkman functions (`sdk`) are defined only after sourcing
`~/.sdkman/bin/sdkman-init.sh`. Inline sourcing is simpler than modifying the
user's shell RC files before this task runs. The sdkman installer itself
appends the source line to `~/.bashrc` and `~/.profile`, so interactive
sessions work without any additional role task.

## No PATH Modification Needed

**Decision**: The role does not add any entry to users' PATH.

**Rationale**: The sdkman installer automatically appends the
`source ~/.sdkman/bin/sdkman-init.sh` snippet to `~/.bashrc` and
`~/.profile` when it runs. Interactive logins therefore inherit the `sdk`
function and the sdkman-managed `java` binary on the PATH. No
`ansible.builtin.blockinfile` task is required.

## No Task-Level `become`

**Decision**: No task in this role sets `become: true` at task level.

**Rationale**: The calling playbook (`configure-linux-roles.yml`) sets
`become: true` at play level, which all tasks inherit. Per-user tasks use
`become_user: "{{ item }}"` to switch user context, matching the pattern
established in the `android_studio` and `flutter` reference roles.

## ARM64 Compatibility

**Decision**: No architecture-specific branching in task files; the role
carries no `not-supported-on-vagrant-arm64` tag in `configure-linux-roles.yml`.

**Rationale**: Both sdkman and Eclipse Temurin publish ARM64 (`aarch64`)
artifacts. The sdkman installer detects the host architecture at runtime and
downloads the appropriate binary. The Temurin JDK candidate identified by
`tem` suffix is available for both `x86_64` and `aarch64`. No platform guard
is necessary.

## Code Conventions

- All YAML files begin with `#SPDX-License-Identifier: MIT-0`.
- Task-level `become: true` is not used (play-level `become` is inherited).
- FQCN (`ansible.builtin.*`) is used throughout.
