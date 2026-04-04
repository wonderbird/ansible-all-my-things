# Feature Specification: Flutter Ansible Role

**Feature Branch**: `004-flutter-role`
**Created**: 2026-04-04
**Status**: Clarified
**Input**: User description: "Create a spec for a new Ansible role named
`flutter` that installs the Flutter SDK and its dependencies on AMD64 Linux
(hobbiton hcloud instance). The role depends on the `android_studio` role
being applied first. Installation method is not yet decided — it likely
involves apt packages, sdkmanager components, and a download step.
Acceptance criterion: `flutter doctor` reports no errors for the Chrome/web
target. The role must follow the same structure, tag placement, and
idempotency patterns as the `android_studio` role, including graceful skip
on ARM64. The primary use case is: provision machine, clone a Flutter GitHub
project, then run `flutter build` targeting Chrome."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build a Flutter Web App After Provisioning (Priority: P1)

A developer provisions a machine using this Ansible project, clones a Flutter
GitHub project onto that machine, and runs `flutter build web` targeting
Chrome. The build completes successfully without any manual SDK configuration
steps.

**Why this priority**: This is the primary end-to-end use case. If a
freshly provisioned machine cannot build a Flutter web project without
manual intervention, the role has not delivered its core value.

**Independent Test**: Provision a fresh AMD64 VM with the `flutter` role
applied, clone a known Flutter sample project, and run `flutter build web`.
Confirm the build completes without errors.

**Acceptance Scenarios**:

1. **Given** a freshly provisioned AMD64 machine with the `flutter` role
   applied, **When** a developer clones a Flutter project and runs
   `flutter build web`, **Then** the build completes successfully without
   requiring any additional SDK downloads or manual configuration.
2. **Given** a freshly provisioned AMD64 machine, **When** the developer
   runs `flutter doctor`, **Then** the Chrome/web target reports no errors
   or missing dependencies.
3. **Given** the `flutter` role is applied, **When** a developer runs
   `flutter build web` as the provisioned user, **Then** the command
   succeeds and produces a `build/web/` output directory.

---

### User Story 2 - Idempotent Re-runs (Priority: P2)

A developer runs the provisioning playbook multiple times against the same
machine. The `flutter` role must not break subsequent runs or re-install an
already-present Flutter SDK installation.

**Why this priority**: Idempotency is a core Ansible principle and is
required for the role to be safely usable in recurring provisioning
workflows.

**Independent Test**: Run the playbook twice on the same AMD64 VM and
confirm the second run reports no `changed` tasks for the `flutter` role.

**Acceptance Scenarios**:

1. **Given** the Flutter SDK was installed by a previous playbook run,
   **When** the playbook runs again, **Then** all tasks in the `flutter`
   role report `ok` or `skipped`, never `changed`.

---

### User Story 3 - Graceful Skip on ARM64 Machines (Priority: P2)

A developer runs the playbook against an ARM64 machine (e.g., a Vagrant VM
on Apple Silicon). The `flutter` role tasks are skipped without errors,
consistent with the `android_studio` role's behaviour on the same host.

**Why this priority**: The project runs against both AMD64 cloud machines
and ARM64 local VMs. The role must not break ARM64 provisioning runs.

**Independent Test**: Run the playbook against an ARM64 Vagrant VM. Verify
that all tasks in the `flutter` role are skipped and the playbook completes
successfully.

**Acceptance Scenarios**:

1. **Given** the target machine is ARM64, **When** the playbook runs,
   **Then** all `flutter` role tasks are skipped via the
   `not-supported-on-vagrant-arm64` tag and no errors are reported.
2. **Given** the target machine is ARM64, **When** the playbook runs,
   **Then** the `android_studio` role tasks are also skipped (both roles
   are consistently absent on ARM64).

---

### User Story 4 - Role Integrates Without Extra Friction (Priority: P3)

A developer who maintains the playbook adds the `flutter` role to the
provisioning run by adding a single entry to `configure-linux-roles.yml`.
No other changes to existing playbooks or roles are required.

**Why this priority**: Ease of integration reduces maintenance burden and
ensures the role follows the same convention as every other role in this
project.

