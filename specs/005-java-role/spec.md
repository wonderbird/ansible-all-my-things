# Feature Specification: Java Role (sdkman + Temurin JDK)

**Feature Branch**: `005-java-role`
**Created**: 2026-04-07
**Status**: Draft
**Input**: User description: "Install sdkman and use it to provision the
current LTS version of the Temurin JDK for every user listed in
`desktop_user_names`."

## User Scenarios & Testing

### User Story 1 - Developer Workstation Has Java After Provisioning (Priority: P1)

A developer runs the Ansible playbook against a fresh Ubuntu workstation. After
the play completes, every user listed in `desktop_user_names` can open a
terminal and execute Java programs without any manual installation steps.

**Why this priority**: This is the primary deliverable of the role. All other
stories depend on this baseline being met.

**Independent Test**: Run the playbook against a clean VM, then log in as one
of the provisioned users and verify that `java -version` exits with code 0 and
prints output containing "Temurin".

**Acceptance Scenarios**:

1. **Given** a clean Ubuntu VM with no prior Java installation, **When** the
   playbook runs with the `java` role enabled, **Then** every user in
   `desktop_user_names` can execute `java -version` and the output contains
   the word "Temurin".

2. **Given** the playbook has already run successfully, **When** the playbook
   runs again against the same host, **Then** no tasks report `changed` (full
   idempotency) and `java -version` still succeeds for every provisioned user.

---

### User Story 2 - sdkman Is Available for the User (Priority: P2)

After provisioning, each user in `desktop_user_names` has sdkman installed in
their home directory and can use it interactively to list, install, or switch
Java versions.

**Why this priority**: sdkman is the mechanism by which Java is installed and
managed. A working sdkman installation enables future self-service version
management by developers without re-running the playbook.

**Independent Test**: Log in as a provisioned user, source
`~/.sdkman/bin/sdkman-init.sh`, and run `sdk version` — it should print the
sdkman version without errors.

**Acceptance Scenarios**:

1. **Given** the playbook has run, **When** a provisioned user sources
   `~/.sdkman/bin/sdkman-init.sh` in a shell, **Then** the `sdk` command
   becomes available and `sdk version` executes successfully.

2. **Given** sdkman is already installed for a user, **When** the playbook runs
   again, **Then** the sdkman installation task is skipped (not re-downloaded
   or re-executed).

---

### User Story 3 - Pinned JDK Version Is Configurable (Priority: P3)

An operator can change the Temurin JDK version installed by updating a single
variable in the role defaults without modifying any task file.

**Why this priority**: Pinning the version in `defaults/main.yml` ensures
reproducible builds and allows controlled upgrades when a new LTS ships.

**Independent Test**: Change `java_sdkman_identifier` in `defaults/main.yml` to
a different valid Temurin identifier, run the playbook on a host where the
original version is already installed, and verify the new version is installed
and selectable.

**Acceptance Scenarios**:

1. **Given** a different valid Temurin identifier is set in
   `java_sdkman_identifier`, **When** the playbook runs, **Then** the
   specified version of the Temurin JDK is installed under
   `~/.sdkman/candidates/java/` for each provisioned user.

---

### Edge Cases

- What happens when `desktop_user_names` is empty? The per-user loop should
  run zero iterations; no tasks should fail.
- What happens when sdkman installation is interrupted (partial
  `~/.sdkman` directory present)? The `creates:` guard targets
  `~/.sdkman/bin/sdkman-init.sh`; a partial install without that file causes
  re-execution of the installer.
- What happens when the specified `java_sdkman_identifier` is not a valid
  sdkman candidate string? The `sdk install` command exits non-zero and the
  task fails with an informative error message.
- What happens on ARM64 hosts? The role must work correctly on both AMD64
  and ARM64; sdkman and Temurin both publish ARM64 artifacts.

## Requirements

### Functional Requirements

- **FR-001**: The role MUST install sdkman into `~/.sdkman` for every user
  listed in `desktop_user_names`.
- **FR-002**: The role MUST install the Temurin JDK version identified by
  `java_sdkman_identifier` via sdkman for every user listed in
  `desktop_user_names`.
- **FR-003**: After the role runs, executing `java -version` as any provisioned
  user MUST succeed (exit code 0) and the output MUST contain the string
  "Temurin".
- **FR-004**: The Temurin JDK version identifier MUST be stored in
  `defaults/main.yml` as `java_sdkman_identifier` so it can be overridden per
  host or group.
- **FR-005**: Every task that uses `command` or `shell` MUST include a
  `creates:` guard or `changed_when:` annotation to ensure idempotency.
  `ansible.builtin.get_url` tasks are already idempotent via `force: false`
  (the default) and do not require a separate `creates:` guard. The
  idempotency guard for the Java install task MUST use the version-specific
  path `~/.sdkman/candidates/java/{{ java_sdkman_identifier }}/bin/java` (not
  the `current/` symlink path), so that changing `java_sdkman_identifier`
  triggers a re-install of the new version.
- **FR-006**: The role MUST be idempotent: running it twice against the same
  host MUST produce no `changed` tasks on the second run.
