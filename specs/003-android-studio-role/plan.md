# Implementation Plan: Android Studio Ansible Role

**Branch**: `003-android-studio-role` | **Date**: 2026-03-31 |
**Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-android-studio-role/spec.md`

## Summary

Install Android Studio (stable) system-wide on AMD64 Ubuntu VMs via the
official snap package (`android-studio --classic`). The role is idempotent
via `community.general.snap`'s native idempotency. ARM64 hosts are skipped
gracefully using the existing `not-supported-on-vagrant-arm64` tag pattern.

## Technical Context

**Language/Version**: YAML (Ansible 2.19+)
**Primary Dependencies**: `community.general.snap` — requires adding
`community.general` to `requirements.yml` (see research.md).
**Storage**: N/A
**Testing**: Manual — `ansible-playbook` against a local Vagrant AMD64 VM;
see quickstart.md
**Target Platform**: Ubuntu Linux, AMD64 only
**Project Type**: Ansible role (infrastructure automation)
**Performance Goals**: N/A
**Constraints**: snapd must be pre-installed (standard Ubuntu); requires
outbound internet access on first provisioning run
**Scale/Scope**: Single role, two files (`meta/main.yml`, `tasks/main.yml`),
one line in `configure-linux-roles.yml`

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
| §IV Simplicity | PASS | Minimal two-file role; `community.general` added |
| | | for snap support; no speculative parameterisation |
| §V Conventional Commits | PASS | `feat:` prefix; co-authored-by trailer |
| §VI Markdown Quality | PASS | markdownlint passes on all spec artefacts |

No violations requiring Complexity Tracking justification.

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
├── meta/main.yml        # Role metadata (author, license, Ansible version)
└── tasks/main.yml       # Snap install task using community.general.snap

configure-linux-roles.yml   # Add android_studio role entry with tag
docs/architecture/technical-debt/technical-debt.md   # Update TD-003
```

**Structure Decision**: Single role, minimal layout matching `google_chrome`.
No `defaults/`, `vars/`, `handlers/`, or `templates/` directories are needed —
the role has no variables and no handlers.

### Code Conventions (matching google_chrome)

- Both `meta/main.yml` and `tasks/main.yml` MUST begin with the SPDX header:
  `#SPDX-License-Identifier: MIT-0`
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
