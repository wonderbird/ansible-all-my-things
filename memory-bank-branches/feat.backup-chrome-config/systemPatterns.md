# System Patterns: feat.backup-chrome-config

## Backup / restore pattern

Application backup/restore is implemented as thin playbooks in
`playbooks/backup/` and `playbooks/restore/` that delegate to two shared task
files:

- `playbooks/backup/backup.yml` — archives a path to a `.tar.gz` on the
  control node, excluding specified patterns
- `playbooks/restore/restore.yml` — uploads archive to target, optionally
  deletes paths before extracting, extracts as target user

Each application playbook supplies only: `path`, `backup_file`,
`exclusion_patterns` (backup) and `backup_file`, `destination_beneath_home`,
`delete_before_beneath_home` (restore).

The main `backup.yml` and `restore.yml` at the repo root import all application
playbooks in **alphabetical order** within the `# Applications` section.

## Tag conventions

- `not-supported-on-vagrant-docker` — applied to **desktop application**
  playbooks. Docker Vagrant boxes omit a desktop environment to keep images
  small. This is NOT a generic "all backup playbooks" tag — it is specifically
  for desktop apps.
- `not-supported-on-vagrant-arm64` — applied to AMD64-only software. Chrome has
  no ARM64 Linux package; this tag skips it on Tart (ARM64) VMs.
- When a play needs both tags, use a YAML list (not a scalar string):

  ```yaml
  tags:
    - not-supported-on-vagrant-docker
    - not-supported-on-vagrant-arm64
  ```

## Role-first organisation (Principle II)

Roles live in `roles/`. Playbooks orchestrate roles only — no direct task
lists. Exception: the backup/restore playbooks are a deliberate thin-delegation
pattern (not a role), which pre-dates the constitution. See TD-002 for the
legacy debt around other playbooks that violate this principle. Whether
backup/restore should become roles is an open question (see task T10 —
Ansible expert consultation).

## Rule-file authority pattern

The constitution defers format/tooling details to dedicated rule files:

- `.cursor/rules/general/330-git-usage.mdc` — authoritative for commit format,
  co-authorship, `--no-pager`
- `.cursor/rules/general/600-documentation-strategy.mdc` — authoritative for
  documentation folder structure and migration policy
- `.cursor/rules/general/400-markdown-formatting.mdc` — authoritative for
  markdown linting (run `markdownlint <file>` after every edit)

Rule files in `.cursor/rules/general/` are symlinks to the shared
`ai-agent-workspace` repo at
`/home/galadriel/Documents/Cline/ai-agent-workspace/.cursor/rules/`.

## Constitution governance

Any amendment to `.specify/memory/constitution.md` requires:

1. A Sync Impact Report comment added above the version line
2. A semantic version bump: MAJOR (breaking), MINOR (new guidance), PATCH
   (clarification/typo)
3. Updated `Last Amended` date
4. Run `markdownlint .specify/memory/constitution.md` and fix all errors
5. Propagation check across `.specify/templates/` — in particular verify that
   `agent-file-template.md` section order is unchanged: Active Technologies →
   Project Structure → Commands → **Recent Changes** → Code Style →
   MANUAL ADDITIONS

Current constitution version: **1.1.1** (Last Amended: 2026-03-26)
