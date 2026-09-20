# Quickstart: Version Update Playbooks

## Prerequisites

- Ansible-core >= 2.19.0 installed and active (project `.venv`)
- Network access to upstream sources (GitHub, Flutter CDN, SDKMAN API, Google Android developer page)
- Run from repository root

## Apply version updates

```bash
ansible-playbook playbooks/update-versions/perform-updates.yml
```

Updates all stale version pins and paired checksums in role `defaults/main.yml` files. No commits are created. Review the diff (`git diff`) and commit manually.

## Typical workflow

```bash

# 2. If stale pins found, apply updates
ansible-playbook playbooks/update-versions/perform-updates.yml

# 3. Review changes
git diff roles/*/defaults/main.yml

# 4. Commit using the project commit convention
# (see commit skill)
```

## Known constraints

- GitHub API requests are unauthenticated (60 requests/hour limit — sufficient for manual runs)
- Android cmdline-tools version is scraped from an HTML page; if Google restructures the page the task will fail with a clear error (see TD-009)
- Java tracking updates the latest patch of the currently pinned major version (Java 21); major version upgrades require a manual defaults edit
