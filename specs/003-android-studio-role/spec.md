# Feature Specification: Android Studio Ansible Role

**Feature Branch**: `003-android-studio-role`
**Created**: 2026-03-31
**Status**: Draft
**Input**: User description: "In order to develop Android applications on my
virtual machines, I would like to create a role named android-studio for this
ansible project, so that I can install Android Studio by mentioning the role
in the file configure-linux.yml"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install Android Studio via Ansible (Priority: P1)

A developer provisions a virtual machine using this Ansible project and wants
Android Studio to be installed automatically as part of the provisioning run.
They add the `android_studio` role to the playbook and run it. Android Studio
is installed and ready to launch on the machine.

**Why this priority**: This is the core deliverable — without a working
installation, no other functionality has value.

**Independent Test**: Run the playbook on a fresh VM with the role included
and verify that Android Studio can be launched afterward.

**Acceptance Scenarios**:

1. **Given** a VM that does not have Android Studio installed, **When** the
   playbook runs with the `android_studio` role applied to that host,
   **Then** Android Studio is installed and launchable.
2. **Given** a VM that already has Android Studio installed (same version),
   **When** the playbook runs again, **Then** the playbook completes without
   errors and Android Studio is not reinstalled (idempotency).
3. **Given** the `android_studio` role is referenced in `configure-linux.yml`,
   **When** the playbook runs on a host not configured for the role,
   **Then** the role is skipped without errors.

---

### User Story 2 - Idempotent Re-runs (Priority: P2)

A developer runs the provisioning playbook multiple times (e.g., after adding
other roles). The `android_studio` role must not break subsequent runs or
re-install an already-present installation.

**Why this priority**: Idempotency is a core Ansible principle and is required
for the role to be safely usable in recurring provisioning workflows.

**Independent Test**: Run the playbook twice on the same VM and confirm the
second run reports no changes and exits successfully.

**Acceptance Scenarios**:

1. **Given** Android Studio was installed by a previous playbook run, **When**
   the playbook runs again, **Then** all tasks in the `android_studio` role
   report `ok` or `skipped`, never `changed`.

---

### User Story 3 - Graceful Skip on Non-AMD64 Machines (Priority: P3)

A developer runs the playbook against an ARM64 machine (e.g., a Vagrant VM on
Apple Silicon). The `android_studio` role tasks are skipped without errors
because Android Studio is not available for that architecture.

**Why this priority**: The project runs against both AMD64 cloud machines and
ARM64 local VMs. The role must not break ARM64 runs.

**Independent Test**: Run the playbook against an ARM64 Vagrant VM. Verify
that all tasks in the `android_studio` role are skipped and the playbook
completes successfully.

**Acceptance Scenarios**:

1. **Given** the target machine is ARM64, **When** the playbook runs,
   **Then** all `android_studio` role tasks are skipped with the
   `not-supported-on-vagrant-arm64` tag and no errors are reported.

---

### Edge Cases

- If an older version of Android Studio is already installed, the role takes
  no action; upgrades are handled by snapd's automatic refresh mechanism.
- If network access is unavailable during provisioning, the snap install
  fails and the playbook aborts with an error. No special handling is
  performed.
- What happens if disk space is insufficient to complete the installation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST contain an Ansible role named `android_studio`
  placed at `roles/android_studio/` using the standard Ansible role directory
  structure.
- **FR-002**: The `android_studio` role MUST install Android Studio on the
  target Linux machine using the snap package
  (`snap install android-studio --classic`), consistent with the official
  Ubuntu install instructions.
- **FR-003**: The role MUST be added to `configure-linux-roles.yml` so that
  it is applied as part of the standard provisioning run. It must NOT be added
  directly to `configure-linux.yml`.
- **FR-003a**: The role MUST follow the same structure, tag placement, and
  idempotency approach established by the `google_chrome` role.
- **FR-004**: The role MUST be idempotent: running it multiple times on the
  same machine MUST produce the same result without errors or redundant
  changes.
- **FR-005**: The installed Android Studio MUST be launchable by the
  configured user after provisioning completes.
- **FR-006**: The role MUST execute only on AMD64 hosts. Android Studio does
  not provide a Linux ARM64 build; ARM64 machines are an expected operating
  condition and must be handled gracefully.
