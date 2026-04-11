# Feature Specification: Rootless Podman Ansible Role

**Feature Branch**: `006-podman-rootless-role`
**Created**: 2026-04-11
**Status**: Draft
**Input**: User description: "Create a new Ansible role called podman inside
the roles/ directory. Install Podman in rootless mode on Ubuntu Linux and
configure it for every user listed in the desktop_user_names variable."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install and Run Podman as a Desktop User (Priority: P1)

A developer provisioning a new Ubuntu Linux workstation runs the Ansible playbook.
After the run completes, every desktop user listed in the shared configuration
variable can invoke `podman` from their own login shell, build a container image
from the repository's Dockerfile, and run that image — without requiring root
privileges.

**Why this priority**: This is the single primary outcome the role exists to
deliver. All other stories depend on this working first.

**Independent Test**: Run the playbook against a fresh Ubuntu VM, then log in
as one of the target users and run `podman --version`. A version string proves
the tool is present and accessible. Run `podman build` and `podman run` to
confirm end-to-end container workflows work.

**Acceptance Scenarios**:

1. **Given** a fresh Ubuntu VM with no Podman installed, **When** the playbook
   is run with a populated `desktop_user_names` list, **Then** `podman --version`
   succeeds for every listed user.

2. **Given** Podman is installed for all listed users, **When** a user runs
   `podman build -t devcontainer -f .devcontainer/Dockerfile .` from the
   repository root, **Then** the build completes without errors.

3. **Given** a container image named `devcontainer` exists in the user's local
   registry, **When** the user runs `podman run --rm devcontainer ansible --version`,
   **Then** an Ansible version string is printed to stdout.

---

### User Story 2 - Rootless Configuration Per User (Priority: P2)

A system administrator needs every listed desktop user to be able to run
containers without root access. The role automatically configures the
kernel-level user-namespace mappings required for rootless container operation.

**Why this priority**: Without correct subuid/subgid entries, rootless Podman
cannot run containers. This is a hard prerequisite for user story 1 to work
reliably across all users, but it is a distinct configuration concern.

**Independent Test**: After the role runs, inspect `/etc/subuid` and `/etc/subgid`.
Each user in `desktop_user_names` must have a valid range entry. Then run
`podman run --rm hello-world` as one of those users to confirm rootless
operation works end-to-end.

**Acceptance Scenarios**:

1. **Given** a user in `desktop_user_names` has no subuid/subgid entries,
   **When** the playbook runs, **Then** valid subuid and subgid ranges are
   present in `/etc/subuid` and `/etc/subgid` for that user.

2. **Given** subuid/subgid entries already exist for a user, **When** the
   playbook runs again, **Then** no duplicate entries are created and the
   task reports no changes.

---

### User Story 3 - Idempotent Re-Runs (Priority: P3)

A developer re-runs the playbook on a machine where Podman is already fully
configured. The role must complete without making any changes, confirming the
system is already in the desired state.

**Why this priority**: Idempotency is a non-negotiable constitutional
requirement (Principle I). Failing this would make the role unsafe for repeated
provisioning runs.

**Independent Test**: Run the playbook twice in sequence. The second run must
report zero changed tasks.

**Acceptance Scenarios**:

1. **Given** Podman is already installed and all users are fully configured,
   **When** the playbook is run again, **Then** every task reports `ok` or
   `skipped` and no task reports `changed`.

---

### Edge Cases

- What happens when a username in `desktop_user_names` does not exist on the
  target system? `ansible.builtin.lineinfile` does NOT fail for a non-existent
  system user — it silently writes an orphaned entry to `/etc/subuid` and
  `/etc/subgid`. The role does not validate whether the user exists in the
  system (YAGNI); callers must ensure `desktop_user_names` contains valid
  system users.

- What happens when the Ubuntu apt package `podman` is already at the latest
  version? The apt task must report no change (idempotent).

- What happens when a user already has subuid/subgid entries from a prior
  manual setup? The role must not create duplicate entries.

