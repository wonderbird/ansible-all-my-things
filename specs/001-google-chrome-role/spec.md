# Feature Specification: Ansible Role — Install Google Chrome (Stable)

**Feature Branch**: `001-google-chrome-role`
**Created**: 2026-03-13
**Status**: Draft
**Input**: User description: "Create an Ansible role `google_chrome` to install Google Chrome (stable) on Ubuntu AMD64 development machines as part of the developer workstation automation project."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Fresh Chrome Installation on AMD64 Workstation (Priority: P1)

A developer runs the workstation automation playbook against a fresh Ubuntu AMD64
machine. After the run completes, Google Chrome (stable) is installed and available
system-wide from the official Google apt repository.

**Why this priority**: This is the primary goal of the feature. All other stories
depend on the installation succeeding correctly.

**Independent Test**: Run the playbook against a clean Ubuntu AMD64 VM with no prior
Chrome configuration. Verify that `google-chrome-stable` is installed and launchable,
and that the Google apt repository is correctly registered with a trusted signing key.

**Acceptance Scenarios**:

1. **Given** a clean Ubuntu AMD64 machine with no Chrome installed, **When** the
   playbook runs, **Then** `google-chrome-stable` is installed, launchable from the
   command line, and the Google apt signing key is present in the system keyring.

2. **Given** the playbook has run successfully, **When** the system's apt package
   index is updated, **Then** Google Chrome updates are delivered automatically via
   the registered Google apt repository.

---

### User Story 2 — Idempotent Re-Run Without Errors (Priority: P2)

A developer re-runs the playbook against a machine that already has Chrome installed.
The run completes without errors, without duplicate apt source entries, and without
redundant changes.

**Why this priority**: Idempotency is a non-negotiable project principle (Constitution
§I). A role that causes apt source conflicts or errors on the second run is broken.

**Independent Test**: Run the playbook twice consecutively against the same AMD64 VM.
The second run must report zero changed tasks and zero failed tasks related to this
role.

**Acceptance Scenarios**:

1. **Given** Chrome is already installed and the Google apt repository is already
   configured, **When** the playbook runs again, **Then** no tasks in the
   `google_chrome` role report a change and no errors occur.

2. **Given** Chrome's post-install process has modified the apt source file created
   by the role (e.g., renamed or reformatted it), **When** the playbook runs again,
   **Then** no duplicate or conflicting apt source entries are created.

---

### User Story 3 — Graceful Skip on Non-AMD64 Machines (Priority: P3)

A developer runs the playbook against an ARM64 machine (e.g., a Vagrant VM on Apple
Silicon). The `google_chrome` role tasks are skipped without errors because Chrome is
not available for that architecture.

**Why this priority**: The project runs against both AMD64 cloud machines and ARM64
local VMs. The role must not break ARM64 runs.

**Independent Test**: Run the playbook against an ARM64 Vagrant VM. Verify that all
tasks in the `google_chrome` role are skipped and the playbook completes successfully.

**Acceptance Scenarios**:

1. **Given** the target machine is ARM64, **When** the playbook runs, **Then** all
   `google_chrome` role tasks are skipped with the `not-supported-on-vagrant-arm64`
   tag and no errors are reported.

---

### Edge Cases

- Chrome previously installed via a manually downloaded `.deb` leaving a conflicting
  apt source entry is **out of scope** — the operator must remove such entries before
  running the playbook.
- What happens if the Google signing key URL is unreachable during the playbook run?
- How does Chrome's own post-install script interact with the apt source file created
  by the role, and does that interaction cause conflicts on subsequent runs?
- What happens if the Google signing key already exists in the system keyring from a
  prior manual installation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The role MUST install the `google-chrome-stable` package on AMD64 machines
  using the official Google apt repository at `https://dl-ssl.google.com/linux/chrome/deb/`.

- **FR-002**: The role MUST register the Google apt repository using the official signing
  key from `https://dl-ssl.google.com/linux/linux_signing_key.pub`, stored securely in
  the system-wide keyring directory.

- **FR-003**: The role MUST guard apt repository registration against Chrome's
  post-install behaviour. Chrome's installer is known to modify or rename apt source
  files after package installation. The exact behaviour MUST be researched during
  planning and the role MUST avoid creating duplicate or conflicting apt source entries
  on re-runs regardless of that behaviour.

- **FR-004**: All tasks in the role MUST carry the tag `not-supported-on-vagrant-arm64`
  so they are skipped on ARM64 hosts.

