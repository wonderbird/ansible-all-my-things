# Research: Android Studio Ansible Role

**Feature**: `003-android-studio-role`
**Date**: 2026-03-31

## Decision 1 — Snap module vs. command module

**Decision**: Use `ansible.builtin.command` with a `creates:` guard rather
than `community.general.snap`.

**Rationale**: `community.general` is not listed in `requirements.yml`. Adding
a full collection for a single snap install task violates Constitution §IV
(Simplicity/YAGNI). The `ansible.builtin.command` approach achieves identical
idempotency with no new dependency:

```yaml
- name: Install Android Studio via snap
  ansible.builtin.command:
    cmd: snap install android-studio --classic
    creates: /snap/android-studio/current
  become: true
```

`/snap/android-studio/current` is the canonical symlink that snapd creates
for every installed classic snap and points to the active revision. Its
presence is a reliable, stable footprint for the `creates:` guard.

**Alternatives considered**:

- `community.general.snap` with `state: present` — rejected; requires adding
  `community.general` to `requirements.yml` for a single task. The module
  also reports `changed` on first install and `ok` on subsequent runs, which
  is the same behaviour as the `creates:` guard approach.

## Decision 2 — Role file layout

**Decision**: Two-file layout matching `google_chrome`: `meta/main.yml` and
`tasks/main.yml` only. No `defaults/`, `vars/`, `handlers/`, or `templates/`
directories.

**Rationale**: The role has no configurable variables (snap package name is
fixed), no service restarts (snap handles its own daemon), no templates, and
no files to distribute. Adding empty directories is noise.

**Alternatives considered**: Full scaffold with all directories — rejected;
Constitution §IV prohibits speculative structure.

## Decision 3 — Idempotency guard path

**Decision**: `creates: /snap/android-studio/current`

**Rationale**: `snapd` creates `/snap/<snap-name>/current` as a symlink to
the active revision for every installed snap. This path is present after any
successful `snap install android-studio` (classic or otherwise) and absent
otherwise. It is stable across snap refreshes (the symlink target changes;
the symlink itself remains). Using it as the `creates:` guard means the
install task is skipped on every subsequent run, regardless of which revision
is active.

**Alternatives considered**:

- `creates: /snap/bin/android-studio` — snap also creates command wrappers
  in `/snap/bin/`; equally valid but less canonical than `current`.
- Checking `/usr/bin/android-studio` — not applicable; classic snaps do not
  write to `/usr/bin/`.