**Independent Test**: Add the `flutter` role entry to
`configure-linux-roles.yml` only, run the playbook against a fresh VM, and
confirm Flutter is installed without editing any other file.

**Acceptance Scenarios**:

1. **Given** the `flutter` role entry is added to `configure-linux-roles.yml`,
   **When** the playbook runs, **Then** Flutter is installed without
   modifying any other playbook file.

---

### Edge Cases

- If the `android_studio` role has not run beforehand, the `flutter` role
  may fail due to missing SDK prerequisites. This is an operator error; the
  role documents its dependency but does not attempt to install
  `android_studio` itself.
- If network access is unavailable during provisioning, any download steps
  fail and the playbook aborts with an error. No special retry or fallback
  handling is performed.
- If disk space is insufficient for the Flutter SDK download, the task
  fails and the playbook aborts with an error. No special handling is
  performed.
- If an older Flutter installation already exists at the expected path,
  the role compares the installed version against the `flutter_version`
  variable. If they match, all download and extract tasks are skipped
  (no-op). If they differ, the old installation is replaced by the new
  version. The upgrade is triggered solely by bumping `flutter_version` in
  `defaults/main.yml`; re-running the playbook with the same value is
  always a no-op.
- On ARM64, both `flutter` and `android_studio` role tasks are skipped;
  the playbook must not fail because `flutter doctor` is never executed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST contain an Ansible role named `flutter`
  placed at `roles/flutter/` using the standard Ansible role directory
  structure.
- **FR-002**: The `flutter` role MUST install the Flutter SDK on the target
  AMD64 Linux machine such that the `flutter` binary is available on the
  provisioned user's PATH.
- **FR-003**: The role MUST be added to `configure-linux-roles.yml` so that
  it is applied as part of the standard provisioning run. It MUST NOT be
  added directly to `configure-linux.yml`.
- **FR-004**: The role MUST follow the same structure, tag placement, and
  idempotency approach established by the `android_studio` role.
- **FR-005**: The role MUST be idempotent: running it multiple times on the
  same machine MUST produce the same result without errors or redundant
  changes.
- **FR-006**: The role MUST execute only on AMD64 hosts. ARM64 and other
  architectures are not in scope and must be handled gracefully.
- **FR-007**: The role MUST be skippable on ARM64 hosts via the tag
  `not-supported-on-vagrant-arm64`. The tag is applied at the role entry
  level in `configure-linux-roles.yml`; individual tasks inside the role do
  NOT carry the tag. This is consistent with the pattern established by the
  `android_studio` and `google_chrome` roles.
- **FR-008**: If the role is ever invoked via `ansible.builtin.include_role`
  (dynamic include), the caller MUST use the `apply: tags:` parameter to
  propagate the tag to inner tasks.
- **FR-009**: After the role runs, `flutter doctor` MUST report no errors for
  the Chrome/web target on the provisioned machine.
- **FR-010**: The role MUST depend on the `android_studio` role having been
  applied first. This prerequisite MUST be documented in `README.md`.
  The `meta/main.yml` file MUST keep `dependencies: []` (empty). The role
  MUST NOT silently install `android_studio` itself. Meta-level dependencies
  are not used in this project because they are invisible to playbook
  readers, break tag filtering, and are designed for redistributed roles
  rather than single-playbook provisioners.
