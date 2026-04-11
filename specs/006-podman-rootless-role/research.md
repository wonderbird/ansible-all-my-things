# Research: Rootless Podman Ansible Role

**Feature**: `006-podman-rootless-role`
**Date**: 2026-04-11

## Summary

All technical questions were resolved from codebase inspection, Ubuntu package
documentation, and Podman upstream documentation. No external unknowns remain.

---

## Decision 1 — Package source for Podman

**Decision**: Install from the Ubuntu distribution repository using
`ansible.builtin.apt` with `name: podman` and `state: present`.

**Rationale**: The Ubuntu 22.04 LTS (Jammy) and later repositories include the
`podman` package. No external PPA is required. Using the distribution package
keeps the role offline-capable after initial APT cache population and avoids
third-party GPG key management. FR-001 and the spec assumption both confirm
this choice.

**Alternatives considered**:

- Kubic OBS PPA (newer Podman versions): rejected — adds PPA management
  complexity with no confirmed benefit for this project (YAGNI).
- Building from source: rejected — out of scope, unnecessary complexity.

---

## Decision 2 — subuid/subgid management strategy

**Decision**: Use `ansible.builtin.lineinfile` with `regexp: '^{{ item }}:'`
and `line: '{{ item }}:{{ podman_subuid_start }}:{{ podman_subuid_count }}'`
on both `/etc/subuid` and `/etc/subgid`, looping over `desktop_user_names`.

**Rationale**: `ansible.builtin.lineinfile` with a start-anchored regexp is
idempotent: it matches the existing line if present (no change) or inserts the
configured line if absent (change). The spec explicitly documents this approach
in its Assumptions section and justifies why `ansible.builtin.user` and
`usermod --add-subuids` are not used:

- `ansible.builtin.user` has no subuid/subgid parameter in any released Ansible
  version as of April 2026.
- `usermod --add-subuids` is not idempotent — it appends duplicates on
  re-runs.

**Alternatives considered**:

- `community.general.user` with subuid support: not available in any released
  version.
- `ansible.builtin.command: usermod --add-subuids`: not idempotent, rejected.
- `ansible.builtin.template` for full file management: over-engineered for a
  single-entry-per-user pattern; lineinfile is sufficient (YAGNI).

---

## Decision 3 — podman system migrate idempotency guard

**Decision**: Use `ansible.builtin.command` with `changed_when: false` to run
`podman system migrate` as each user after subuid/subgid changes.

**Rationale**: `podman system migrate` is a safe, fast, non-destructive command
that re-applies the user-namespace mapping from `/etc/subuid` and `/etc/subgid`
to the user's local container storage. It produces no reliable sentinel file to
use with `creates:`. Marking it `changed_when: false` satisfies FR-006 and
Principle I by preventing spurious "changed" reports. The command is always
executed but is idempotent in effect — running it on an already-migrated system
is a no-op at the storage level.

**Alternatives considered**:

- Triggering migrate via a handler notified by the lineinfile tasks: would
  prevent migrate from running on the first play run if subuid/subgid lines
  are not yet present. Running unconditionally is simpler and correct.
- Using `creates:` with a sentinel file: no reliable sentinel exists for
  migration state; this would require writing a marker file, adding
  unnecessary complexity.

---

## Decision 4 — Default subuid/subgid ranges

**Decision**: `podman_subuid_start: 100000`, `podman_subuid_count: 65536`. Identical
defaults for `podman_subgid_start` and `podman_subgid_count`.

**Rationale**: These are the standard defaults used by `useradd` on modern
Ubuntu systems (documented in `/etc/login.defs`). 65536 sub-IDs is the
minimum required for containers that map up to 65535 UIDs. Using the same
start for all users is a conscious simplification: this role targets a
workstation with a small, known set of desktop users, not a multi-tenant server
where ranges must be non-overlapping (YAGNI / Principle IV).

**Alternatives considered**:

- Per-user calculated offsets (e.g. `100000 + user_index * 65536`): adds
  complexity; not needed for a single-person workstation.
- Larger count (e.g. 131072): unnecessary; 65536 covers all practical rootless
  container use cases.

---

## Decision 5 — No task-level `become: true`

**Decision**: No task in `tasks/main.yml` sets `become: true` at task level.
The calling playbook `configure-linux-roles.yml` sets `become: true` at play
level. Per-user tasks use `become_user: "{{ item }}"`.

**Rationale**: Matches the established convention in `roles/java/`,
`roles/android_studio/`, and `roles/flutter/`. Play-level `become` is
inherited by all tasks. `become_user` overrides the effective user for
specific tasks without requiring explicit `become: true` on each.

---

## Decision 6 — ARM64 compatibility

**Decision**: No architecture-specific branching; no `not-supported-on-vagrant-arm64`
tag in `configure-linux-roles.yml`.

**Rationale**: The Ubuntu `podman` package is available for both `amd64` and
`arm64`. APT resolves the correct architecture automatically. Rootless
configuration via `/etc/subuid` and `/etc/subgid` is architecture-independent.
`podman system migrate` is also architecture-independent.

---

## No NEEDS CLARIFICATION items remaining

All technical questions are resolved. The plan and design can proceed to Phase 1.
