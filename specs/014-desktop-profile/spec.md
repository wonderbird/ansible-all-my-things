# Feature Specification: Desktop Profile for Create and Destroy VM Playbooks

**Feature Branch**: `014-desktop-profile`

**Created**: 2026-06-20

**Status**: Draft

**Input**: User description: "Desktop profile for create-vm.yml / configure-profile.yml (Roadmap Phase 5a). Add `desktop` as a selectable `profile` value; register a `desktop` inventory group; verbatim-import the legacy desktop playbooks (`configure-linux-roles.yml`'s role list, `setup-desktop.yml`, `setup-keyring.yml`, `setup-desktop-apps.yml`) under a logged Principle II exception; reject `provider=docker profile=desktop`; condition the AWS RDP (3389) rule on `profile==desktop`; scope the `basic` profile to its own inventory group first so `basic` and `desktop` never share one mutable role list. Out of scope: `setup-homebrew.yml`, `restore.yml` porting, real role extraction from the legacy desktop playbooks, podman provider, Phase 6 legacy retirement."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a desktop-profile VM (Priority: P1)

An engineer wants a VM with a full desktop environment — not the headless
`basic` profile — provisioned through the same unified commands used for
every other VM. They run `create-vm.yml -e profile=desktop` (with any
provider except `docker`, which is rejected — see User Story 2). The system
creates the VM, registers it in a `desktop` inventory group distinct from
`basic`, and configuring it installs the full desktop stack (display
manager, desktop environment, keyring, desktop apps) instead of the basic
headless role set.

**Why this priority**: This is the core value of the feature — it is the
only thing today's stack cannot do through `create-vm.yml`/
`configure-profile.yml` at all. Every current target lacking a desktop
environment must instead go through the legacy `provision.yml` →
`configure-linux.yml` path, which `create-vm.yml` was meant to replace.

**Independent Test**: Run `create-vm.yml -e provider=tart -e profile=desktop`
followed by `configure-profile.yml` against the new host. Verify the host
lands in the `desktop` inventory group (not `basic`) and ends up with a
working desktop environment, keyring, and desktop apps installed.

**Acceptance Scenarios**:

1. **Given** an engineer requests `profile=desktop` with a non-`docker`
   provider, **When** `create-vm.yml` runs, **Then** the new VM is registered
   in the `desktop` inventory group (never `basic`).
2. **Given** a VM registered in the `desktop` group, **When**
   `configure-profile-roles.yml` runs against it, **Then** it receives the
   full legacy desktop role list (the same roles `configure-linux-roles.yml`
   would have applied), not the `basic` profile's role list.
3. **Given** a VM registered in the `desktop` group, **When**
   `configure-profile.yml` runs against it, **Then** it additionally receives
   `setup-desktop.yml`, `setup-keyring.yml`, and `setup-desktop-apps.yml`,
   imported unchanged from the legacy stack.

---

### User Story 2 - Block an unsupported provider/profile combination loudly (Priority: P2)

An engineer mistakenly requests a desktop VM on the `docker` provider, which
cannot support a desktop environment (the minimized docker image used for
the `docker` provider was always built without desktop support — a
pre-existing, deliberate limitation). Instead of starting a long-running
provisioning step and failing confusingly partway through, the command
refuses immediately with an explicit, actionable error, and no infrastructure
action (no container, no inventory write) occurs.

**Why this priority**: Without this guard, the only way an engineer
discovers the incompatibility is a failed mid-provisioning task with no clear
cause — the kind of silent/confusing failure Constitution Principle XII
exists to prevent. It is cheap to add and protects every engineer who
guesses wrong about provider/profile compatibility.

**Independent Test**: Run
`create-vm.yml -e provider=docker -e profile=desktop`. Verify the command
fails immediately, before any container is created or inventory file is
touched, with a message naming both `provider=docker` and `profile=desktop`
as the incompatible combination.

**Acceptance Scenarios**:

1. **Given** `provider=docker` and `profile=desktop` are both requested,
   **When** `create-vm.yml` runs, **Then** it fails immediately with an
   explicit error naming the incompatible combination, before any container
   is created.
2. **Given** any other provider (`tart`, `hcloud`, `aws`) with
   `profile=desktop`, **When** `create-vm.yml` runs, **Then** it proceeds
   normally (no rejection).