- **FR-011**: The Flutter SDK MUST be installed by downloading the official
  stable release archive (`.tar.xz`) from `flutter.dev` as described in the
  Flutter manual installation guide
  (https://docs.flutter.dev/install/manual). The role MUST NOT use `apt`,
  `snap`, or `sdkmanager` for the Flutter SDK itself.
- **FR-012**: The role MUST configure the Flutter environment for every user
  listed in `desktop_user_names` by adding `$HOME/flutter/bin` to `$PATH`
  in each user's `~/.bashrc` via `ansible.builtin.blockinfile`, so that
  those users can invoke `flutter` commands without additional shell
  configuration.
- **FR-013**: The role MUST NOT install Android Studio or Android SDK
  components that are already handled by the `android_studio` role, to
  avoid duplication and potential conflicts.
- **FR-014**: The Chrome web browser MUST be present on the machine when the
  role runs; the `google_chrome` role is assumed to have already installed
  it. The `flutter` role does not install Chrome.
- **FR-015**: The Flutter SDK MUST be extracted to `/home/{{ item }}/flutter`
  for each user listed in `desktop_user_names`, consistent with the
  `android_studio` role placing its SDK under `~/Android/Sdk`. Files under
  this directory MUST be owned by `{{ item }}:{{ item }}`; use
  `become_user: "{{ item }}"` on the `unarchive` task to ensure correct
  ownership.
- **FR-016**: PATH configuration for the Flutter SDK MUST be performed via
  `ansible.builtin.blockinfile` in each user's `~/.bashrc`, following the
  same pattern as the `claude_code` role. The block MUST add
  `$HOME/flutter/bin` to `$PATH`.
- **FR-017**: The role MUST install the following apt packages as Flutter
  system dependencies: `clang`, `cmake`, `ninja-build`, `pkg-config`,
  `libgtk-3-dev`, `mesa-utils`. These packages MUST be installed before the
  Flutter SDK archive is extracted.
- **FR-018**: After installing the apt packages in FR-017, the role MUST run
  `systemctl daemon-reload` to ensure any new unit files are recognised by
  the init system.
- **FR-019**: A role variable `flutter_sha256` in `defaults/main.yml` MUST
  store the SHA-256 checksum of the Flutter SDK archive for the version
  specified by `flutter_version`. The `get_url` task MUST pass
  `checksum: "sha256:{{ flutter_sha256 }}"` to verify archive integrity,
  mirroring the `android_studio` checksum pattern.
- **FR-020**: *(merged into FR-010)*
- **FR-021**: A role variable `flutter_version` in `defaults/main.yml`
  MUST control which version of the Flutter SDK is installed. The default
  value MUST be a specific, pinned stable release (e.g. `3.29.2`).
- **FR-022**: The role MUST be idempotent with respect to version: if the
  installed Flutter version matches `flutter_version`, all download and
  extraction tasks MUST be skipped. If the versions differ, the role MUST
  replace the existing installation with the version specified by
  `flutter_version`. An upgrade is triggered solely by bumping
  `flutter_version` and re-running the playbook.
- **FR-023**: The role MUST include a `DESIGN.md` file under `roles/flutter/`
  documenting non-obvious implementation decisions (e.g. version-based
  idempotency mechanism, PATH setup approach, apt prerequisite rationale).

### Key Entities

- **Ansible Role (`flutter`)**: A self-contained unit of Ansible automation
  placed under `roles/flutter/` that encapsulates all tasks, files,
  templates, and variables needed to install the Flutter SDK and satisfy
  the Chrome/web target in `flutter doctor`.
- **`configure-linux-roles.yml`**: The roles playbook where the `flutter`
  role entry will be added, after the `android_studio` entry, consistent
  with the declared dependency order.
- **`desktop_user_names`**: A variable defined in `group_vars/` or
  `host_vars/` listing the users for whom Flutter must be configured. The
  role iterates over this list but does not define or validate it.
- **Target Host (`hobbiton`)**: An AMD64 Hetzner Cloud instance running a
  Debian/Ubuntu-based Linux distribution where the Flutter SDK will be
  installed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a provisioning run that includes the `flutter` role,
  running `flutter doctor` on the target VM exits with zero errors for the
  Chrome/web target.
- **SC-002**: After provisioning, a developer can clone a Flutter project
  and run `flutter build web` to completion without any manual configuration
  steps or additional downloads.
- **SC-003**: Running the playbook twice on the same AMD64 VM produces zero
  `changed` tasks for the `flutter` role on the second run.
- **SC-004**: Running the playbook against an ARM64 machine completes without
  errors, with all `flutter` role tasks skipped.
- **SC-005**: Adding the role to the provisioning playbook requires no more
  than a single entry in `configure-linux-roles.yml`.

## Clarifications

The following questions were raised during specification and have been
resolved by the user.

| # | Question | Decision |
|---|----------|----------|
| Q1 | PATH configuration method for desktop users | **Option A — `blockinfile` in each user's `~/.bashrc`.** Same pattern as the `claude_code` role. The block adds `$HOME/flutter/bin` to `$PATH`. |
| Q2 | Flutter SDK install directory per user | **Option A — `/home/{{ item }}/flutter` per user.** Consistent with `android_studio` placing its SDK under `~/Android/Sdk`. |
| Q3 | System apt packages required as Flutter dependencies | **Custom — install exactly:** `clang`, `cmake`, `ninja-build`, `pkg-config`, `libgtk-3-dev`, `mesa-utils`. Also run `systemctl daemon-reload` after package installation. This is a proven list from the user's manual installation experience. |
| Q4 | Checksum verification for the Flutter SDK archive | **Option A — store `flutter_sha256` in `defaults/main.yml` alongside `flutter_version`; pass `checksum: "sha256:{{ flutter_sha256 }}"` to `get_url`.** Mirrors the `android_studio` checksum pattern. |
| Q5 | How to document the `android_studio` prerequisite dependency | **Option A — document `android_studio` as prerequisite in `README.md` only; `meta/main.yml` keeps `dependencies: []`.** Consistent with all other roles in the project. Meta dependencies are invisible to playbook readers, break tag filtering, and are designed for redistributed roles — not private single-playbook provisioners. |

## Assumptions

- The `android_studio` role is applied before the `flutter` role in every
  provisioning run. The `flutter` role does not validate this at runtime.
- The `google_chrome` role is applied before the `flutter` role, ensuring
  the Chrome browser is present for the web target.
- The target machines are running a Debian/Ubuntu-based Linux distribution,
  consistent with the rest of this Ansible project.
- The role will be integrated via `configure-linux-roles.yml` rather than
  directly into `configure-linux.yml`.
- The provisioned user account is already created by the `setup-users.yml`
  playbook before this role runs.
- Outbound internet access is available during provisioning for any required
  downloads.
- Only AMD64 architecture is in scope; ARM64 and other architectures are
  explicitly out of scope for this role.
- The Flutter installation must satisfy the Chrome/web target in
  `flutter doctor`; other targets (Android emulator, iOS, desktop) are out
  of scope.
- `desktop_user_names` is defined in inventory variables before this role
  executes; the role does not validate its presence.
- The Flutter SDK is installed from the official `.tar.xz` archive
  published on `flutter.dev`. The archive URL format is stable enough to
  be constructed from `flutter_version` alone.
- Version-based idempotency is implemented by reading the `version` file
  at `<sdk_root>/version` (e.g. `/home/{{ item }}/flutter/version`) using
  `ansible.builtin.slurp`, and comparing its content to `flutter_version`.
  Running `flutter --version` is not used because it requires Dart runtime
  initialisation. The SHA-256 checksum stored in `flutter_sha256` is used
  by `get_url` for download integrity verification, not for idempotency
  decisions.
- Upgrades are intentional and operator-driven: bumping `flutter_version`
  (and updating `flutter_sha256` accordingly) in `defaults/main.yml` is
  the sole trigger for replacing the SDK. Downgrades follow the same
  mechanism as upgrades.
- The Flutter SDK is extracted per-user into `/home/{{ item }}/flutter`.
  This directory layout is consistent with the `android_studio` role
  placing the Android SDK under `~/Android/Sdk`.
- The apt packages `clang`, `cmake`, `ninja-build`, `pkg-config`,
  `libgtk-3-dev`, and `mesa-utils` are sufficient to satisfy the
  Flutter Chrome/web toolchain prerequisites on the target
  Debian/Ubuntu-based distribution. No additional system packages are
  required beyond what is already present on the base image.

## Out of Scope

- Flutter for ARM64, i386, or any architecture other than AMD64.
- Flutter Beta or dev channel releases; only the stable channel is in scope.
- Flutter targets other than Chrome/web (Android emulator, iOS, Linux
  desktop, Windows). These may work as a side-effect but are not validated.
- IDE preferences, Flutter project templates, or per-user Dart/Flutter
  configuration beyond PATH setup.
- Automatic Flutter version upgrades triggered by anything other than
  bumping the `flutter_version` role variable. The role never auto-upgrades
  to a newer stable release on its own.
- Flutter uninstallation or downgrade automation.
- Android SDK component installation beyond what the `android_studio` role
  already provisions.
- Creation or management of Flutter projects; the role only provisions the
  toolchain.
