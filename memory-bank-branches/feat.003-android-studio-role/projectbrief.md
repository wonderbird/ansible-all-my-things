# Project Brief: feat.003-android-studio-role

**Goal**: Create `android_studio` Ansible role that installs Android Studio
(stable) via snap on AMD64 Ubuntu VMs and skips gracefully on ARM64.

**Spec**: `specs/003-android-studio-role/spec.md`
**Plan**: `specs/003-android-studio-role/plan.md`
**Research**: `specs/003-android-studio-role/research.md`
**Test guide**: `specs/003-android-studio-role/quickstart.md`

## Deliverables

| File | Action |
| ---- | ------ |
| `roles/android_studio/meta/main.yml` | Create |
| `roles/android_studio/tasks/main.yml` | Create |
| `configure-linux-roles.yml` | Add role entry |
| `docs/architecture/technical-debt/technical-debt.md` | Update TD-003 |

## Key Constraints

- Install via `community.general.snap` (`name: android-studio`, `classic: true`,
  `state: present`); idempotency handled natively by the module
- Requires adding `community.general` to `requirements.yml`
- Tag `not-supported-on-vagrant-arm64` at role-entry level in
  `configure-linux-roles.yml` only (not on individual tasks)
- Mirror two-file layout of `roles/google_chrome/` (`meta/` + `tasks/` only)
- Both files MUST begin with `#SPDX-License-Identifier: MIT-0`
- `become: true` at play level only (not task level)