---

### User Story 3 - Desktop VMs on AWS get RDP access without exposing it on basic VMs (Priority: P3)

An engineer creates a desktop-profile VM on AWS and needs to reach it over
RDP. At the same time, every existing `basic`-profile AWS VM must keep
exposing only SSH (port 22) — the desktop feature must not silently widen
the network exposure of unrelated, already-running basic VMs that share the
same security group.

**Why this priority**: Lowest priority of the three because it only applies
to one provider (AWS) and is a refinement of User Story 1's AWS path, not a
new capability on its own — but it is a real security boundary that must
hold from day one of the desktop profile shipping, not as a later patch.

**Independent Test**: Create one `basic`-profile and one `desktop`-profile VM
on AWS sharing the same security group. Verify the desktop VM's security
group allows inbound 3389; verify the basic VM's security group does not.

**Acceptance Scenarios**:

1. **Given** `provider=aws` and `profile=desktop`, **When** `create-vm.yml`
   runs, **Then** the security group used by the new VM allows inbound TCP
   3389, in addition to the existing TCP 22 rule.
2. **Given** `provider=aws` and `profile=basic`, **When** `create-vm.yml`
   runs (before or after a desktop VM has been created), **Then** the
   security group used by that VM allows only TCP 22 — never TCP 3389 — even
   though basic and desktop VMs share the same `ansible-sg` security group
   today.

---

### Edge Cases

- What happens when `profile=desktop` is requested with the existing
  `basic`-only inventory plumbing still in place? Out of order: the `basic`
  profile must already be scoped to its own inventory group before the
  `desktop` group is introduced, so the two profiles never apply roles to
  the same host.
- What happens to `setup-homebrew.yml`, part of the legacy desktop stack?
  Dropped entirely — not ported, not imported, not referenced. (Pre-existing
  decision: arm64-unsupported, low value.)
- What happens to `restore.yml` (the legacy backup/settings restore step)?
  Not ported by this feature. It is deferred to immediately before the
  legacy stack's eventual retirement, proven via its own
  backup → destroy → create → restore round-trip first.
- What happens to the legacy desktop playbooks
  (`setup-desktop.yml`/`setup-keyring.yml`/`setup-desktop-apps.yml`)
  themselves? They are imported **verbatim**, unmodified, and not extracted
  into standalone roles by this feature — an explicitly accepted, logged
  exception to the project's normal role-first rule, since extracting them
  properly is large enough to be its own follow-up.
- What happens to `provision.yml`/`destroy.yml`/`provisioners/` (the legacy
  entrypoints these desktop playbooks are imported from)? Unchanged, not
  removed — they remain the fallback path until a later phase proves full
  parity and retires them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `create-vm.yml` MUST accept a new `profile` extra-var with
  values `basic` (default) and `desktop`. No such extra-var exists today —
  `create-vm.yml` has no `profile` parameter at all, and
  `configure-profile-roles.yml`/`configure-profile.yml` unconditionally apply
  one fixed role list to `hosts: linux` (the de facto, but unnamed, "basic"
  behavior). This feature introduces the `profile` mechanism itself, not a
  second branch of an existing one.
- **FR-002**: When `profile=desktop`, `create-vm.yml` MUST register the new
  VM in a `desktop` inventory group, distinct from the `basic` group used by
  `profile=basic`.
- **FR-003**: Before the `desktop` group is introduced, `configure-profile-roles.yml`
  and `configure-profile.yml` MUST be scoped to the `basic` inventory group
  (not the broader `linux` group they target today), confirmed
  behavior-preserving against every current target. This MUST land first so
  `basic` and `desktop` never apply roles to the same host via one shared,
  mutable role list.
- **FR-004**: `configure-profile-roles.yml` MUST gain a `profile=desktop`
  branch that imports the existing legacy `configure-linux-roles.yml` role
  list **verbatim** (unmodified) for hosts in the `desktop` group.
- **FR-005**: `configure-profile.yml` MUST gain a `profile=desktop` branch
  that additionally imports `setup-desktop.yml`, `setup-keyring.yml`, and
  `setup-desktop-apps.yml` **verbatim** (unmodified) for hosts in the
  `desktop` group.
