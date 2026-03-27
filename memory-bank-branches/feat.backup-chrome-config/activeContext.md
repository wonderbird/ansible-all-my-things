# Active Context: feat.backup-chrome-config

## Current focus

Branch `002-backup-chrome-config`. T7 (Windows OS rationale), T8 (Python
rationale), T9 (technical debt section), T11 (markdownlint all staged `.md`
files), and T12 (first-time reader review of `solution-strategy.md`) are
complete. The immediate next action is T2: commit all changes.

## Next immediate action

**T2** — Commit all changes in `ansible-all-my-things` on branch
`002-backup-chrome-config`.

## Pending tasks (in execution order)

**T2** *(start here)* — Commit all changes in `ansible-all-my-things` on
branch `002-backup-chrome-config`.

**T3** — Sync updated `CLAUDE.md` to
`/home/galadriel/Documents/Cline/ai-agent-workspace/`. Copy the rule-file
references (020, 310, 330, 400, memory-bank-branches pointer), architecture
links, and removal of --no-pager. Do NOT copy the session state section.

**T4** — Commit in `ai-agent-workspace`: `330-git-usage.mdc` fix + CLAUDE.md
sync from T3.

**T10** *(deferred)* — Consult an Ansible expert: is the backup/restore
playbook pattern (no roles) a deliberate "operational tasks → playbooks"
convention, or technical debt? Answer shapes whether to add an ADR or a
TD entry.

*(After T2)* — Implement feature: create
`playbooks/backup/google-chrome-settings.yml`,
`playbooks/restore/google-chrome-settings.yml`, update `backup.yml` and
`restore.yml` (alphabetical insertion between cursor and vscode).

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
