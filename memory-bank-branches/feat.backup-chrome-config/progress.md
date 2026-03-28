# Progress: feat.backup-chrome-config

## What works

- **spec.md** — complete and committed (commit `c4ffcca`); includes FR-009
  (missing-profile graceful-skip), US1 scenario 4, and Session 2026-03-28
  clarifications
- **plan.md** — complete and committed (`c4ffcca`); Summary updated to reflect
  stat guard as a structural difference from Chromium (references TD-008)
- **quickstart.md** — complete and committed (`c4ffcca`); includes
  Missing-Profile Smoke Test section for FR-009 verification
- **tasks.md** — complete and committed (`c4ffcca`); T001 description extended
  to require FR-009 stat guard; T005 extended to reference Missing-Profile
  Smoke Test
- **research.md** — complete and markdownlint-clean (committed)
- **docs/architecture/solution-strategy.md** — arc42 Section 4, complete
  (committed)
- **docs/architecture/technical-debt/technical-debt.md** — TD-008 added;
  markdownlint-clean (committed)
- **.markdownlint.json** — `MD013: { tables: false, code_blocks: false }`
  (committed)
- **.specify/memory/constitution.md** — updated to v1.1.1 (committed)
- **.specify/templates/agent-file-template.md** — updated (committed)
- **CLAUDE.md** — updated with rule file references and architecture pointers
  (committed)
- **.cursor/rules/general/330-git-usage.mdc** (symlink source) — fixed and
  updated (committed in ai-agent-workspace)
- **memory-bank-branches/feat.backup-chrome-config/** — all 6 files current
- **playbooks/backup/google-chrome-settings.yml** — implemented (US1):
  `stat` guard for missing profile, `debug` message when absent, backup
  tasks skipped when directory does not exist (FR-009 implemented)
- **backup.yml** — import added alphabetically between cursor and vscode
  (committed)

## What is left to build

Tasks are tracked in `specs/002-backup-chrome-config/tasks.md`.

- **Manual verification** *(START HERE)* — quickstart.md steps 1–3: run
  backup on `hobbiton`, verify archive exists and excludes ephemeral data
  (US1 checkpoint)
- **T003** — Create `playbooks/restore/google-chrome-settings.yml` (US2)
- **T004** — Update `restore.yml` with import (US2)
- **T005** — Full E2E acceptance test on AMD64 host (US3, manual), including
  Missing-Profile Smoke Test for FR-009 verification
- **T006–T007** — Memory bank update and final commit

## Known issues

None. All committed changes are consistent and markdownlint-clean. spec.md
has pre-existing MD013 prose line-length violations throughout (pre-date this
feature branch); these are not regressions.
