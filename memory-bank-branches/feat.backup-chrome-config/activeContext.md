# Active Context: feat.backup-chrome-config

## Current focus

Branch `002-backup-chrome-config`. US1 (T001 + T002) is implemented and
committed. spec.md, plan.md, tasks.md, and quickstart.md have been updated
to capture FR-009 (missing-profile graceful-skip) and align all artifacts.
The spec is now consistent with the implementation. Ready for manual
verification on `hobbiton`.

## Next immediate action

**Manual verification** — Run backup on `hobbiton` and confirm the archive
exists and excludes ephemeral data (quickstart.md steps 1–3, US1 checkpoint).

## Pending tasks (in execution order)

Tasks are defined in `specs/002-backup-chrome-config/tasks.md`.

- **Manual verification** *(start here)* — quickstart.md steps 1–3: run
  backup, verify archive exists and excludes ephemeral data
- **T003** — Create `playbooks/restore/google-chrome-settings.yml` (US2)
- **T004** — Update `restore.yml`: insert import between `cursor-settings.yml`
  and `vscode-settings.yml` (US2)
- **T005** — Full E2E acceptance test per `quickstart.md` on AMD64 host (US3),
  including the Missing-Profile Smoke Test (FR-009 verification)
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
  If not found, fall back to `npx markdownlint-cli <file>`.
- FR-009 is implemented in `playbooks/backup/google-chrome-settings.yml` and
  now fully documented in spec.md (FR-009, US1 scenario 4), tasks.md (T001,
  T005), quickstart.md (Missing-Profile Smoke Test), and plan.md (Summary).

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
- spec.md has pre-existing MD013 (line-length) violations throughout — do not
  reflow the whole file as part of unrelated edits.
