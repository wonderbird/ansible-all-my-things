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

### User Story 4 - SDK Pre-Provisioned at First Launch (Priority: P2)

A developer provisions a virtual machine using this Ansible project. When
they launch Android Studio for the first time, the first-launch setup wizard
completes quickly — within 30 seconds — because all required SDK components
are already present on the machine.

**Why this priority**: Without SDK pre-provisioning, the wizard triggers
large downloads that can take 10–30 minutes, blocking the developer from
starting work. Pre-provisioning eliminates this wait.

**Independent Test**: On a freshly provisioned VM, launch Android Studio and
step through the Standard setup wizard. Measure time from wizard start to
completion.

**Acceptance Scenarios**:

1. **Given** a freshly provisioned VM, **When** Android Studio is launched
   for the first time and the Standard setup wizard is followed, **Then** the
   wizard completes within 30 seconds, indicating no major downloads are
   pending.
2. **Given** a VM where SDK pre-provisioning has already run, **When** the
   playbook runs again, **Then** the SDK pre-provisioning tasks report `ok`
   or `skipped`, never `changed`.
3. **Given** the target machine is ARM64, **When** the playbook runs,
   **Then** all SDK pre-provisioning tasks are also skipped (consistent with
   User Story 3).

---

### Edge Cases

- If an older version of Android Studio is already installed, the role takes
  no action; upgrades are handled by snapd's automatic refresh mechanism.
- If network access is unavailable during provisioning, the snap install
  fails and the playbook aborts with an error. No special handling is
  performed.
- If network access is unavailable during SDK pre-provisioning, the
  playbook aborts with an error. No special handling is performed
  (consistent with the snap-install network-failure edge case).
- If disk space is insufficient, the snap install or SDK download fails and
  the playbook aborts with an error. No special handling is performed.

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
- **FR-009**: The role MUST pre-provision the Android SDK for every user
  listed in `desktop_user_names` so that the Android Studio first-launch
  wizard requires no additional downloads.
- **FR-010**: The SDK components to pre-provision are those the Standard
  setup wizard would download: platform tools, the latest stable SDK
  platform, matching build tools, the emulator binary, and platform sources.
  Emulator system images are excluded; they are downloaded on-demand when
  the user creates a virtual device (AVD).
- **FR-011**: The role MUST always install the latest stable SDK components
  available at provisioning time. SDK version pinning is out of scope.
- **FR-012**: SDK pre-provisioning MUST be idempotent: re-running the role
  on a machine where the SDK is already present MUST produce no `changed`
  tasks.

### Key Entities

- **Ansible Role (`android_studio`)**: A self-contained unit of Ansible
  automation placed under `roles/android_studio/` that encapsulates all
  tasks, files, templates, and variables needed to install Android Studio.
- **`configure-linux.yml`**: The top-level playbook that orchestrates all
  provisioning steps by importing sub-playbooks including
  `configure-linux-roles.yml`.
- **`configure-linux-roles.yml`**: The roles playbook where the
  `android_studio` role entry will be added, consistent with existing roles.
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
- **SC-005**: A manual test on a freshly provisioned VM shows that the
  Android Studio first-launch wizard (Standard setup) completes within
  30 seconds, indicating no major downloads are pending.

## Clarifications

### Session 2026-04-03

- Q: What SDK components must be pre-provisioned so that the first-launch
  wizard has nothing significant left to download? → A: Exactly the
  components the Standard setup wizard would download: platform-tools, the
  latest stable SDK platform, matching build tools, the emulator binary, and
  platform sources. System images are out of scope — downloaded on-demand
  when the user creates a virtual device (AVD).
- Q: Should emulator system images be included? → A: No — see above.
- Q: What is the acceptance criterion for SDK pre-provisioning? → A: A
  manual test showing that the first-launch wizard completes within
  30 seconds, used as an indicator that no major downloads are pending.
- Q: Should the SDK version be pinned? → A: No. The role always installs
  the latest stable SDK components available at provisioning time.
- Q: Where is `desktop_user_names` defined? → A: In `group_vars/` or
  `host_vars/` for the target host. The role iterates over this list
  but does not define or validate it.
- Q: How is the matching build-tools version determined? → A: The role
  installs the latest available build-tools version; it does not
  attempt to match the build-tools version to the platform API level.
- Q: How are cmdline-tools acquired? → A: The download URL contains a
  build number that changes per release. The build number and SHA-256
  checksum are exposed as role variables in `defaults/main.yml` and
  bumped manually when a new version is needed. Both values are listed
  at
  <https://developer.android.com/studio/index.html#command-line-tools-only>.

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
  runtime); no separate dependency installation is needed for the IDE itself.
- SDK pre-provisioning downloads components from Google's servers during
  provisioning; outbound internet access is required.
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
- IDE preferences and per-user IDE configuration are out of scope.
- AVD (emulator) creation and system image downloads are out of scope.
  System images are downloaded on-demand when the user creates a virtual
  device through Android Studio.
- Pinned version installation; the role installs the latest available stable
  release. Version pinning is deferred.
- Android Studio uninstallation or downgrade automation.