- **FR-006**: `create-vm.yml` MUST reject the combination
  `provider=docker` with `profile=desktop` immediately, with an explicit
  error naming both values, before any container is created or inventory
  entry written.
- **FR-007**: When `provider=aws` and `profile=desktop`, the AWS security
  group used by the new VM MUST allow inbound TCP 3389, added as an
  additional rule alongside the existing TCP 22 rule.
- **FR-008**: The TCP 3389 rule from FR-007 MUST be conditioned on
  `profile==desktop` and MUST NOT be applied when creating a `basic`-profile
  AWS VM, even though basic and desktop VMs share one AWS security group
  today.
- **FR-009**: This feature MUST NOT port, reference, or import
  `setup-homebrew.yml` in any profile branch.
- **FR-010**: This feature MUST NOT port `restore.yml` or any of its
  functionality.
- **FR-011**: This feature MUST NOT extract `setup-desktop.yml`,
  `setup-keyring.yml`, or `setup-desktop-apps.yml` into standalone Ansible
  roles. The verbatim-import approach is an explicitly accepted exception to
  the project's normal role-first rule (Constitution Principle II) and MUST
  be logged in this feature's `plan.md` Complexity Tracking table before
  implementation of the desktop branches (FR-004, FR-005) begins.
- **FR-012**: This feature MUST NOT modify the behavior, output, or files
  touched by `create-vm.yml`/`destroy-vm.yml`/`configure-profile.yml`/
  `configure-profile-roles.yml` when `profile=basic` is requested, other than
  the group-scoping change in FR-003 (which MUST be behavior-preserving).

### Key Entities

- **Profile**: The `profile` extra-var on `create-vm.yml`, now carrying two
  live values, `basic` and `desktop`, each mapped to its own inventory group
  and its own role/playbook set.
- **Desktop Inventory Group**: A new inventory group holding VMs created
  with `profile=desktop`, configured by the desktop branches of
  `configure-profile-roles.yml` and `configure-profile.yml`.
- **AWS Desktop Security Rule**: The TCP 3389 (RDP) ingress rule, applied
  only to AWS VMs created with `profile=desktop`, additive to the existing
  TCP 22 rule on the shared `ansible-sg` security group.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An engineer provisions a working desktop VM (any provider
  except `docker`) with the same single-command shape already used for
  `basic` VMs (`create-vm.yml -e profile=desktop` then
  `configure-profile.yml`).
- **SC-002**: 100% of `provider=docker profile=desktop` attempts fail
  immediately with an explicit, actionable error, before any container is
  created.
- **SC-003**: Zero basic-profile AWS VMs gain inbound RDP (3389) access as a
  side effect of this feature shipping.
- **SC-004**: Every existing `basic`-profile target continues to behave
  identically (same roles applied, same files touched) after the group-scope
  change (FR-003) lands.
- **SC-005**: The Principle II exception for verbatim-importing the legacy
  desktop playbooks is recorded in this feature's `plan.md` Complexity
  Tracking table before any desktop-branch implementation code is merged.

## Assumptions

- Every current target of `configure-profile-roles.yml`/`configure-profile.yml`
  is already a member of the `basic` inventory group, so scoping those plays
  to `hosts: basic` (FR-003) is behavior-preserving and requires no inventory
  changes beyond the scoping itself.
- No `profile` extra-var or `basic` inventory group exists in the codebase
  today (verified by grep); `configure-profile-roles.yml` currently targets
  `hosts: linux` unconditionally. FR-003's group-scoping change and FR-001's
  `profile` extra-var are both net-new, not refinements of existing code.
- The `docker` provider's incompatibility with a desktop environment is a
  pre-existing, deliberate limitation (already documented by the
  `not-supported-on-vagrant-docker` tag on the legacy desktop playbooks), not
  a new restriction introduced by this feature.
- Real role extraction from `setup-desktop.yml`, `setup-keyring.yml`, and
  `setup-desktop-apps.yml` is valuable future work but is explicitly deferred
  to a separate follow-up, not part of this feature's scope.
- `restore.yml` porting requires its own proof (a backup → destroy → create →
  restore round-trip) and is deferred to immediately before the legacy
  stack's eventual retirement, not bundled into this feature.
- The shared `ansible-sg` AWS security group (used by both basic and desktop
  VMs today) is reused as-is; this feature does not introduce a separate
  security group per profile.
