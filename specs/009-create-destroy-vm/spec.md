# Feature Specification: Create and Destroy VM Playbooks

**Feature Branch**: `009-create-destroy-vm`
**Created**: 2026-06-06
**Status**: Draft
**Input**: `docs/feature-requests/feat.create-destroy-vm/prd.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create New VM (Priority: P1)

An engineer wants to spin up a fresh Linux VM for testing or development.
They run a single command, optionally specifying a profile and provider.
The system picks the next unused hostname from the ordered pool, creates
the VM, places it in the correct inventory group, and reports the hostname
on completion.

**Why this priority**: Core value. Without VM creation nothing else in the
feature matters. All other stories depend on VMs existing.

**Independent Test**: Run `create-vm.yml` with no extra-vars. The command
completes, prints a hostname, and the VM is reachable via SSH.

**Acceptance Scenarios**:

1. **Given** the hostname pool has unused entries, **When** `create-vm.yml`
   runs with no extra-vars, **Then** a new VM is created with the default
   provider (`tart`) and default profile (`basic`), the next unused
   hostname from the pool is assigned, the VM is registered in inventory
   under the `basic` group, and the hostname is printed on completion.
2. **Given** `provider=hcloud` is specified, **When** `create-vm.yml` runs
   with `profile=basic provider=hcloud`, **Then** a VM is created on
   Hetzner Cloud with the next unused pool hostname, and it appears in
   inventory under the `hcloud` and `basic` groups.
3. **Given** one VM already exists, **When** `create-vm.yml` runs again,
   **Then** a second VM is created with the next unused hostname, and both
   VMs coexist in inventory.
4. **Given** `profile=desktop`, **When** `create-vm.yml` runs, **Then**
   the new VM is placed in the `desktop` inventory group using the next
   unused hostname from the pool.

---

### User Story 2 - Destroy VM by Hostname (Priority: P2)

An engineer is done with a VM and wants to remove it cleanly. They run a
single command specifying the hostname. The VM is deleted from the provider
and removed from inventory, leaving no dangling entries.

**Why this priority**: Symmetrical to creation. Lifecycle management is
incomplete without clean teardown. Dangling VMs accumulate cost and stale
inventory entries cause confusion.

**Independent Test**: Given a running VM `edoras`, run `destroy-vm.yml`
with `hostname=edoras`. Verify the VM no longer exists on the provider
and `edoras` is absent from inventory.

**Acceptance Scenarios**:

1. **Given** a VM `edoras` exists in inventory, **When** `destroy-vm.yml`
   runs with `hostname=edoras`, **Then** the VM is deleted from the
   provider and `edoras` no longer appears in inventory.
2. **Given** `hostname` refers to a local provider VM (tart or docker),
   **When** `destroy-vm.yml` completes, **Then** the static inventory file
   no longer contains that hostname.
3. **Given** a hostname not present in inventory, **When** `destroy-vm.yml`
   runs, **Then** the playbook fails immediately with a clear error message
   identifying the unknown hostname.

---

### User Story 3 - Pool Exhaustion Fails Loud (Priority: P3)

All hostnames in the pool are in use. The engineer attempts to create
another VM. The system refuses immediately with an error that names the
exhausted pool, without making any infrastructure change.

**Why this priority**: Safety guardrail needed before VMs accumulate.
Failure must be explicit and actionable rather than silent or misleading.

**Independent Test**: Exhaust the hostname pool, then attempt VM creation.
The command fails before any provider action, with an error message naming
the pool.

**Acceptance Scenarios**:

1. **Given** all hostnames in the pool are in use, **When** `create-vm.yml`
   runs, **Then** the playbook fails immediately — before any VM or
   provider action — with an error message naming the exhausted pool.

---

### User Story 4 - Provider-Encoded Hostnames (Priority: P4)

An engineer glancing at inventory can identify which provider hosts a VM
from its hostname alone, without consulting documentation or filtering by
group.

**Why this priority**: Cosmetic quality of life. Infrastructure functions
correctly without it; delivered last.

**Independent Test**: Create one VM per provider. Read the four hostnames.
Without any other context, confirm each hostname's LOTR region maps
unambiguously to exactly one provider.

**Acceptance Scenarios**:

1. **Given** VMs exist across multiple providers, **When** an engineer
   lists hostnames, **Then** each hostname's LOTR region maps unambiguously
   to exactly one provider (North-West → hcloud, North-East → aws,
   Middle/South-West → tart or docker).
2. **Given** the pool contains the existing names as its first five
   entries, **When** new VMs are created, **Then** the next hostname is
   the next unused entry in the ordered pool.

---

### User Story 5 - Configure VMs by Profile (Priority: P5)

An engineer who has created one or more VMs wants to apply the appropriate
software configuration. They run a single command that targets all
inventory hosts by default, or a subset via the standard `--limit` flag.

**Why this priority**: Completes the create → configure lifecycle. Depends
on VM creation (P1) and inventory group placement being in place.

**Independent Test**: Create a VM with `profile=desktop`, then run
`configure.yml`. Verify the VM receives the roles associated with the
`desktop` group.

**Acceptance Scenarios**:

1. **Given** one or more VMs are in inventory, **When** `configure.yml`
   runs with no extra flags, **Then** all inventory hosts receive the
   configuration roles appropriate to their profile group.
2. **Given** VMs exist in both `basic` and `desktop` groups, **When**
   `configure.yml` runs with `--limit desktop`, **Then** only hosts in the
   `desktop` group are configured; hosts in `basic` are unchanged.
3. **Given** a single VM `edoras` exists in inventory, **When**
   `configure.yml` runs with `--limit edoras`, **Then** only that host is
   configured.

---

### Edge Cases

- What happens when the provider is unreachable at VM creation time? The
  playbook should fail with a provider-specific error; no hostname is
  consumed from the pool.
- What happens when `destroy-vm.yml` is given a hostname that exists in
  inventory but the VM is already gone from the provider? The playbook
  attempts cleanup, removes the stale inventory entry, and warns the
  engineer.
- What if two operators run `create-vm.yml` concurrently? Pool allocation
  must not assign the same hostname to both.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST create one new VM per `create-vm.yml`
  invocation; it MUST NOT reuse or reprovision an existing VM.
- **FR-002**: `create-vm.yml` MUST accept `profile` (optional: `basic` or
  `desktop`; default `basic`) and `provider` (optional: `tart`, `docker`,
  `hcloud`, `aws`; default `tart`).
- **FR-003**: `destroy-vm.yml` MUST accept `hostname` (required)
  identifying a VM present in inventory.
- **FR-004**: The system MUST draw the VM hostname from a single shared
  ordered list of LOTR place names, regardless of provider or profile.
  Hostnames are assigned sequentially; the next unused entry in the list
  is selected on each invocation.
- **FR-005**: The system MUST register each newly created VM in inventory
  and place it in the group matching its profile (`basic` or `desktop`)
  before `create-vm.yml` completes.
- **FR-006**: For local providers (`tart`, `docker`), the system MUST
  update the static inventory file on both create and destroy.
- **FR-007**: For cloud providers (`hcloud`, `aws`), inventory MUST be
  managed via dynamic inventory integration; no manual file edits are
  required.
- **FR-008**: `create-vm.yml` MUST print the assigned hostname on
  successful completion.
- **FR-009**: When the hostname pool is exhausted, `create-vm.yml` MUST
  fail immediately with an error message naming the exhausted pool, without
  performing any provider or VM action.
- **FR-010**: `destroy-vm.yml` MUST remove the hostname from inventory on
  completion.
- **FR-011**: `destroy-vm.yml` MUST fail with a clear, actionable error if
  the specified hostname is not found in inventory.
- **FR-012**: A new `configure.yml` playbook MUST apply the roles
  appropriate to each host's profile group. It MUST target all inventory
  hosts by default; the standard `--limit` flag restricts execution to a
  named group, hostname, or pattern.
- **FR-013**: The superseded artefacts `provision.yml`, `destroy.yml`, and
  `provisioners/` MUST be deleted once `create-vm.yml`, `destroy-vm.yml`,
  and `configure.yml` demonstrably cover the same use cases and existing
  hosts have been migrated. No existing feature is broken during
  implementation; old and new playbooks coexist until migration is
  complete.
- **FR-014**: User documentation (`docs/user-manual/create-vm.md`) MUST
  document `create-vm.yml`, `destroy-vm.yml`, and `configure.yml`; all
  references to `provision.yml` or `destroy.yml` MUST be removed from
  user-facing documentation.
- **FR-015**: The hostname pool ships with ten ordered LOTR place names.
  The first five entries are the existing hostnames (`hobbiton`,
  `rivendell`, `lorien`, `dagorlad`, `moria`). The pool is extensible:
  operators may append names at any time.

### Key Entities

- **VM Profile**: Determines the inventory group a newly created VM is
  placed into and therefore which configuration roles `configure.yml`
  applies to it. Values: `basic` (console only), `desktop` (desktop
  environment). Profile does not affect hostname selection.
- **Provider**: The platform where the VM is created. Values: `tart`
  (local macOS), `docker` (local Linux), `hcloud` (Hetzner Cloud), `aws`
  (Amazon Web Services).
- **Hostname Pool**: A single shared ordered list of LOTR place names used
  across all providers and profiles. Ships with ten names; the first five
  are the existing hostnames. Entries are either available or in use and
  are allocated sequentially. The list is ordered so that names from
  North-West Eriador correspond to hcloud, North-East Iron Hills to aws,
  and Middle–South-West Rohan–Gondor to tart and docker, enabling
  hostnames to encode provider at a glance.
- **Inventory Entry**: A record of a VM's hostname, connection details,
  and group membership, persisted so automation can target the VM.
  Local-provider entries live in a static file; cloud-provider entries are
  resolved dynamically.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An engineer creates any supported VM type on any provider
  with a single command; no extra-vars are required for the common case
  (basic tart VM).
- **SC-002**: An engineer destroys any VM with a single command specifying
  only the hostname.
- **SC-003**: An engineer applies profile-appropriate configuration to any
  set of VMs with a single command, optionally restricted to a group or
  hostname via `--limit`.
- **SC-004**: Every hostname visible in inventory identifies its provider
  at a glance without consulting external documentation.
- **SC-005**: Pool exhaustion is detected and reported before any
  infrastructure change is attempted, with an error message naming the
  depleted pool.
- **SC-006**: No references to `provision.yml` or `destroy.yml` remain in
  user-facing documentation or scripts after delivery.
- **SC-007**: Concurrent VM creation never assigns the same hostname to two
  VMs.

## Assumptions

- The hostname pool ships with ten names. The first five are the existing
  hostnames; five additional LOTR names consistent with their geographic
  region are chosen during planning.
- The tart/docker shared LOTR region (Middle–South-West) means both local
  providers draw from the same geographic name band; hostnames are globally
  unique so no collision occurs.
- Cloud provider credentials and configuration (API keys, regions, instance
  types) are available in the environment at run time; `create-vm.yml` does
  not manage credential provisioning.
- `provision.yml`, `destroy.yml`, and `provisioners/` coexist with the new
  playbooks throughout implementation. They are deleted only after the new
  playbooks demonstrably cover the same use cases and existing hosts have
  been migrated. No existing feature breaks during implementation.
- When a cloud VM is deleted via the provider API, the dynamic inventory
  automatically stops returning it; no additional deregistration step is
  required for cloud providers on destroy.
- If a VM exists on the provider but is absent from the static inventory
  (for local providers), `destroy-vm.yml` treats it as unknown and fails;
  manual cleanup of orphaned VMs is out of scope.
- The existing `moria` AWS Windows host is unaffected; Windows VM creation
  remains out of scope.
