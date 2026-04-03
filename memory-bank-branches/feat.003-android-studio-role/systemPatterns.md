# System Patterns

## Role structure

```text
roles/android_studio/
├── defaults/main.yml  # android_cmdlinetools_build variable
├── meta/main.yml      # galaxy_info + dependencies: []
└── tasks/main.yml     # snap install + SDK pre-provisioning
```

## tasks/main.yml pattern

```yaml
#SPDX-License-Identifier: MIT-0
---
- name: Install Android Studio via snap
  community.general.snap:
    name: android-studio
    classic: true
    state: present
```

## configure-linux-roles.yml entry pattern (mirrors google_chrome)

```yaml
- role: android_studio
  tags: not-supported-on-vagrant-arm64
```

Tag at role-entry level only — individual tasks carry no tags.

Roles in `configure-linux-roles.yml` are sorted alphabetically.

## meta/main.yml pattern (mirrors `roles/google_chrome/meta/main.yml`)

See `specs/003-android-studio-role/plan.md` for the exact fields.

## Idempotency guard

`/snap/android-studio/current` — symlink created by snapd on install;
absent before install; stable across snap refreshes.

## Research decisions

`specs/003-android-studio-role/research.md` — why `community.general.snap`
over `ansible.builtin.command`, two-file layout rationale, native idempotency.
