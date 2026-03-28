# Implementation Plan: Backup Google Chrome Browser Configuration

**Branch**: `002-backup-chrome-config` | **Date**: 2026-03-24 |
**Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002-backup-chrome-config/spec.md`

## Summary

Add Google Chrome backup and restore playbooks that are structurally similar
to the existing Chromium equivalents, differing in: source path
(`~/.config/google-chrome/Default`), archive name
(`google-chrome-backup.tar.gz`), the addition of the
`not-supported-on-vagrant-arm64` tag alongside `not-supported-on-vagrant-docker`,
and a `stat` guard in the backup playbook that checks for the profile directory,
emits an operator-visible debug message when absent, and skips backup tasks
without error (FR-009; Chromium lacks this guard — see TD-008). Both playbooks
are expected to delegate to the existing generic `backup.yml` and
`restore.yml` task files.

## Technical Context

**Language/Version**: Ansible (YAML playbooks, no version constraint beyond
what is already in use)
**Primary Dependencies**: Generic task files `playbooks/backup/backup.yml`
and `playbooks/restore/restore.yml` (existing, unchanged)
**Storage**: `configuration/home/my_desktop_user/backup/google-chrome-backup.tar.gz`
(local, overridable via `BACKUP_DIR`)
**Testing**: Manual end-to-end test on AMD64 desktop host (see Constraints)
**Target Platform**: Ubuntu Linux, AMD64 only
**Project Type**: Ansible automation (backup/restore playbooks)
**Performance Goals**: N/A — file archival, no latency target
**Constraints**: Chrome is AMD64-only. The `not-supported-on-vagrant-arm64`
tag means the playbooks are skipped on Tart (ARM64) VMs. The end-to-end
acceptance test (enable home button → backup → remove config → verify dialog
→ restore → verify no dialog) **must be executed manually on an AMD64 desktop
host**; it cannot be automated via the local VM test workflow.
**Scale/Scope**: Single desktop user, single host

## Constitution Check

| Principle | Status | Notes |
| --- | --- | --- |
| I. Idempotency | Pass | Generic task files use idempotent Ansible modules (`archive`, `fetch`, `copy`, `unarchive`, `file`). No `shell`/`command` tasks introduced. |
| II. Role-First | Pass | No new role needed. Backup/restore is intentionally implemented as playbooks delegating to generic task files — identical to all other app backups in this repo. |
| III. Test Locally Before Cloud | Pass with caveat | Chrome is AMD64-only; the `not-supported-on-vagrant-arm64` tag excludes it from Tart VMs. Acceptance test must run on AMD64 desktop host. This constraint pre-exists in the `google_chrome` role and is not introduced by this feature. |
| IV. Simplicity (YAGNI) | Pass | Two new playbook files, two import lines. No new roles, abstractions, or parameterisation beyond what exists. |
| V. Conventional Commits | Pass | One `feat:` commit per working increment. |
| VI. Markdown Quality | Pass | Plan follows ATX headings, blank-line-separated lists, no trailing whitespace. |
| VII. Structured Problem Solving | Pass | No unexpected obstacles at planning time. |

## Project Structure

### Documentation (this feature)

```text
specs/002-backup-chrome-config/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

No `data-model.md` or `contracts/` directory: this feature involves only
file archival with no data model and no external interfaces.

### Source Code (repository root)

```text
playbooks/
├── backup/
│   └── google-chrome-settings.yml   # NEW
└── restore/
    └── google-chrome-settings.yml   # NEW

backup.yml    # UPDATE: add import under # Applications, between cursor-settings.yml and vscode-settings.yml (alphabetical)
restore.yml   # UPDATE: add import under # Applications, between cursor-settings.yml and vscode-settings.yml (alphabetical)
```

**Structure Decision**: Follows the identical layout of all other application
backup/restore pairs in this repo. No new directories or roles.

## Key Design Decisions

### 1. Tag combination: `not-supported-on-vagrant-docker` + `not-supported-on-vagrant-arm64`

`not-supported-on-vagrant-docker` is applied to desktop application playbooks
because Docker-based Vagrant boxes do not include a desktop environment (images
are kept small and simple). All existing desktop app backup/restore playbooks
carry this tag; Chrome is a desktop application and requires it too.

`not-supported-on-vagrant-arm64` is additionally required because the Google
Chrome apt repository provides only AMD64 packages — Chrome cannot be installed
on ARM64 machines. The `google_chrome` role in `configure-linux-roles.yml`
already carries this tag; the backup/restore playbooks must match to be skipped
consistently on Tart (ARM64) VMs.

The Ansible `tags` field on a play accepts a list. Both tags are applied as a list:

```yaml
tags:
  - not-supported-on-vagrant-docker
  - not-supported-on-vagrant-arm64
```

### 2. Placement in backup.yml / restore.yml

Both orchestration files use alphabetical ordering within the `# Applications`
section. `google-chrome-settings.yml` sorts between `cursor-settings.yml` and
`vscode-settings.yml`.

### 3. Acceptance test is manual and AMD64-only

The end-to-end test (User Story 3 in spec) requires launching a graphical
browser. It cannot be run on a headless Vagrant VM or on ARM64. It is performed
on an AMD64 desktop host following the procedure in `quickstart.md`.

## Assumptions

### A1. Generic task files used as-is

`playbooks/backup/backup.yml` and `playbooks/restore/restore.yml` are expected
to work without modification — the only differences from the Chromium playbook
are `path`, `backup_file`, and `destination_beneath_home`. If implementation
reveals that a change is needed, modification is acceptable. Apply KISS and
YAGNI: keep the changeset as small as reasonably possible.

### A2. Acceptance test is manual and AMD64-only

The end-to-end test (User Story 3 in spec) requires launching a graphical
browser. It cannot be run on a headless Vagrant VM or on ARM64. It is performed
on an AMD64 desktop host following the procedure defined in the spec.