- **FR-005**: The role MUST execute only on AMD64 hosts. The architecture guard is
  the tag-based skip mechanism: every task in the role carries the
  `not-supported-on-vagrant-arm64` tag (see FR-004), and the role entry in
  `configure-linux-roles.yml` also carries that tag so that
  `--skip-tags not-supported-on-vagrant-arm64` skips all role tasks at once. No
  separate assert task is used. This is consistent with the pattern established in
  `playbooks/setup-homebrew.yml`.

- **FR-006**: The installation MUST be system-wide. No per-user Chrome configuration
  is performed by this role.

- **FR-007**: The role MUST be added to `configure-linux-roles.yml` so it is applied
  as part of the standard developer workstation automation.

- **FR-008**: The role MUST be placed at `roles/google_chrome/` using standard Ansible
  role directory structure.

- **FR-009**: The role MUST follow the same pattern for signing key handling, apt
  source configuration, and idempotency guards established in
  `playbooks/tasks/setup-vscode.yml`.

### Key Entities

- **Google Chrome Stable**: The target software package, identified as
  `google-chrome-stable` in the Google apt repository.
- **Google Apt Signing Key**: The GPG key published at
  `https://dl-ssl.google.com/linux/linux_signing_key.pub`, used to authenticate
  packages from the Google apt repository.
- **Google Apt Repository**: The Debian package repository at
  `https://dl-ssl.google.com/linux/chrome/deb/`, providing `google-chrome-stable`.
- **Apt Source File**: The file written to `/etc/apt/sources.list.d/` that registers
  the Google repository. Its exact name and format after Chrome's post-install
  modification must be determined during planning research.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a single playbook run against a clean AMD64 workstation,
  Google Chrome is installed and launchable without any manual intervention.

- **SC-002**: A second consecutive playbook run against the same machine reports
  zero changes and zero failures for all tasks in the `google_chrome` role.

- **SC-003**: Running the playbook against an ARM64 machine completes without
  errors, with all `google_chrome` role tasks skipped.

- **SC-004**: The Google apt repository remains correctly registered and functional
  after Chrome's post-install process has run, so that future system updates deliver
  Chrome updates automatically.

## Assumptions

- The target OS is Ubuntu Linux (the project's primary guest OS per the constitution).
- Only AMD64 architecture is in scope; ARM64 and other architectures are explicitly
  out of scope for this role.
- No per-user Chrome preferences, extensions, or policies are required; system-wide
  package installation is sufficient.
- The latest available `google-chrome-stable` package is acceptable. Pinned versions
  are deferred — see Technical Debt section.

## Technical Debt

A new entry must be added to `docs/architecture/technical-debt/technical-debt.md`
covering all package installation roles in the project, not only `google_chrome`.

**Architecture guard inconsistency across roles**: The `google_chrome` role uses the
tag-based skip mechanism (`not-supported-on-vagrant-arm64`) as its sole architecture
guard, matching the `setup-homebrew.yml` pattern. The `claude_code` role uses a hard
assert task instead. These two approaches are inconsistent: the tag-based approach
silently skips on wrong architectures (only effective when the operator uses the skip
tag), while the assert approach fails loudly regardless. A future consolidation should
pick one pattern and apply it uniformly across all architecture-constrained roles.

All package installation roles (including `google_chrome`, `cursor_ide`, and
`claude_code`) install the **latest available** version of each package rather than a
pinned version. This means re-running the playbook after a new upstream release will
install a different package version than a previous run, which technically violates the
idempotency principle (Constitution §I) at the package-version level. The risk is
accepted for developer workstation tooling, where staying current outweighs strict
version pinning, but it should be revisited if version consistency across a fleet of
machines becomes a requirement.

## Clarifications

### Session 2026-03-13

- Q: When the playbook runs on a non-AMD64 machine without the skip tag applied, should the architecture guard cause a hard failure or silently skip via tags? → A: Tag-based skip only — every task carries `not-supported-on-vagrant-arm64` and the role entry in `configure-linux-roles.yml` is also tagged, matching the `setup-homebrew.yml` pattern. No assert task. NOTE: this deviates from the `claude_code` role, which uses a hard assert; that deviation must be documented as technical debt during implementation.
- Q: Should the role handle machines where Chrome was previously installed via a manually downloaded `.deb`, leaving a conflicting apt source entry? → A: Out of scope — operator must remove conflicting manually created apt source entries before running the playbook.

## Out of Scope

- Google Chrome for ARM64, i386, or any architecture other than AMD64.
- Per-user Chrome configuration, policies, or extension management.
- Google Chrome Beta or Unstable channels.
- Pinned Chrome version installation.
- Chrome uninstallation or downgrade automation.
- Cleanup of apt source entries created by a prior manual `.deb` installation.
