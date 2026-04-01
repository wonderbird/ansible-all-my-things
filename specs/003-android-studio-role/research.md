# Research: Android Studio Ansible Role

**Feature**: `003-android-studio-role`
**Date**: 2026-03-31

## Decision 1 — Snap module vs. command module

**Decision**: Use `community.general.snap` with `state: present`.

**Rationale**: Official collection modules are preferred over raw
`ansible.builtin.command` for maintainability and faster upstream fixes.
`community.general.snap` expresses intent declaratively and handles
idempotency natively — it reports `changed` on first install and `ok` on
subsequent runs without a manual guard:

```yaml
- name: Install Android Studio via snap
  community.general.snap:
    name: android-studio
    classic: true
    state: present
```

`community.general` must be added to `requirements.yml` to satisfy this
dependency.

**Alternatives considered**:

- `ansible.builtin.command` with a `creates:` guard — rejected; custom guards
  are harder to maintain than a purpose-built module, and any bugs must be
  fixed in-repo rather than relying on upstream fixes.

## Decision 2 — Role file layout

**Decision**: Two-file layout matching `google_chrome`: `meta/main.yml` and
`tasks/main.yml` only. No `defaults/`, `vars/`, `handlers/`, or `templates/`
directories.

**Rationale**: The role has no configurable variables (snap package name is
fixed), no service restarts (snap handles its own daemon), no templates, and
no files to distribute. Adding empty directories is noise.

**Alternatives considered**: Full scaffold with all directories — rejected;
Constitution §IV prohibits speculative structure.

## Decision 3 — Idempotency

**Decision**: Rely on `community.general.snap` native idempotency; no manual
guard path needed.

**Rationale**: The module checks snap state before acting and reports `ok`
when the snap is already installed. A `creates:` guard is unnecessary and
would duplicate logic the module already encapsulates.

**Alternatives considered**:

- `creates: /snap/android-studio/current` — valid guard path for
  `ansible.builtin.command`, but not applicable now that the snap module is
  used (see Decision 1).
