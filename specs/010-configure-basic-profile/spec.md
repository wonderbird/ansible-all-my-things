# Feature Specification: Configure Basic Profile for Tart VMs

**Feature Branch**: `010-configure-basic-profile`
**Created**: 2026-06-10
**Status**: Implemented

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bring a fresh tart VM to a baseline (Priority: P1)

An operator has just created a new tart Linux VM with `create-vm.yml`. The VM
is in its bare cloud-image state: it has only a default pre-existing account,
no configured users, default packages, default timezone, and no development
tooling. The operator runs `configure-profile.yml` against the `tart`
inventory group with no extra-vars. The playbook sets up user accounts and SSH
access, brings the OS packages and timezone to the project's standard, installs
the Node.js toolchain for desktop users, installs and configures the standard
set of development tool roles, and reboots the VM if required — leaving the VM
ready for development work.

**Why this priority**: This is the entire feature. Without it, every
freshly-created VM requires manual, error-prone setup before it can be used.

**Independent Test**: Run `create-vm.yml` to create a new tart VM, then run
`configure-profile.yml` against the `tart` group with no extra-vars.
Verify the operator can SSH in as `my_ansible_user` and as each configured
desktop user using their SSH key (no password), and that podman, ruby,
python, the Dolt SQL server, and the Claude Code CLI are all available.

**Acceptance Scenarios**:

1. **Given** a freshly created tart VM reachable only via its default
   pre-existing account, **When** `configure-profile.yml` runs against
   the `tart` group with no extra-vars, **Then** the playbook completes
   successfully and `my_ansible_user` and all `desktop_users` exist as members
   of the sudo group, each with their SSH public key installed for passwordless
   login.
2. **Given** a VM configured by Scenario 1, **When** an operator attempts to
   SSH in using a password, **Then** the connection is rejected because SSH
   password authentication is disabled.
3. **Given** a VM configured by Scenario 1, **When** an operator inspects the
   package cache and installed packages, **Then** the package cache is
   up to date, all packages are at their latest available versions, and the
   system timezone is `Europe/Berlin`.
4. **Given** a VM configured by Scenario 1, **When** an operator logs in as a
   desktop user, **Then** a Node Version Manager is available, the current
   Node.js LTS release is installed and set as the default, and the global npm
   CLI tools `eslint`, `markdownlint-cli`, `prettier`, and `typescript` are
   installed and runnable.
5. **Given** a VM configured by Scenario 1, **When** an operator inspects the
   VM, **Then** the container runtime (podman), Ruby, Python, the Dolt SQL
   server, and the Claude Code CLI are all installed and configured.
6. **Given** a VM configured by Scenario 1 where the OS reports a pending
   reboot is required (e.g. after a kernel update), **When**
   `configure-profile.yml` runs, **Then** the VM reboots and the
   playbook waits for it to come back online before completing successfully.

---

### User Story 2 - Re-running the playbook is a no-op (Priority: P2)

An operator has already run `configure-profile.yml` successfully once
against a tart VM. They run it again — for example, to confirm the VM's
configuration still matches the desired baseline, or because they are unsure
whether the first run completed. The second run reports that nothing changed.

**Why this priority**: Idempotency is required by the project constitution and
is essential for operator confidence: re-running the playbook must be safe and
side-effect-free, so it can be used as a routine "make sure the VM is in the
right state" check.

**Independent Test**: After completing User Story 1's scenario, run
`configure-profile.yml` again against the same VM with no extra-vars and
verify the run reports no changes to any task.

**Acceptance Scenarios**:

1. **Given** a tart VM already configured by a successful run of
   `configure-profile.yml`, **When** the playbook is run again with no
   extra-vars, **Then** every task reports no change and the playbook
   completes successfully.

---

### Edge Cases

- What happens if `configure-profile.yml` is run against a VM that was
  never processed by `create-vm.yml` (e.g. a VM that already has
  `my_ansible_user` configured, but not via the default bootstrap account)?
  The playbook is expected to be run against tart-group VMs in their
  post-`create-vm.yml` state; behavior against VMs in other states is
  out of scope for this feature.
- What happens if the OS does not require a reboot at the end of the run? The
  playbook completes without rebooting.
- What happens if a desktop user's home directory or shell configuration
  already contains a `.bashrc`-loading block from a previous run? The block is
  not duplicated (idempotent).
- What happens if the Node.js LTS release or global npm tool versions change
  between runs (e.g. a new Node.js LTS is released upstream)? Re-running the
  playbook on an already-configured VM does not attempt to upgrade an
  already-installed Node.js LTS or already-installed global npm tools to a
  newer version; it only ensures they are present. Keeping these up to date on
  existing VMs is out of scope for this feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a single playbook,
  `configure-profile.yml`, runnable against the `tart` inventory group
  with no extra-vars required for the common case.
- **FR-002**: The system MUST be able to connect to a freshly created tart VM
  using its pre-existing default account (which exists before
  `my_ansible_user` is created), and this default account name MUST be
  configurable per inventory group via group variables, consistent with how
  other platforms (e.g. AWS, Hetzner) already configure their respective
  default bootstrap accounts. For the `tart` inventory group, this default
  account name MUST be `"admin"`.
