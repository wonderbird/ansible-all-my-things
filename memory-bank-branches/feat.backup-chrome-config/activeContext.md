# Active Context: feat.backup-chrome-config

## Current focus

Branch `002-backup-chrome-config`. US1 (T001 + T002) is implemented and under
manual testing. During testing a new requirement was discovered: the backup
playbook must check whether the Chrome profile directory exists and emit a
clear operator-visible message when it does not. This requirement must be
persisted in `spec.md` before resuming testing.

## Next immediate action

**Update `spec.md`** — add the missing-profile graceful-skip behaviour as a
new functional requirement and update the relevant edge case entry. Once
spec.md is committed, resume manual backup verification (quickstart.md steps
1–3).

## Pending tasks (in execution order)

Tasks are defined in `specs/002-backup-chrome-config/tasks.md`.

- **spec.md update** *(start here)* — persist the missing-profile requirement:
  add an FR for the `stat` guard + `debug` message in the backup playbook
- **Manual verification** — Run backup on `hobbiton`, verify archive exists
  and excludes ephemeral data (US1 checkpoint before US2)
- **T003** — Create `playbooks/restore/google-chrome-settings.yml` (US2)
- **T004** — Update `restore.yml`: insert import between `cursor-settings.yml`
  and `vscode-settings.yml` (US2)
- **T005** — Full E2E acceptance test per `quickstart.md` on AMD64 host (US3)
- **T006** — Update memory bank (activeContext.md, progress.md)
- **T007** — Commit with `feat:` prefix and `Co-authored-by` trailer
- **T10** *(deferred)* — Ansible expert consult on backup/restore playbooks
  vs. roles

## Active decisions and considerations

- Tags on Chrome playbooks MUST be a YAML list (not a scalar string like
  Chromium), because two tags are needed:

  ```yaml
  tags:
    - not-supported-on-vagrant-docker
    - not-supported-on-vagrant-arm64
  ```

- Backup/restore generic task files are assumed unmodified (Assumption A1 in
  plan.md) — revisit if implementation reveals otherwise.
- The backup/restore pattern (playbooks, not roles) is an open question (T10).
  Do not refactor until T10 is resolved.
- `.markdownlint.json` was created at repo root:
  `MD013: { tables: false, code_blocks: false }`. MD024 and headings exceptions
  are NOT in the config — subheadings in technical-debt.md are made unique with
  TD-ID prefixes (e.g. `### TD-001: Description`) instead.
- `markdownlint` is installed globally; use `markdownlint <file>` directly.
- The missing-profile requirement discovered during testing: the backup
  playbook must use `stat` to check whether
  `~/.config/google-chrome/Default` exists, emit a clear `debug` message
  when absent, and skip the backup tasks. This is already implemented in
  `playbooks/backup/google-chrome-settings.yml` but not yet in `spec.md`.
  TD-008 records the same gap for the Chromium playbook.

## Important patterns learned this session

- Rule files are authoritative sources; the constitution delegates to them.
- `docs/architecture/solution-strategy.md` is the canonical location for
  technology decisions; NEVER put active technologies in CLAUDE.md.
- Memory bank is the correct place for session state and task tracking.
- After any constitution amendment, run `markdownlint` on it and check
  propagation to `.specify/templates/`.
- MD024 must be satisfied by making headings unique, not by suppressing the
  rule. Use TD-ID prefixes for repeated subheadings in technical-debt.md.
- Fenced code blocks inside ordered list items need blank lines before and
  after the fence (MD031).
- Chrome backup tags are a YAML list; Chromium uses a scalar — intentional,
  must not be "corrected" to match Chromium.
- New requirements discovered during testing must be persisted in `spec.md`
  before resuming testing or moving to the next story.
