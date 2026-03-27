# Active Context: feat.backup-chrome-config

## Current focus

Branch `002-backup-chrome-config`. T2 (commit all changes), T3 (sync CLAUDE.md
to ai-agent-workspace), and T4 (commit in ai-agent-workspace) are complete.
The immediate next action is the feature implementation.

## Next immediate action

**Implementation** — Create `playbooks/backup/google-chrome-settings.yml`,
`playbooks/restore/google-chrome-settings.yml`, and update root `backup.yml`
and `restore.yml` (alphabetical insertion between cursor and vscode entries).

## Pending tasks (in execution order)

**Implementation** *(start here)* — Create
`playbooks/backup/google-chrome-settings.yml`,
`playbooks/restore/google-chrome-settings.yml`, update `backup.yml` and
`restore.yml` (alphabetical insertion between cursor and vscode).

**T10** *(deferred)* — Consult an Ansible expert: is the backup/restore
playbook pattern (no roles) a deliberate "operational tasks → playbooks"
convention, or technical debt? Answer shapes whether to add an ADR or a
TD entry.

## Active decisions and considerations

- The `not-supported-on-vagrant-docker` tag is for **desktop apps** only, not
  all backup playbooks. Chrome needs it because Docker boxes have no desktop.
- `not-supported-on-vagrant-arm64` applies because Chrome has no ARM64 package.
- Backup/restore generic task files are assumed unmodified (Assumption A1 in
  plan.md) — revisit if implementation reveals otherwise.
- The backup/restore pattern (playbooks, not roles) is an open question (T10).
  Do not refactor until T10 is resolved.
- Constitution is at v1.1.1. Propagation check for v1.1.1: verify that
  `agent-file-template.md` needs no change due to the Documentation Standards
  table-to-list conversion. Current assessment: no change needed.
- `agent-file-template.md` section order MUST be preserved: Active Technologies
  → Project Structure → Commands → **Recent Changes** → Code Style →
  MANUAL ADDITIONS. The "Recent Changes" section must remain between "Commands"
  and "Code Style".
- `.markdownlint.json` was created at repo root during T11 with
  `MD013: { tables: false, code_blocks: false }` to suppress line-length
  errors inside tables and code blocks.
- `markdownlint` is installed globally (`npm install --global markdownlint-cli`);
  use `markdownlint <file>` directly (not `npx markdownlint`).

## Important patterns learned this session

- Rule files are authoritative sources; the constitution delegates to them
  (same pattern used for 330, 600, and now 400).
- The `agent-file-template.md` drives what `update-agent-context.sh` writes
  into CLAUDE.md — updating the template prevents unwanted sections from
  being regenerated.
- `docs/architecture/solution-strategy.md` is the canonical location for
  technology decisions; NEVER put active technologies in CLAUDE.md.
- Memory bank (this directory) is the correct place for session state and
  task tracking. CLAUDE.md should contain only timeless project guidance.
- After any constitution amendment, run `markdownlint` on the constitution
  file itself and check propagation to `.specify/templates/` before committing.
- MD060 table separator rows must use the compact style with spaces:
  `| --- | --- |` not `|---|---|`.
- Fenced code blocks inside ordered list items need blank lines before and
  after the fence to satisfy MD031.