- **FR-003**: The system MUST ensure the configured admin user
  (`my_ansible_user`) and all configured desktop users (`desktop_users`) exist
  on the VM as members of the sudo group.
- **FR-004**: The system MUST grant `my_ansible_user` passwordless sudo
  access.
- **FR-005**: The system MUST install each configured user's SSH public key so
  that user can log in via SSH without a password.
- **FR-006**: The system MUST disable SSH password authentication on the VM.
- **FR-007**: The system MUST configure each configured user's `.bash_profile`
  to load `.bashrc` on login.
- **FR-008**: The system MUST refresh the OS package cache and upgrade all
  installed packages to their latest available versions.
- **FR-009**: The system MUST set the VM's system timezone to `Europe/Berlin`.
- **FR-010**: The system MUST install a Node Version Manager for each
  configured desktop user.
- **FR-011**: The system MUST install the current Node.js LTS release for each
  configured desktop user and set it as that user's default Node.js version.
- **FR-012**: The system MUST install the following global npm CLI tools for
  each configured desktop user: `eslint`, `markdownlint-cli`, `prettier`, and
  `typescript`.
- **FR-013**: The system MUST install and configure a container runtime
  (podman) on the VM.
- **FR-014**: The system MUST install and configure Ruby on the VM.
- **FR-015**: The system MUST install and configure Python on the VM.
- **FR-016**: The system MUST install and configure a Dolt SQL server on the
  VM.
- **FR-017**: The system MUST install and configure the Claude Code CLI on the
  VM.
- **FR-018**: The system MUST NOT install tmux or any desktop-only tooling
  (e.g. a browser) as part of this profile.
- **FR-019**: The system MUST check, at the end of the run, whether the OS
  requires a reboot (e.g. after a kernel update) and, if so, reboot the VM and
  wait for it to come back online before the playbook completes
  successfully. If no reboot is required, the playbook completes without
  rebooting.
- **FR-020**: Every task performed by `configure-profile.yml` MUST be
  idempotent: running the playbook again against an already-configured VM MUST
  report no further changes.
- **FR-021**: The system MUST NOT require any new Ansible Galaxy collections
  beyond those already used by the project.

### Key Entities

- **Default Bootstrap Account**: The pre-existing account on a freshly
  provisioned VM, used to connect before `my_ansible_user` exists. Its name is
  a per-inventory-group configuration value (`"admin"` for the `tart` group).
- **Admin User (`my_ansible_user`)**: The primary configured account used for
  ongoing administration of the VM; gains sudo group membership and
  passwordless sudo.
- **Desktop User (`desktop_users`)**: One or more configured user accounts that
  receive sudo group membership, SSH key access, and the Node.js toolchain.
- **Development Tool Role**: One of five standalone capabilities installed and
  configured on the VM as part of this profile — container runtime (podman),
  Ruby, Python, Dolt SQL server, Claude Code CLI.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An operator brings a freshly created tart VM to a fully
  configured, development-ready baseline with a single command and no
  extra-vars.
- **SC-002**: After one successful run of `configure-profile.yml`, all
  configured users (`my_ansible_user` and every `desktop_users` entry) can log
  in to the VM via SSH using their key, with no password prompt, and SSH
  password authentication is rejected.
- **SC-003**: After one successful run, the VM's package cache is current, all
  packages are upgraded, and the system timezone reads `Europe/Berlin`.
- **SC-004**: After one successful run, every configured desktop user has a
  working Node.js LTS environment with `eslint`, `markdownlint-cli`,
  `prettier`, and `typescript` available as global commands.
- **SC-005**: After one successful run, podman, Ruby, Python, the Dolt SQL
  server, and the Claude Code CLI are all installed and configured on the VM.
- **SC-006**: A second run of `configure-profile.yml` against the same
  VM, with no extra-vars, reports zero changed tasks.

## Assumptions

- `configure-profile.yml` is run manually as the second step of a
  two-step workflow (`create-vm.yml` then `configure-profile.yml`)
  against VMs in the `tart` inventory group, in the state `create-vm.yml`
  leaves them in (default account only, no `my_ansible_user` yet).
- The default bootstrap account name for the `tart` inventory group is
  `"admin"`, matching the credentials `create-vm.yml` registers in
  `inventories/tart_autogenerated.yml`.
- "Current Node.js LTS release" means whatever release the project's chosen
  Node Version Manager identifies as the active LTS at the time the playbook
  runs; the playbook does not pin a specific Node.js version number in its
  requirements.
- The fixed set of global npm CLI tools (`eslint`, `markdownlint-cli`,
  `prettier`, `typescript`) reflects current frequently-used tooling and may be
  revisited in future features; changing this set is out of scope here.
- tmux and desktop-only tools (e.g. a browser) are explicitly excluded from
  this profile because their full functionality (e.g. terminal "nerd fonts")
  depends on a desktop environment that a tart VM does not have.
- No new Ansible Galaxy collections are introduced by this feature.
