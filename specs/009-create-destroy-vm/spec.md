# Feature Specification: Create and Destroy VM Playbooks

**Feature Branch**: `009-create-destroy-vm`
**Created**: 2026-06-06
**Status**: Draft
**Input**: User description: "We shall specify the feature explained in docs/feature-requests/feat.create-destroy-vm/prd.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create New VM (Priority: P1)

An engineer wants to spin up a fresh Linux VM for testing or development. They run a
single command specifying what kind of VM they need (profile) and optionally which
provider to use. The system picks the next available hostname from a provider-specific
pool, creates the VM, registers it so it is immediately targetable, and reports the
hostname on completion.

**Why this priority**: Core value. Without VM creation nothing else in the feature
matters. All other stories depend on VMs existing.

**Independent Test**: Run `create-vm.yml` with `profile=basic` against a test
environment. The command completes, prints a hostname, and the VM is reachable via SSH.

**Acceptance Scenarios**:

1. **Given** no VMs from the default provider (tart) pool are in use, **When**
   `create-vm.yml` runs with `profile=basic`, **Then** a new VM is created, its
   hostname is drawn from the tart pool, it is registered in inventory, and the
   hostname is printed on completion.
2. **Given** `provider=hcloud` is specified, **When** `create-vm.yml` runs with
   `profile=basic provider=hcloud`, **Then** a VM is created on Hetzner Cloud with a
   hostname from the North-West LOTR pool, and it appears in inventory under the
   `hcloud` and `linux` groups.
3. **Given** one tart VM already exists, **When** `create-vm.yml` runs again with
   `profile=basic`, **Then** a second VM is created with a different hostname from the
   pool, and both VMs coexist in inventory.
4. **Given** `profile=desktop`, **When** `create-vm.yml` runs, **Then** the VM is
   configured with a desktop environment, using a hostname drawn from the same
   provider pool as a `basic` VM.

---

### User Story 2 - Destroy VM by Hostname (Priority: P2)

An engineer is done with a VM and wants to remove it cleanly. They run a single
command specifying the hostname. The VM is deleted from the provider and removed from
inventory, leaving no dangling entries.

**Why this priority**: Symmetrical to creation. Lifecycle management is incomplete
without clean teardown. Dangling VMs accumulate cost and stale inventory entries cause
confusion.

**Independent Test**: Given a running VM `edoras`, run `destroy-vm.yml` with
`hostname=edoras`. Verify the VM no longer exists on the provider and `edoras` is
absent from inventory.

**Acceptance Scenarios**:

1. **Given** a VM `edoras` exists in inventory, **When** `destroy-vm.yml` runs with
   `hostname=edoras`, **Then** the VM is deleted from the provider and `edoras` no
   longer appears in inventory.
2. **Given** `hostname` refers to a local provider VM (tart or docker), **When**
   `destroy-vm.yml` completes, **Then** the static inventory file no longer contains
   that hostname.
3. **Given** a hostname not present in inventory, **When** `destroy-vm.yml` runs,
   **Then** the playbook fails immediately with a clear error message identifying the
   unknown hostname.

---

### User Story 3 - Provider-Encoded Hostnames (Priority: P3)

An engineer glancing at inventory can identify which provider hosts a VM from its
hostname alone, without consulting documentation or filtering by group.

**Why this priority**: Reduces cognitive load in multi-provider environments. The
infrastructure self-documents. Lower than create/destroy because infrastructure
functions correctly without it.

**Independent Test**: Create one VM per provider. Read the four hostnames. Without
any other context, confirm each hostname's LOTR region maps unambiguously to exactly
one provider.

**Acceptance Scenarios**:

1. **Given** VMs exist across multiple providers, **When** an engineer lists
   hostnames, **Then** each hostname's LOTR region maps unambiguously to exactly one
   provider (North-West → hcloud, North-East → aws, Middle/South-West → tart or
   docker).
2. **Given** grandfathered hostnames `hobbiton`, `rivendell`, `lorien`, `dagorlad`
   are already assigned, **When** new VMs are created for their respective providers,
   **Then** the next hostname is drawn from the same regional pool without reusing the
   grandfathered name.

---

### User Story 4 - Pool Exhaustion Fails Loud (Priority: P4)

All hostnames in a provider's pool are in use. The engineer attempts to create another
VM. The system refuses immediately with an error that names the exhausted pool, without
making any infrastructure change.

**Why this priority**: Safety guardrail. Failure must be explicit and actionable rather
than silent or misleading. Lower priority because it is a rare boundary condition.

**Independent Test**: Exhaust a provider pool, then attempt VM creation. The command
fails before any provider action, with an error message naming the pool.

**Acceptance Scenarios**:

1. **Given** all hostnames in the tart pool are in use, **When** `create-vm.yml` runs
   with `provider=tart`, **Then** the playbook fails immediately — before any VM or
   provider action — with an error message naming the exhausted pool.

---

### Edge Cases

