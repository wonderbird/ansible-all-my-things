# System Patterns

## Role structure (mirrors `roles/google_chrome/`)

```text
roles/android_studio/
├── meta/main.yml   # galaxy_info + dependencies: []
└── tasks/main.yml  # single install task
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

## meta/main.yml pattern (mirrors `roles/google_chrome/meta/main.yml`)

See `specs/003-android-studio-role/plan.md` for the exact fields.

## Idempotency guard

`/snap/android-studio/current` — symlink created by snapd on install;
absent before install; stable across snap refreshes.

## Research decisions

`specs/003-android-studio-role/research.md` — why `community.general.snap`
over `ansible.builtin.command`, two-file layout rationale, native idempotency.
