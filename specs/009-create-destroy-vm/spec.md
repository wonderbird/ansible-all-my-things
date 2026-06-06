# Feature Specification: Create and Destroy VM Playbooks (Phase 1)

**Feature Branch**: `009-create-destroy-vm`
**Created**: 2026-06-06
**Status**: Draft
**Input**: `docs/feature-requests/feat.create-destroy-vm/prd.md`
**Scope**: Phase 1 of
`docs/feature-requests/feat.create-destroy-vm/roadmap.md`

## Scope Note

This spec covers **Phase 1 only**: create and destroy a local `tart` VM with
the `basic` profile. The full vision — additional providers, the `desktop`
profile, a profile-group `configure.yml`, dynamic-inventory integration,
provider-encoded hostnames, and deletion of the superseded `provision.yml` /
`destroy.yml` / `provisioners/` artefacts — is sequenced across later phases in
`roadmap.md` and is explicitly **out of scope here**.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a tart VM (Priority: P1)

An engineer wants to spin up a fresh local Linux VM for testing or development.
They run a single command. The system picks the next unused hostname from the
shared ordered pool, creates the VM on `tart`, registers it in the static
inventory under the `basic` group, and reports the hostname on completion. If
the pool is exhausted, the command refuses immediately — before any
infrastructure action — with an error naming the exhausted pool.

**Why this priority**: Core value and the walking skeleton. Without VM
creation nothing else in the feature matters; every later phase builds on it.

**Independent Test**: Run `create-vm.yml` with no extra-vars on a tart-capable
host. The command completes, prints a hostname, and the VM is reachable via
SSH and present in the static inventory.

**Acceptance Scenarios**:

1. **Given** the hostname pool has unused entries, **When** `create-vm.yml`
   runs with no extra-vars, **Then** a new VM is created on the default
   provider (`tart`) with the default profile (`basic`), the next unused
   hostname from the pool is assigned, the VM is registered in the static
   inventory under the `basic` group, and the hostname is printed on
   completion.
2. **Given** one VM already exists, **When** `create-vm.yml` runs again,
   **Then** a second VM is created with the next unused hostname, and both VMs
   coexist in inventory.
3. **Given** all hostnames in the pool are in use, **When** `create-vm.yml`
   runs, **Then** the playbook fails immediately — before any VM or provider
   action — with an error message naming the exhausted pool.

---

### User Story 2 - Destroy a tart VM by hostname (Priority: P2)

An engineer is done with a VM and wants to remove it cleanly. They run a single
command specifying the hostname. The VM is deleted from `tart` and removed from
the static inventory, leaving no dangling entries.

**Why this priority**: Symmetrical to creation. Lifecycle management is
incomplete without clean teardown. Dangling VMs accumulate cost and stale
inventory entries cause confusion.

**Independent Test**: Given a running tart VM `lorien`, run `destroy-vm.yml`
with `hostname=lorien`. Verify the VM no longer exists on tart and `lorien` is
absent from the static inventory.

**Acceptance Scenarios**:

1. **Given** a tart VM exists in inventory, **When** `destroy-vm.yml` runs with
   its `hostname`, **Then** the VM is deleted from tart and the hostname no
   longer appears in the static inventory file.
2. **Given** a hostname not present in inventory, **When** `destroy-vm.yml`
   runs, **Then** the playbook fails immediately with a clear error message
   identifying the unknown hostname.

---

### Edge Cases

- What happens when tart is unavailable at VM creation time? The playbook
  should fail with a provider-specific error; no hostname is consumed from the
  pool.
- What happens when `destroy-vm.yml` is given a hostname that exists in
  inventory but the VM is already gone from tart? The playbook attempts
  cleanup, removes the stale inventory entry, and warns the engineer.
- What if two operators run `create-vm.yml` concurrently? Pool allocation must
  not assign the same hostname to both.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST create one new VM per `create-vm.yml`
  invocation; it MUST NOT reuse or reprovision an existing VM.
- **FR-002**: `create-vm.yml` MUST accept `profile` (optional; only `basic` is
  supported in this phase; default `basic`) and `provider` (optional; only
  `tart` is supported in this phase; default `tart`). An unsupported value MUST
  fail loud with an actionable error.
- **FR-003**: `destroy-vm.yml` MUST accept `hostname` (required) identifying a
  VM present in inventory.
- **FR-004**: The system MUST draw the VM hostname from a single shared ordered
  list of LOTR place names. Hostnames are assigned sequentially; the next
  unused entry in the list (the first name not already present in inventory) is
  selected on each invocation.
- **FR-005**: The system MUST register each newly created VM in inventory and
  place it in the `basic` group before `create-vm.yml` completes.
- **FR-006**: For the `tart` provider, the system MUST update the static
  inventory file on both create and destroy.
- **FR-008**: `create-vm.yml` MUST print the assigned hostname on successful
  completion.
- **FR-009**: When the hostname pool is exhausted, `create-vm.yml` MUST fail
  immediately with an error message naming the exhausted pool, without
  performing any provider or VM action.
- **FR-010**: `destroy-vm.yml` MUST remove the hostname from the static
  inventory on completion.
- **FR-011**: `destroy-vm.yml` MUST fail with a clear, actionable error if the
  specified hostname is not found in inventory.
- **FR-015**: The hostname pool ships with ten ordered LOTR place names. The
  first five entries are the existing hostnames (`hobbiton`, `rivendell`,
  `lorien`, `dagorlad`, `moria`). The pool is extensible: operators may append
  names at any time.

> Deferred requirements from the full vision — dynamic inventory (was FR-007),
> `configure.yml` (was FR-012), artefact deletion (was FR-013), full
> documentation migration (was FR-014) — are tracked in `roadmap.md`.

### Key Entities

- **VM Profile**: Determines the inventory group a newly created VM is placed
  into. In this phase the only supported value is `basic` (console only).
  Profile does not affect hostname selection.
- **Provider**: The platform where the VM is created. In this phase the only
  supported value is `tart` (local macOS).
- **Hostname Pool**: A single shared ordered list of LOTR place names. Ships
  with ten names; the first five are the existing hostnames. Entries are either
  available or in use and are allocated sequentially.
- **Inventory Entry**: A record of a VM's hostname, connection details, and
  group membership, persisted in the static inventory file so automation can
  target the VM.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An engineer creates a basic tart VM with a single command; no
  extra-vars are required for the common case.
- **SC-002**: An engineer destroys any tart VM with a single command
  specifying only the hostname.
- **SC-005**: Pool exhaustion is detected and reported before any
  infrastructure change is attempted, with an error message naming the depleted
  pool.
- **SC-007**: Concurrent VM creation never assigns the same hostname to two
  VMs.

## Assumptions

- The hostname pool ships with ten names. The first five are the existing
  hostnames; five additional LOTR names are chosen during planning. Because a
  single shared sequential pool is used, the chosen names need not encode any
  provider region (see `roadmap.md`, Phase 6).
- This phase targets the `tart` provider only. tart is macOS-ARM and has no
  Molecule container path, so local validation (Constitution III) is performed
  on a Mac, not in CI.
- `provision.yml`, `destroy.yml`, and `provisioners/` are untouched in this
  phase; they remain the active path for the providers not yet migrated. Their
  deletion is deferred to `roadmap.md`, Phase 7.
- If a tart VM exists on the provider but is absent from the static inventory,
  `destroy-vm.yml` treats it as unknown and fails; manual cleanup of orphaned
  VMs is out of scope.
- The existing `moria` AWS Windows host is unaffected; Windows VM creation
  remains out of scope.
