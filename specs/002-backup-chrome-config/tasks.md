---

description: "Task list for feat.backup-chrome-config"
---

# Tasks: Backup Google Chrome Browser Configuration

**Input**: Design documents from `specs/002-backup-chrome-config/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: No automated tests — acceptance test is manual and AMD64-only (see
US3 and `quickstart.md`).

**Organization**: Tasks are grouped by user story. US1 (backup) and US2
(restore) are independent and can be implemented in parallel. US3 (E2E
verification) requires both to be complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

## Reference Pattern

Model all playbook files on the existing Chromium equivalents:

- Backup reference: `playbooks/backup/chromium-settings.yml`
- Restore reference: `playbooks/restore/chromium-settings.yml`

Key differences from Chromium:

- Path: `/home/{{ backup_user }}/.config/google-chrome/Default`
- Archive: `google-chrome-backup.tar.gz`
- Tags: both `not-supported-on-vagrant-docker` AND
  `not-supported-on-vagrant-arm64` (YAML list, not scalar string)

---

## Phase 1: Setup

This feature requires no project initialization or dependency changes. The
existing generic task files (`playbooks/backup/backup.yml` and
`playbooks/restore/restore.yml`) are reused unchanged. Skip directly to the
user story phases.

---

## Phase 2: Foundational

No blocking prerequisites. US1 and US2 can begin immediately.

---

## Phase 3: User Story 1 — Back Up Google Chrome Settings (Priority: P1) — MVP

**Goal**: Running the backup playbook archives the Chrome profile to
`google-chrome-backup.tar.gz`, excluding ephemeral data, as part of the
standard backup run.

**Independent Test**: Run
`ansible-playbook playbooks/backup/google-chrome-settings.yml -e backup_from_host=hobbiton`
and verify `configuration/home/my_desktop_user/backup/google-chrome-backup.tar.gz`
is created and excludes cache/history/storage/favicons.

### Implementation for User Story 1

- [x] T001 [P] [US1] Create `playbooks/backup/google-chrome-settings.yml`
  mirroring `playbooks/backup/chromium-settings.yml` with: `name: Backup
  Google Chrome settings`, `path:
  /home/{{ backup_user }}/.config/google-chrome/Default`, `backup_file:
  google-chrome-backup.tar.gz`, and tags as a YAML list:
  `not-supported-on-vagrant-docker` and `not-supported-on-vagrant-arm64`
  (identical exclusion_patterns to Chromium)
- [x] T002 [US1] Add import line to `backup.yml` under `# Applications`,
  alphabetically between `cursor-settings.yml` and `vscode-settings.yml`:
  `- import_playbook: playbooks/backup/google-chrome-settings.yml`

**Checkpoint**: US1 is complete when the archive is created and the
import appears in `backup.yml`.

---

## Phase 4: User Story 2 — Restore Google Chrome Settings (Priority: P2)

**Goal**: Running the restore playbook removes any pre-existing Chrome profile
and extracts the backup archive to `~/.config/google-chrome/Default` for
the primary desktop user.

**Independent Test**: Remove `~/.config/google-chrome/Default` on the target
host, run
`ansible-playbook playbooks/restore/google-chrome-settings.yml --limit hobbiton`,
and verify Chrome opens without the first-run dialog.

### Implementation for User Story 2

- [ ] T003 [P] [US2] Create `playbooks/restore/google-chrome-settings.yml`
  mirroring `playbooks/restore/chromium-settings.yml` with: `name: Restore
  Google Chrome settings`, `hosts: linux`, `backup_file:
  google-chrome-backup.tar.gz`, `destination_beneath_home:
  .config/google-chrome/Default`, `delete_before_beneath_home:
  [".config/google-chrome/Default"]`, and tags as a YAML list:
  `not-supported-on-vagrant-docker` and `not-supported-on-vagrant-arm64`
- [ ] T004 [US2] Add import line to `restore.yml` under `# Applications`,
  alphabetically between `cursor-settings.yml` and `vscode-settings.yml`:
  `- import_playbook: playbooks/restore/google-chrome-settings.yml`

**Checkpoint**: US2 is complete when restore extracts to the correct path and
the import appears in `restore.yml`.

---

## Phase 5: User Story 3 — End-to-End Verification (Priority: P3)

**Goal**: Confirm the full backup-restore cycle preserves settings faithfully on
an AMD64 desktop host.

**Independent Test**: Execute the full 9-step procedure in `quickstart.md` on
the AMD64 desktop host (`hobbiton`). Chrome must not show the first-run dialog
and must display the home button after restore.

### Implementation for User Story 3

- [ ] T005 [US3] Follow the manual acceptance test in
  `specs/002-backup-chrome-config/quickstart.md` on `hobbiton` (AMD64): enable
  home button → backup → remove config → verify first-run dialog → close Chrome
  → remove config again → restore → verify no dialog and home button visible.
  This task is verification only — no code changes.

**Checkpoint**: US3 is complete when all 9 quickstart steps pass on the AMD64
host.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T006 [P] Update `memory-bank-branches/feat.backup-chrome-config/activeContext.md`
  and `progress.md` to reflect implementation complete
- [ ] T007 Commit all changes with `feat:` prefix following
  `.cursor/rules/general/330-git-usage.mdc` (include `Co-authored-by` trailer
  for Claude Code)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phases 1–2**: Skipped (no setup or foundational work needed)
- **Phase 3 (US1)**: No dependencies — start immediately
- **Phase 4 (US2)**: No dependencies on US1 — can run in parallel with Phase 3
- **Phase 5 (US3)**: Depends on both Phase 3 and Phase 4 being complete
- **Phase 6 (Polish)**: Depends on Phase 5 being verified

### User Story Dependencies

- **US1 (P1)**: Independent — start immediately
- **US2 (P2)**: Independent — start immediately (parallel with US1)
- **US3 (P3)**: Depends on US1 and US2

### Parallel Opportunities

- T001 (backup playbook) and T003 (restore playbook) can be written in parallel
- T002 (backup.yml update) and T004 (restore.yml update) can be done in parallel
  after their respective playbooks are created

---

## Parallel Example

```bash
# Phase 3 and 4 in parallel:
Task T001: Create playbooks/backup/google-chrome-settings.yml
Task T003: Create playbooks/restore/google-chrome-settings.yml

# Then in parallel:
Task T002: Update backup.yml (after T001)
Task T004: Update restore.yml (after T003)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 — create backup playbook
2. Complete T002 — add import to `backup.yml`
3. **STOP and VALIDATE**: run backup and inspect archive

### Incremental Delivery

1. T001 + T002 → US1 done → run backup, verify archive
2. T003 + T004 → US2 done → run restore, verify clean restore
3. T005 → US3 done → full E2E cycle passes on AMD64 host
4. T006 + T007 → commit and update memory bank

---

## Notes

- [P] tasks = different files, no dependencies between them
- US3 is purely manual verification — no code changes required
- The `not-supported-on-vagrant-arm64` tag is a YAML list item alongside
  `not-supported-on-vagrant-docker`; do NOT use a scalar string for tags (the
  Chromium playbook uses scalar — Chrome must use a list)
- Alphabetical insertion order in `backup.yml` / `restore.yml`: chromium →
  cursor → **google-chrome** → vscode
- After any Markdown edits, run `markdownlint <file>` (rule 400)