- **FR-007**: The role MUST be skippable on ARM64 hosts via the tag
  `not-supported-on-vagrant-arm64`. The tag is applied at the role entry level
  in `configure-linux-roles.yml`; individual tasks inside the role do NOT
  carry the tag. This keeps `tasks/main.yml` readable and avoids per-task tag
  repetition. This is consistent with the pattern established for the
  `google_chrome` role and `playbooks/setup-homebrew.yml`.
- **FR-008**: If the role is ever invoked via `ansible.builtin.include_role`
  (dynamic include), the caller MUST use the `apply: tags:` parameter to
  propagate the tag to inner tasks; otherwise the skip will not reach them.

### Key Entities

- **Ansible Role (`android_studio`)**: A self-contained unit of Ansible
  automation placed under `roles/android_studio/` that encapsulates all
  tasks, files, templates, and variables needed to install Android Studio.
- **`configure-linux.yml`**: The top-level playbook that orchestrates all
  provisioning steps; the `android_studio` role will be referenced here.
- **Target Host**: A virtual machine running a supported Linux distribution
  where Android Studio will be installed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a provisioning run that includes the `android_studio`
  role, `snap list android-studio` exits successfully on the target VM,
  confirming the snap is installed and active.
- **SC-002**: Running the playbook twice on the same VM produces zero
  `changed` tasks for the `android_studio` role on the second run.
- **SC-003**: Running the playbook against an ARM64 machine completes without
  errors, with all `android_studio` role tasks skipped.
- **SC-004**: Adding the role to the provisioning playbook requires no more
  than a single line or block entry to apply it to the appropriate host group.

## Clarifications

### Session 2026-03-31

- Q: How should Android Studio be installed? → A: Via snap package
  (`snap install android-studio --classic`), consistent with the official
  Ubuntu install instructions.
- Q: Should the role upgrade an existing installation? → A: No. The role
  ensures the snap is present (`state: present`); upgrades are left to
  snapd's built-in automatic refresh mechanism.
- Q: Should the role ensure snapd is installed and running? → A: No. snapd
  is assumed to be present on all target machines (standard Ubuntu). The
  role performs no snapd setup.
- Q: Should the role fail hard or continue with a warning if the snap
  install fails (e.g., no network)? → A: Fail hard. The role must not
  suppress snap errors; a failed install aborts the playbook.
- Q: What is the verifiable definition of "launchable" for acceptance
  testing? → A: `snap list android-studio` exits successfully (snap is
  installed and active).
  (`snap install android-studio --classic`), consistent with the official
  Ubuntu install instructions.

## Assumptions

- Android Studio will be installed via the official snap package
  (`android-studio --classic`). No tarball download or apt repository is
  involved.
- The target machines are running a Debian/Ubuntu-based Linux distribution,
  consistent with the rest of this Ansible project.
- The role will be integrated via `configure-linux-roles.yml` (which is
  already imported by `configure-linux.yml`) rather than added directly to
  `configure-linux.yml`.
- The provisioned user account is already created by the `setup-users.yml`
  playbook before this role runs.
- The snap package bundles all required dependencies (including a Java
  runtime); no separate dependency installation is needed.
- snapd is assumed to be pre-installed on all target machines (standard
  Ubuntu); the role performs no snapd setup.
- Only AMD64 architecture is in scope; ARM64 and other architectures are
  explicitly out of scope for this role.

## Technical Debt

Because the role uses `state: present` and delegates upgrades to snapd's
automatic refresh, re-running the playbook on an already-provisioned machine
is a true no-op and does not change the installed version. Idempotency is
fully preserved between playbook runs.

The remaining version-consistency concern is narrower: fresh machines
provisioned at different points in time will receive whichever snap revision
was current at the time of first install. This means two machines provisioned
weeks apart may run different Android Studio versions. This is accepted for
developer workstation tooling where staying current outweighs strict version
pinning across a fleet.

The existing technical debt entry in
`docs/architecture/technical-debt/technical-debt.md` covering this pattern
MUST be updated to include `android_studio`, noting that the idempotency
impact is weaker for snap-based roles than for apt-based ones.

## Out of Scope

- Android Studio for ARM64, i386, or any architecture other than AMD64.
- Android Studio Beta or Canary channels; only the stable release is in scope.
- Per-user configuration: SDK paths, AVD (emulator) setup, and IDE preferences
  are out of scope. The role performs a system-wide installation only.
- Android SDK component management: downloading or pre-configuring SDK
  platforms, build tools, or emulator images is a separate concern.
- Pinned version installation; the role installs the latest available stable
  release. Version pinning is deferred.
- Android Studio uninstallation or downgrade automation.
