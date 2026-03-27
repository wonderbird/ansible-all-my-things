# Project Brief: feat.backup-chrome-config

## Project

`ansible-all-my-things` — Ansible automation for provisioning and maintaining
personal infrastructure: Linux desktop (hobbiton), cloud VMs (AWS EC2, Hetzner),
and a Windows Server VM.

## Feature Scope

**Primary**: Add backup and restore playbooks for the Google Chrome browser
configuration, following the same pattern used for Chromium.

**Secondary (same branch)**: A governance and documentation cleanup workstream
ran in parallel — fixing rule file inconsistencies, creating
`docs/architecture/solution-strategy.md`, and updating the constitution to
v1.1.0.

## Core Requirements

### Chrome backup/restore

- Archive `~/.config/google-chrome/Default` for the primary desktop user
- Exclude ephemeral data (same patterns as Chromium: cache, history, storage,
  favicons)
- Restore cleanly (delete before extract)
- Tags: `not-supported-on-vagrant-docker` AND `not-supported-on-vagrant-arm64`
  (Chrome is AMD64-only, desktop app)
- Import into `backup.yml` and `restore.yml` in alphabetical order
  (between `cursor-settings.yml` and `vscode-settings.yml`)
- Delegate to existing generic `playbooks/backup/backup.yml` and
  `playbooks/restore/restore.yml` task files (assumption: no modification needed)

### Governance cleanup

- Constitution updated to v1.1.0
- Rule files designated as authoritative sources: `330-git-usage.mdc` (commits),
  `600-documentation-strategy.mdc` (docs)
- `docs/architecture/solution-strategy.md` created (arc42 Section 4)
- CLAUDE.md updated with rule pointers and architecture links

## Success Criteria

See `specs/002-backup-chrome-config/spec.md` for the full acceptance test
(configure home button → backup → remove config → verify dialog → restore →
verify no dialog + home button visible). Test must run on AMD64 desktop host.

## Git Branch

`002-backup-chrome-config` on remote `origin`