- What happens when the provider is unreachable at VM creation time? The playbook
  should fail with a provider-specific error; no hostname is consumed from the pool.
- What happens when `destroy-vm.yml` is given a hostname that exists in inventory but
  the VM is already gone from the provider? The playbook attempts cleanup, removes the
  stale inventory entry, and warns the engineer.
- What if two operators run `create-vm.yml` concurrently for the same provider? Pool
  allocation must not assign the same hostname to both.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST create one new VM per `create-vm.yml` invocation; it
  MUST NOT reuse or reprovision an existing VM.
- **FR-002**: `create-vm.yml` MUST accept `profile` (required: `basic` or `desktop`)
  and `provider` (optional: `tart`, `docker`, `hcloud`, `aws`; default `tart`).
- **FR-003**: `destroy-vm.yml` MUST accept `hostname` (required) identifying a VM
  present in inventory.
- **FR-004**: The system MUST draw the VM hostname from an ordered, provider-specific
  pool of LOTR place names; the pool's LOTR region MUST encode the provider.
- **FR-005**: The system MUST register each newly created VM in inventory before
  `create-vm.yml` completes, making it immediately targetable.
- **FR-006**: For local providers (`tart`, `docker`), the system MUST update the
  static inventory file on both create and destroy.
- **FR-007**: For cloud providers (`hcloud`, `aws`), inventory MUST be managed via
  dynamic inventory integration; no manual file edits are required.
- **FR-008**: `create-vm.yml` MUST print the assigned hostname on successful
  completion.
- **FR-009**: When the provider's hostname pool is exhausted, `create-vm.yml` MUST
  fail immediately with an error message naming the exhausted pool, without performing
  any provider or VM action.
- **FR-010**: `destroy-vm.yml` MUST remove the hostname from inventory on completion.
- **FR-011**: `destroy-vm.yml` MUST fail with a clear, actionable error if the
  specified hostname is not found in inventory.
- **FR-012**: The superseded artefacts `provision.yml`, `destroy.yml`, and the
  `provisioners/` directory MUST be deleted.
- **FR-013**: User documentation (`docs/user-manual/create-vm.md`) MUST document
  `create-vm.yml` and `destroy-vm.yml`; all references to `provision.yml` or
  `destroy.yml` MUST be removed from user-facing documentation.
- **FR-014**: Grandfathered hostnames (`hobbiton`, `rivendell`, `lorien`, `dagorlad`,
  `moria`) MUST be the first entries in their respective provider pools.

### Key Entities

- **VM Profile**: Defines the software configuration applied to a new VM. Values:
  `basic` (console only), `desktop` (desktop environment). Profile does not affect
  hostname pool selection.
- **Provider**: The platform where the VM is created. Values: `tart` (local macOS),
  `docker` (local Linux), `hcloud` (Hetzner Cloud), `aws` (Amazon Web Services).
- **Hostname Pool**: An ordered list of LOTR place names scoped to a provider. Each
  entry is either available or in use. Pools are regional: North-West/Eriador
  (hcloud), North-East/Iron Hills (aws), Middle–South-West/Rohan–Gondor (tart and
  docker), South-East/Mordor (Windows, reserved for future use).
- **Inventory Entry**: A record of a VM's hostname, connection details, and group
  membership, persisted so automation can target the VM. Local-provider entries live
  in a static file; cloud-provider entries are resolved dynamically.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An engineer creates any supported VM type on any supported provider with
  a single command and no manual steps beyond supplying the required parameters.
- **SC-002**: An engineer destroys any VM with a single command specifying only the
  hostname.
- **SC-003**: Every hostname visible in inventory identifies its provider at a glance
  without consulting external documentation.
- **SC-004**: Pool exhaustion is detected and reported before any infrastructure
  change is attempted, with an error message that names the depleted pool.
- **SC-005**: No references to `provision.yml` or `destroy.yml` remain in user-facing
  documentation or scripts after delivery.
- **SC-006**: Concurrent VM creation for the same provider never assigns the same
  hostname to two VMs.

## Assumptions

- LOTR hostname pools have sufficient names for foreseeable use; exact pool contents
  and sizes are an implementation detail to be defined during planning.
- `tart` and `docker` share the same LOTR region (Middle–South-West) because they are
  both local providers; hostnames within the shared pool are globally unique,
  preventing collision between the two.
- Cloud provider credentials and configuration (API keys, regions, instance types) are
  available in the environment at run time; `create-vm.yml` does not manage credential
  provisioning.
- The existing `moria` AWS Windows host is grandfathered and unaffected; Windows VM
  creation remains out of scope.
- When a cloud VM is deleted via the provider API, the dynamic inventory automatically
  stops returning it; no additional deregistration step is required for cloud providers
  on destroy.
- If a VM exists on the provider but is absent from the static inventory (for local
  providers), `destroy-vm.yml` treats it as unknown and fails; manual cleanup of
  orphaned VMs is out of scope.
