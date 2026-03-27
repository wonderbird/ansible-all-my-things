# Active Context: feat.backup-chrome-config

## Current focus

Branch `002-backup-chrome-config`. tasks.md is complete and
markdownlint-clean. The immediate next action is implementing US1 (MVP):
create the backup playbook and add its import to `backup.yml`, then verify
the backup manually before proceeding to US2.

## Next immediate action

**T001** — Create `playbooks/backup/google-chrome-settings.yml` (US1, MVP).
Then **T002** — add the import line to `backup.yml`. After both are done, run
the manual backup verification (quickstart.md steps 1–3) before starting US2.

## Pending tasks (in execution order)

Tasks are defined in `specs/002-backup-chrome-config/tasks.md`.

- **T001** *(start here)* — Create
  `playbooks/backup/google-chrome-settings.yml` (US1)
- **T002** — Update `backup.yml`: insert import between `cursor-settings.yml`
  and `vscode-settings.yml` (US1)
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
  `MD013: { tables: false, code_blocks: false }`
- `markdownlint` is installed globally; use `markdownlint <file>` directly.

## Important patterns learned this session

- Rule files are authoritative sources; the constitution delegates to them.
- `docs/architecture/solution-strategy.md` is the canonical location for
  technology decisions; NEVER put active technologies in CLAUDE.md.
- Memory bank is the correct place for session state and task tracking.
- After any constitution amendment, run `markdownlint` on it and check
  propagation to `.specify/templates/`.
- MD060 table separator rows must use: `| --- | --- |` not `|---|---|`.
- Fenced code blocks inside ordered list items need blank lines before and
  after the fence (MD031).
- tasks.md tag note: Chrome tags are a YAML list; Chromium uses a scalar —
  this is intentional and must not be "fixed" to match Chromium.
