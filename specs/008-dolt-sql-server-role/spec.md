# Feature Specification: Dolt SQL Server Ansible Role

**Feature Branch**: `008-dolt-sql-server-role`
**Created**: 2026-05-30
**Status**: Draft
**Input**: User description: "beads task 1l6"

## Feature Goal

The motivating outcome is that all parallel agent sessions on the same VM can write
task-tracking data simultaneously without any write failing due to lock contention.

This outcome cannot be tested directly in isolation — write collisions are probabilistic
and rare under normal load. Instead, it is guaranteed architecturally: if a shared
write service is running (US1) and developers have opted their repositories in (US2),
concurrent writes succeed by design. The user stories below specify the concrete,
testable conditions that together deliver this guarantee.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - SQL Server Starts Automatically on VM Boot (Priority: P1)

Each VM is created fresh and destroyed regularly. The shared write service must be
running before any agent session starts, without manual intervention after VM creation.

After a VM is provisioned once, the shared write service starts automatically on every
boot — including the initial boot after provisioning — without operator action.

**Why this priority**: Auto-startup is the foundational prerequisite. Without it,
the shared service is absent when agents start, and no other story can deliver value.

**Independent Test**: Provision a VM, reboot it, start an agent session. Verify the
agent connects to the shared service without any manual steps.

**Acceptance Scenarios**:

1. **Given** a VM provisioned for the first time, **When** the VM completes its boot
   sequence, **Then** the shared write service is running and accepting connections
   before any agent session can begin.
2. **Given** a running shared write service, **When** the service process is
   killed (SIGKILL), **Then** the service restarts automatically within a few
   seconds without any operator action (FR-003).
3. **Given** a VM where the shared write service is installed and enabled,
   **When** the VM reboots, **Then** the service is active and accepting
   connections again before any agent session can begin (FR-002).

---

### User Story 2 - Developer Initializes Repository with Dolt Backend (Priority: P2)

A developer who wants to use the running Dolt SQL server for task tracking in their git
repository runs `bd init --server` once in that repository. After initialization, tasks
created in the repository are stored in the Dolt server. This is an explicit
per-repository opt-in; only developers who choose server-backed task tracking need this
step.

**Why this priority**: Without this step no repository connects to the server. This is
the opt-in that activates the feature for actual use in a project.

**Independent Test**:

1. Create a new directory, run `git init`, add a file and commit.
2. Run `bd init --server`.
3. Create a task with `bd create`.
4. Query the Dolt server directly to verify the task record exists in the Dolt database
   for the repository's prefix — proving storage landed in Dolt, not an embedded fallback.

**Acceptance Scenarios**:

1. **Given** a git repository with at least one commit and the Dolt server running,
   **When** `bd init --server` is run, **Then** beads initializes successfully with the
   Dolt server as its backend.
2. **Given** a repository initialized with `bd init --server`, **When** a task is
   created via `bd create`, **Then** querying the Dolt server directly shows the task
   present in the Dolt database for that repository's prefix.
3. **Given** a repository initialized with `bd init --server`, **When** the Dolt server
   is queried, **Then** a dedicated database exists for the repository's prefix,
   confirming server-backed storage is active.

---

### Edge Cases

- What if provisioning is re-run on a VM where the service is already running? The
  re-run must complete without disrupting or duplicating the running service.
- What if `bd init --server` (new repo configuration) or `bd bootstrap` (restoring
  tasks in a repo already configured with server backend) is run when the server is
  not running? Both commands must fail with a clear, actionable error. Silent fallback
  to embedded mode is not acceptable in either case.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The VM provisioning process MUST install the Dolt database binary on
  each new VM as part of standard base setup.
- **FR-002**: The shared write service MUST start automatically when the VM boots,
  with no operator action required after provisioning.
- **FR-003**: The shared write service MUST restart automatically if it stops
  unexpectedly.
- **FR-004**: The Dolt SQL server MUST be ready to accept `bd init --server`
  connections immediately after provisioning completes, without requiring credentials
  or configuration beyond what the role provides.
- **FR-005**: The provisioning process MUST be idempotent — re-running it on a VM
  where the service is already installed and running MUST complete without errors
  and MUST NOT disrupt or duplicate the running service.
- **FR-006**: The provisioning process MUST NOT initialize task-tracking databases
  or restore backup data — those responsibilities belong to the session startup
  process.
- **FR-007**: The shared write service MUST accept connections from localhost only
  (loopback interface). It MUST NOT be reachable from other hosts on the network.

### Key Entities

- **Shared Write Service**: Local database service accepting concurrent writes from
  multiple agent sessions on the same VM. Runs continuously from VM boot until
  VM destruction.
- **Repository Initialization**: A one-time, per-repository developer action
  (`bd init --server`) that configures the task-tracking tool to use the Dolt SQL
  server as its backend. The role does not perform this step; it only ensures the
  server is ready to accept it.
- **VM Provisioning**: One-time setup process run when a new VM is created.
  Responsible for installing software and configuring services; does not configure
  any specific repository.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All parallel agent sessions on a provisioned VM write task-tracking
  data simultaneously with zero failures due to write-lock contention.
- **SC-002**: Shared write service is running and ready within the VM's normal boot
  sequence, before any agent session begins.
- **SC-003**: Re-provisioning a VM that already has the service installed completes
  without errors and without interrupting active agent sessions.
- **SC-004**: A developer can initialize any git repository to use the Dolt SQL
  server backend by running a single command after provisioning, with no additional
  server-side configuration required.
- **SC-005**: A crashed shared write service recovers automatically on VM reboot
  without operator intervention.

## Assumptions

- VM provisioning is performed by existing base-setup automation; this feature
  extends that process.
- Shared write service is local to each VM — not shared across multiple VMs.
- Database initialization and data restore/backup remain the responsibility of
  session startup and shutdown processes respectively; not this provisioning feature.
- Task-tracking tool supports connecting to the Dolt SQL server via `bd init --server`;
  no changes to the tool itself are required.
- Repository configuration is a per-repository developer opt-in (`bd init --server`);
  the role does not configure any repository automatically.

## Clarifications

### Session 2026-05-30

- Q: US1 is the hoped-for outcome but cannot be tested directly (collisions are
  probabilistic). How should this be represented? → A: Converted US1 to a
  "Feature Goal" section above user stories. The goal is verified architecturally
  through US1 + US2 together, not by a direct collision test. Former US2 → US1
  (P1), former US3 → US2 (P2).
- Q: Should the shared write service accept connections from localhost only or
  from all network interfaces? → A: Localhost only (loopback interface only;
  not reachable from other hosts). Added FR-007.
- Q: Does the Ansible role configure repository task-tracking settings, or only
  install and start the server? → A: Role = server only. `bd init --server` is a
  developer one-time action per repository; the role has no knowledge of any
  specific repo. Invalidated old FR-004 and SC-004.
- Q: How should FR-004 and SC-004 be updated given that `bd init --server` is a
  manual developer step? → A: FR-004 replaced with server readiness for
  `bd init --server`. SC-004 replaced with "single command to init any repo,
  no extra server-side setup required."
- Q: Should US2 acceptance verify task presence by querying Dolt directly or via
  beads round-trip? → A: Direct Dolt query — only this proves storage landed in
  Dolt rather than silently falling back to embedded mode.
- Q: First edge case ("agent session detects missing server") is redundant and
  hard to test — what are the real entry points? → A: Removed vague "agent session"
  edge cases. Real entry points are `bd init --server` (new repo) and `bd bootstrap`
  (cloned repo with existing server config). Both must fail loudly when server is
  not running. Edge Cases section updated accordingly.
