# Active Context: feat.backup-chrome-config

## Current focus

Branch `002-backup-chrome-config`. All implementation tasks complete and
tested. US1 (backup), US2 (restore), US3 (E2E acceptance test), and the
FR-009 Missing-Profile Smoke Test have all passed on `hobbiton` (AMD64).
Ready for final commit (T007) and PR to main.

## Next immediate action

**T007** — Final commit with `feat:` prefix and `Co-authored-by` trailer,
then open PR to main.

## Pending tasks (in execution order)

Tasks are defined in `specs/002-backup-chrome-config/tasks.md`.

- **T007** *(start here)* — Final commit and PR to main
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
  fully verified via the Missing-Profile Smoke Test.
- The first-run configuration dialog did not appear when Chrome was launched
  with no `Default` profile — Chrome tracks first-run state outside of
  `~/.config/google-chrome/Default`. The home button absence/presence is the
  reliable E2E indicator.

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
- Chrome's first-run dialog state is stored outside `Default/`; home button
  visibility is the correct E2E restore indicator.
