# Design Notes: podman role

This document records non-obvious design decisions made during implementation
of the `podman` role. Decision numbers correspond to entries in
`specs/006-podman-rootless-role/research.md`; only non-obvious decisions are
recorded here, so gaps in numbering are intentional.

## Decision 2 — lineinfile idempotency strategy for subuid/subgid

`ansible.builtin.lineinfile` with `regexp: "^{{ item }}:"` is used to manage
entries in `/etc/subuid` and `/etc/subgid`.

The start-anchored regexp matches the existing line if it is already present
(no change) or inserts the configured line if it is absent (change). This
makes the task idempotent across playbook re-runs.

`ansible.builtin.user` does not support subuid/subgid parameters in any
released Ansible version (as of April 2026). `usermod --add-subuids` is not
idempotent — it appends duplicate entries on every run. `lineinfile` is the
correct tool here.

## Decision 3 — `podman system migrate` `changed_when: false` guard

`ansible.builtin.command: podman system migrate` runs as each desktop user
after subuid/subgid changes. The task is marked `changed_when: false` because
the command produces no reliable sentinel that could be used with `creates:`.

Running it unconditionally is safe: on an already-migrated system it is a
no-op at the storage level. Its cost is negligible. The `changed_when: false`
guard prevents spurious "changed" reports on idempotency re-runs.

A handler was not used. Handlers fire only when a notifying task reports
`changed`, which would suppress the migration on idempotency re-runs where
subuid/subgid lines are already correct. More importantly, introducing a
`handlers/` directory for a single side-effect-free command adds structural
complexity with no benefit — the unconditional approach is simpler and equally
correct.

## Decision 4 — Shared subuid/subgid start value for all users

All users listed in `desktop_user_names` receive the same default
`podman_subuid_start` / `podman_subgid_start` value (`100000`). This is
intentional for the primary use case: a single-person workstation where only
one user requires rootless Podman at a time. Overlapping subordinate ID ranges
cause no problems when only one user's containers run concurrently.

Per-user offset calculation is out of scope (YAGNI). Callers deploying to
multi-user servers where non-overlapping ranges are required must override
`podman_subuid_start` and `podman_subgid_start` per user via `host_vars` or
`group_vars`.

## Decision 5 — Play-level `become` convention

No task in `tasks/main.yml` sets `become: true` at task level. The calling
playbook sets `become: true` at play level, which is inherited by all tasks.
Per-user tasks use `become_user: "{{ item }}"` to override the effective user
without requiring explicit `become: true` on each task.

This matches the convention established in `roles/java/`,
`roles/android_studio/`, and `roles/flutter/`.
