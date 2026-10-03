# Quickstart: Version Update Playbooks

## Prerequisites

- Ansible-core >= 2.19.0 installed and active (project `.venv`)
- Network access to every tracked tool's upstream source (see
  `playbooks/update-versions/vars/tools.yml`)
- Run from repository root

## Apply version updates

```bash
ansible-playbook playbooks/update-versions/perform-updates.yml
```

Updates all stale version pins and paired checksums in role `defaults/main.yml`
files. No commits are created. Review the diff (`git diff`) and commit manually.

## Typical workflow

```bash
# 1. Apply updates
ansible-playbook playbooks/update-versions/perform-updates.yml

# 2. Review changes
git diff roles/*/defaults/main.yml

# 3. Commit using the project commit convention
# (see commit skill)
```

## Known constraints

- GitHub API requests are unauthenticated (60 requests/hour limit — sufficient
  for manual runs)
- Android cmdline-tools version is scraped from an HTML page; if Google
  restructures the page the task will fail with a clear error
- Java tracking updates the latest patch of the currently pinned major version;
  major version upgrades require a manual defaults edit
