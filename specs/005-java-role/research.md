<!-- SPDX-License-Identifier: MIT-0 -->

# Research: Java Role (sdkman + Temurin JDK)

**Branch**: `005-java-role` | **Date**: 2026-04-07

This document resolves every unknown and dependency identified during plan
Technical Context fill-in.

## sdkman Installer — Download and Idempotency

**Decision**: Use `ansible.builtin.get_url` to download the sdkman installer
script to a fixed path (e.g. `/tmp/sdkman-install.sh`), guarded with
`creates: /tmp/sdkman-install.sh`. Then run it with `ansible.builtin.shell`
guarded with `creates: ~/.sdkman/bin/sdkman-init.sh`.

**Rationale**: sdkman provides a single-file shell installer at
`https://get.sdkman.io`. There is no system package, no checksum file, and
no Ansible Galaxy collection module for sdkman. The two-step
download-then-execute pattern is the minimal idiomatic approach; the
`creates:` guards on both steps ensure idempotency. This pattern is already
established by the `android_studio` role's `get_url` + `unarchive` sequence.

**Alternatives considered**:

- Ansible Galaxy `ironicbadger.sdkman` role: introduces an external
  dependency and is overkill for a three-task installation. Rejected per
  Principle IV (YAGNI).
- Downloading and re-running the installer every time with `changed_when:
  false`: hides genuine first-run changes; violates spirit of Principle I.
- System-package Java (`apt install default-jdk`): does not install sdkman
  or Temurin; out of scope per spec Assumption 6.

## sdkman Installer URL and Checksum

**Decision**: Download from `https://get.sdkman.io` without checksum
verification. This matches the project convention established in the
`android_studio` role (spec section Assumptions, bullet 2) and is consistent
with how all upstream sdkman documentation instructs users to install sdkman.

**Rationale**: sdkman does not publish signed checksums for its installer
script. HTTPS transport integrity is the accepted control. The spec explicitly
states this assumption and notes it matches the `android_studio` convention.

**Alternatives considered**:

- SHA-256 checksum: not available from upstream; cannot be added.
- Pinning the installer to a tagged GitHub release URL: possible but
  introduces maintenance burden each time sdkman releases; not worth it given
  HTTPS is the project-accepted risk level.

## JDK Install Command — Idempotency Guard Path

**Decision**: Use a `creates:` guard pointing to the version-specific binary
path `~/.sdkman/candidates/java/{{ java_sdkman_identifier }}/bin/java`.

**Rationale**: The spec (FR-005 and Key Entities section) explicitly requires
the version-specific path, not `~/.sdkman/candidates/java/current/bin/java`.
Using the `current/` symlink would prevent the role from installing a newly
pinned version when `java_sdkman_identifier` is updated, because the symlink
always exists once any version is installed.

**Alternatives considered**:

- `current/bin/java`: Rejected — would silently skip version updates.
- A separate `sdk use` task: Not needed; `sdk install` sets the installed
  version as current by default.

## sdkman init.sh Sourcing in Shell Tasks

**Decision**: Source `~/.sdkman/bin/sdkman-init.sh` inline in the same
`ansible.builtin.shell` task that calls `sdk install java`:

```yaml
ansible.builtin.shell:
  cmd: >
    bash -c 'source /home/{{ item }}/.sdkman/bin/sdkman-init.sh
    && sdk install java {{ java_sdkman_identifier }}'
  creates: "/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}/bin/java"
```

**Rationale**: sdkman functions are shell functions defined by `sdkman-init.sh`;
they are not standalone executables. A non-interactive Ansible `shell` task
does not load `.bashrc`, so the init script must be sourced explicitly. Using
`bash -c 'source ... && sdk install ...'` is the idiomatic approach and avoids
creating a temporary wrapper script.

**Alternatives considered**:

- Setting `executable: /bin/bash` and sourcing in `cmd`: equivalent; `bash -c`
  is slightly clearer.
- Calling `~/.sdkman/candidates/java/.../bin/java` install path via direct
  tar extraction: bypasses sdkman bookkeeping; would break `sdk` commands for
  the user. Rejected.

## ARM64 Compatibility

**Decision**: No architecture-specific branching is required. The role runs
identically on AMD64 and ARM64.

**Rationale**: sdkman detects the host architecture at runtime and downloads
the appropriate Temurin JDK artifact. The Temurin `21.0.7-tem` identifier
resolves to an ARM64 tarball on ARM64 hosts automatically. Unlike the
`android_studio` role (which is tagged `not-supported-on-vagrant-arm64`
because the snap is AMD64-only), the `java` role needs no such tag.

**Alternatives considered**:

- `when: ansible_architecture == 'x86_64'`: Rejected — both architectures
  are supported; a conditional would incorrectly skip ARM64 hosts.

## Default JDK Identifier

**Decision**: `java_sdkman_identifier: "21.0.7-tem"` as the default in
`defaults/main.yml`.

**Rationale**: OpenJDK 21 is the current LTS as of the feature authoring date
(2026-04-07). The `tem` vendor suffix selects Eclipse Temurin (Adoptium).
`21.0.7` is the latest patch release of Java 21 LTS as of this date.

**Alternatives considered**:

- `21-tem` (floating minor/patch): installs the latest 21.x but makes
  idempotency fragile — sdkman would show the version as `21.0.7-tem` on
  disk but the guard path would differ. Rejected per FR-005.
- Java 17 LTS: older LTS; 21 is the current recommended LTS. Rejected.

## `become_user` vs. `become` Pattern

**Decision**: Tasks that operate in the user's home directory use
`become_user: "{{ item }}"` without `become: true` at task level. The
`ansible.builtin.get_url` download to `/tmp` does not need `become_user`.

**Rationale**: `configure-linux-roles.yml` sets `become: true` at play level
(line 4), which is inherited by all tasks. Adding `become: true` at task level
is redundant and violates FR-010. The `android_studio` reference role uses
exactly this pattern.

## No PATH Modification Required at Provisioning Time

**Decision**: The role does NOT add sdkman to `.bashrc` at provisioning time.

**Rationale**: sdkman's own installer appends the necessary `source
~/.sdkman/bin/sdkman-init.sh` snippet to `.bashrc` and `.profile` during
installation. No additional `blockinfile` task is needed, unlike the `flutter`
role which must add Flutter's `bin/` to PATH manually. This keeps the role
simpler (Principle IV).

**Alternatives considered**:

- Using `ansible.builtin.blockinfile` to ensure the PATH entry: would be
  redundant with what the sdkman installer already does and could create
  duplicate entries on re-run if the installer's own snippet differs slightly
  from what Ansible writes.
