# Tech Context: feat.backup-chrome-config

## Technology stack

- **Automation**: Ansible (playbooks, roles, inventory)
- **Local test VMs**: Vagrant + Tart (macOS ARM64), Vagrant + Docker (Linux)
- **Cloud targets**: AWS EC2, Hetzner Cloud
- **Guest OS**: Ubuntu Linux (primary), Windows Server 2025 (secondary — for
  Windows-only applications)
- **Scripting**: Bash (simple scripts), Python (complex scripts; also required
  for AWS CLI support)
- **Secret management**: Ansible Vault via `ANSIBLE_VAULT_PASSWORD_FILE`

## Chrome-specific technical details

- **Profile path**: `~/.config/google-chrome/Default` (apt install, not snap)
- **Archive name**: `google-chrome-backup.tar.gz`
- **Exclusion patterns**: same as Chromium — `*Cache*`, `*cache*`, `*History*`,
  `*Local Storage*`, `*Session Storage*`, `*SharedStorage*`, `*WebStorage*`,
  `*blob_storage*`, `*Favicons*`
- **Restore destination**: `.config/google-chrome/Default` beneath home
- **Delete before restore**: `.config/google-chrome/Default`
- **Platform constraint**: AMD64 only (no ARM64 apt package exists)

## Target hosts

- **hobbiton** — primary AMD64 desktop (backup source, restore target).
  Always specify explicitly: `-e backup_from_host=hobbiton` (backup) or
  `--limit hobbiton` (restore). Default host would be `lorien`.

## Backup storage

Default location: `configuration/home/my_desktop_user/backup/`
Override with environment variable: `BACKUP_DIR`

## ai-agent-workspace relationship

Shared rule files are symlinks:

```text
.cursor/rules/general/ → ../../../../ai-agent-workspace/.cursor/rules/
```

Path: `/home/galadriel/Documents/Cline/ai-agent-workspace/`

Changes to shared rule files (e.g. `330-git-usage.mdc`) must be committed in
`ai-agent-workspace` as a separate commit (task T4).

## Markdown linting

```bash
markdownlint <file>
```

Config: `.markdownlint.json` at repo root
(`MD013: { tables: false, code_blocks: false }`).
If not installed:

```bash
npm install --global markdownlint-cli
```
