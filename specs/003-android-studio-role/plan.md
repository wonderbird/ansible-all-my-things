# Implementation Plan: Android Studio Ansible Role

**Branch**: `003-android-studio-role` | **Date**: 2026-03-31 |
**Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-android-studio-role/spec.md`

## Summary

Install Android Studio (stable) system-wide on AMD64 Ubuntu VMs via the
official snap package (`android-studio --classic`). The role also
pre-provisions the Android SDK (cmdline-tools, platform-tools, latest
platform, build-tools, emulator, platform sources) for every user in
`desktop_user_names`, so the first-launch wizard completes within
30 seconds. The role is idempotent via `community.general.snap`'s native
idempotency and `community.general.android_sdk`'s declarative state
management. ARM64 hosts are skipped gracefully using the existing
`not-supported-on-vagrant-arm64` tag pattern.

## Technical Context

**Language/Version**: YAML (Ansible 2.19+)
**Primary Dependencies**: `community.general.snap` (snap install),
`community.general.android_sdk` (SDK component install + license
acceptance), `ansible.builtin.get_url` (cmdline-tools download),
`ansible.builtin.unarchive` (cmdline-tools extraction). Requires
`community.general` in `requirements.yml` (see research.md).
**Storage**: N/A
**Testing**: Manual — `ansible-playbook` against a local Vagrant AMD64 VM;
see quickstart.md
**Target Platform**: Ubuntu Linux, AMD64 only
**Project Type**: Ansible role (infrastructure automation)
**Performance Goals**: N/A
**Constraints**: snapd must be pre-installed (standard Ubuntu); requires
outbound internet access on first provisioning run (snap + SDK downloads);
snap bundles JetBrains Runtime (JBR) at
`/snap/android-studio/current/android-studio/jbr/bin/java` — covers the
Java 17+ requirement for sdkmanager
**Scale/Scope**: Single role, three files (`meta/main.yml`,
`tasks/main.yml`, `defaults/main.yml`), one entry in
`configure-linux-roles.yml`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
| --------- | ------ | ----- |
| §I Idempotency | PASS | `community.general.snap` handles idempotency |
| | | natively; second run reports `ok`, never `changed` |
| §II Role-First | PASS | New role in `roles/android_studio/`; no logic |
| | | added to playbooks directly |
| §III Test Locally | PASS | Must test on AMD64 Vagrant VM before cloud |
| | | (see quickstart.md) |
| §IV Simplicity | PASS* | Three-file role; `defaults/main.yml` added for |
| | | cmdline-tools build number variable. SDK automation |
| | | adds complexity — justified by US4 (see Complexity |
| | | Tracking below). No speculative parameterisation |
| §V Conventional Commits | PASS | `feat:` prefix; co-authored-by trailer |
| §VI Markdown Quality | PASS | markdownlint passes on all spec artefacts |

### Complexity Tracking

| Item | Justification |
| ---- | ------------- |
| SDK pre-provisioning (US4, FR-009–FR-012) | Expands role from two to three files and adds multiple tasks (cmdline-tools download, extraction, SDK install per user). Justified by US4: without pre-provisioning, first-launch wizard takes 10–30 minutes. Complexity is bounded — all new tasks use declarative Ansible modules, no custom scripts. |

## Project Structure

### Documentation (this feature)

```text
specs/003-android-studio-role/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks — not created here)
```

No `data-model.md` (installer role — no data entities) and no `contracts/`
directory (internal automation, no external interfaces).

### Source Code (repository root)

```text
roles/android_studio/
├── defaults/main.yml    # Role variables (android_cmdlinetools_build)
├── meta/main.yml        # Role metadata (author, license, Ansible version)
└── tasks/main.yml       # Snap install + SDK pre-provisioning tasks

configure-linux-roles.yml   # Add android_studio role entry with tag
docs/architecture/technical-debt/technical-debt.md   # Update TD-003
```

**Structure Decision**: Single role, minimal layout. `defaults/main.yml`
added for the cmdline-tools build number variable (see research.md
Decision 5). No `vars/`, `handlers/`, or `templates/` directories are
needed — the role has no handlers and no templates.

### Code Conventions (matching google_chrome)

- All YAML files (`meta/main.yml`, `tasks/main.yml`, `defaults/main.yml`)
  MUST begin with the SPDX header: `#SPDX-License-Identifier: MIT-0`
- Task-level `become: true` MUST NOT be used; the play in
  `configure-linux-roles.yml` already sets `become: true`.

### meta/main.yml fields

```yaml
#SPDX-License-Identifier: MIT-0
galaxy_info:
  author: Stefan Boos
  description: Install Android Studio (Stable) on AMD64 Ubuntu Linux via snap
  company: n.a.
  issue_tracker_url: https://github.com/wonderbird/ansible-all-my-things/issues
  license: MIT
  min_ansible_version: 2.19
  galaxy_tags: []

dependencies: []
```

### defaults/main.yml fields

```yaml
#SPDX-License-Identifier: MIT-0
---
# Build number for Android SDK command-line tools.
# URL: https://dl.google.com/android/repository/commandlinetools-linux-{build}_latest.zip
# Update this value when a new cmdline-tools version is needed.
android_cmdlinetools_build: "<set during implementation>"
```

### SDK Pre-Provisioning Design (User Story 4)

SDK pre-provisioning runs after the snap install task and executes per
user in `desktop_user_names`. The task sequence for each user:

1. **Create ANDROID_HOME** — `ansible.builtin.file` ensures
   `~/Android/Sdk` exists, owned by the user.
2. **Download cmdline-tools** — `ansible.builtin.get_url` fetches the
   ZIP to a temp location. Idempotent via `checksum` or `creates:`.
3. **Extract cmdline-tools** — `ansible.builtin.unarchive` extracts to
   `~/Android/Sdk/cmdline-tools/latest/`. Idempotent via `creates:`.
4. **Install SDK components** — `community.general.android_sdk` installs
   `platform-tools`, `platforms;android-<latest>`, `build-tools;<latest>`,
   `emulator`, and `sources;android-<latest>` with
   `accept_licenses: true`. The module uses the snap-bundled JBR at
   `/snap/android-studio/current/android-studio/jbr/bin/java`.

All tasks use `become_user: "{{ item }}"` to ensure correct file
ownership (see research.md Decision 6).