- **FR-007**: The role MUST work on both AMD64 and ARM64 Ubuntu Linux hosts.
- **FR-008**: All YAML files in the role MUST begin with the comment
  `#SPDX-License-Identifier: MIT-0`.
- **FR-009**: All Ansible module references MUST use fully qualified collection
  names (`ansible.builtin.*`, `community.general.*`).
- **FR-010**: The role MUST NOT set `become: true` at task level; play-level
  `become: true` is inherited from the calling playbook. Per-user tasks MUST
  use `become_user: "{{ item }}"` to switch to each user's context, matching
  the pattern established in the `android_studio` role.
- **FR-011**: The role MUST include a `meta/main.yml` with `galaxy_info`.
- **FR-012**: The role MUST include a `DESIGN.md` documenting non-obvious design
  decisions.
- **FR-013**: The role MUST install the packages `zip`, `unzip`, and `curl` via
  `ansible.builtin.apt` as the very first task in `tasks/main.yml`, before any
  sdkman installation steps. These packages are required by the sdkman installer.
- **FR-014**: The role MUST include a Molecule test scenario under
  `roles/java/molecule/default/` using the `podman` driver (via
  `molecule-plugins[podman]`).
- **FR-015**: The Molecule scenario MUST use `ubuntu:24.04` as the container
  image platform.
- **FR-016**: The Molecule scenario MUST include a `prepare.yml` playbook that
  installs `python3` and `sudo` inside the container before the converge phase
  runs (Ansible requires both to execute tasks).
- **FR-017**: The Molecule `prepare.yml` MUST create a system user named
  `testuser` inside the container, and the Molecule `converge.yml` MUST pass
  `desktop_user_names: ["testuser"]` to the role.
- **FR-018**: The Molecule scenario MUST enable the built-in idempotency
  verifier step (second converge run that asserts zero `changed` tasks).
- **FR-019**: The Molecule scenario MUST include a `verify.yml` playbook that
  runs `java -version` as `testuser` and asserts the output contains "Temurin".

### Key Entities

- **`desktop_user_names`**: A list of OS usernames that the role provisions.
  Each user receives an independent sdkman installation and Temurin JDK in
  their own home directory.
- **`java_sdkman_identifier`**: A string in sdkman candidate format (e.g.,
  `21.0.7-tem`) that uniquely identifies the Temurin JDK build to install.
- **sdkman installation**: Per-user directory tree rooted at `~/.sdkman`,
  initialized by the sdkman shell installer. Presence is checked via
  `~/.sdkman/bin/sdkman-init.sh`.
- **Temurin JDK candidate**: Per-user installation under
  `~/.sdkman/candidates/java/<identifier>/`. The `current` symlink points to
  the active version; `java` binary lives at
  `~/.sdkman/candidates/java/current/bin/java`. Idempotency guards MUST
  reference the version-specific path
  `~/.sdkman/candidates/java/{{ java_sdkman_identifier }}/bin/java` rather
  than the `current/` symlink, so that updating `java_sdkman_identifier` causes
  the new version to be installed.

## Success Criteria

### Measurable Outcomes

- **SC-001**: After the role runs, `java -version` executed as any user in
  `desktop_user_names` exits with code 0 and its output contains "Temurin".
- **SC-002**: A second consecutive run of the playbook produces zero `changed`
  tasks for the `java` role (full idempotency).
- **SC-003**: The role runs to completion without errors on both AMD64 and
  ARM64 Ubuntu Linux test VMs.
- **SC-004**: The installed JDK version matches the value of
  `java_sdkman_identifier` defined in `defaults/main.yml`.
- **SC-005**: Running `molecule test` inside `roles/java/` succeeds: the
  converge phase installs Java without errors, the idempotency step reports
  zero `changed` tasks, and the verify step confirms `java -version` output
  contains "Temurin" for `testuser`.

## Assumptions

- The sdkman installer script URL (`https://get.sdkman.io`) is publicly
  accessible from the provisioning target.
- The sdkman installer is downloaded over HTTPS without a separate checksum
  file; no checksum verification is performed. This is intentional: sdkman
  does not publish signed checksums for its installer, and HTTPS transport
  integrity is considered sufficient, matching the convention established in the
  `android_studio` role.
- The Temurin JDK identifier `21.0.7-tem` is used as the default pinned
  version; this represents the Temurin build of OpenJDK 21 LTS as of the
  feature authoring date. Operators MUST update this value when a newer LTS
  patch is desired.
- `desktop_user_names` is defined at the play or group level before the role
  is invoked; it is not the role's responsibility to create these OS users.
- The calling playbook sets `become: true` at play level, which the role
  relies on to switch to each user's context via `become_user: "{{ item }}"`.
- No system-wide Java installation (`/usr/bin/java`, `apt install default-jdk`)
  is required; the role provisions Java exclusively through sdkman in user home
  directories.
- Internet access is available during provisioning; no offline/air-gapped
  support is in scope.
- A Molecule test suite (`molecule-plugins[podman]`) is the primary automated
  acceptance mechanism for this role. `molecule test` MUST pass before the
  branch is merged.
- Standard Ansible output and verbosity apply to all tasks. No task in this
  role requires `no_log: true`; in particular, the sdkman init script source
  path does not contain sensitive data and MUST NOT suppress output.