- What happens when `desktop_user_names` is an empty list? The role must
  install Podman system-wide but skip all per-user configuration loops without
  error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The role MUST install Podman from the Ubuntu distribution
  package repository using the system package manager.

- **FR-002**: The role MUST ensure that, for every user in `desktop_user_names`,
  a valid subuid range entry exists in `/etc/subuid`.

- **FR-003**: The role MUST ensure that, for every user in `desktop_user_names`,
  a valid subgid range entry exists in `/etc/subgid`.

- **FR-004**: Every task MUST be idempotent: re-running the role against an
  already-configured host MUST produce zero changed tasks.

- **FR-005**: The role MUST use `ansible.builtin.*` fully-qualified collection
  names for every module used.

- **FR-006**: Any `command` or `shell` task MUST include a `creates:` or
  `changed_when:` guard to prevent unnecessary re-execution.

- **FR-007**: The role MUST include a `defaults/main.yml` file that declares
  all role variables with sensible defaults.

- **FR-008**: The role MUST include a `meta/main.yml` file describing the
  role's metadata (author, licence, platforms).

- **FR-009**: Every YAML file in the role MUST carry the SPDX licence header
  `# SPDX-License-Identifier: MIT-0` as its first line.

- **FR-010**: The role MUST include a `README.md` documenting the role's
  purpose, variables, and usage, following the project's Markdown quality
  standards (Principle VI).

- **FR-011**: The role MUST NOT install the `podman-docker` compatibility
  shim; users invoke `podman` directly.

- **FR-012**: The role MUST include a `DESIGN.md` file documenting non-obvious
  design decisions (e.g. subuid/subgid allocation strategy, `podman system
  migrate` guard choice).

### Assumptions

- The Ubuntu distribution package for `podman` (available in Ubuntu 22.04 LTS
  and later) supports `--mount=type=cache` in `podman build`. No external PPA
  is required.

- The `# syntax=docker/dockerfile:1` comment in `.devcontainer/Dockerfile` is
  a BuildKit parser directive that Podman ignores silently; no Podman-specific
  Dockerfile modifications are needed.

- Each username in `desktop_user_names` corresponds to an existing system user.
  User creation is out of scope for this role.

- subuid/subgid entries are managed with `ansible.builtin.lineinfile` targeting
  `/etc/subuid` and `/etc/subgid` directly. The `regexp` is anchored to
  `^username:` so each task matches and enforces the complete
  `username:start:count` line — making the operation idempotent. Neither
  `ansible.builtin.user` (no subuid/subgid support in any released Ansible
  version) nor `usermod --add-subuids` (not idempotent) is used. Default role
  variables: `subuid_start: 100000`, `subuid_count: 65536` (and identical
  defaults for subgid).

- Systemd lingering is not configured. The use case is interactive
  `podman build` / `podman run`; no containers run as persistent services.
  Enabling lingering would add complexity with no benefit (YAGNI).

- No role-level `registries.conf` management is needed. All image references
  in scope use fully-qualified names (e.g. `docker.io/python:trixie`). Podman's
  default `/etc/containers/registries.conf` already includes `docker.io` as an
  unqualified-search registry.

- No Ubuntu version pre-flight assert is added. The role targets Ubuntu 22.04
  LTS and later; a version check is out of scope (YAGNI / Principle IV).

- The calling playbook MUST set `become: true` at play level. The role itself
  does not set `become: true` on individual tasks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After one playbook run on a fresh Ubuntu VM, every user in
  `desktop_user_names` can execute `podman --version` without errors.

- **SC-002**: After one playbook run, a user in `desktop_user_names` can
  successfully build the repository's development container image using
  `podman build` and run it using `podman run` without root privileges.

- **SC-003**: A second consecutive playbook run against an already-configured
  host reports zero changed tasks (full idempotency).

- **SC-004**: Every user in `desktop_user_names` has a subuid and subgid range
  entry present in `/etc/subuid` and `/etc/subgid` respectively.
