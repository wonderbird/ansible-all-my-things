# Quickstart: Dolt SQL Server Ansible Role

How to build, test, and validate the `dolt_sql_server` role.

## Prerequisites

Project `.venv` with Molecule (re-create whenever absent — it is git-ignored):

```bash
# from repo root
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy install -r requirements.yml
```

## Scaffold the role

```bash
bash scripts/new-role.sh dolt_sql_server
```

Then customise `meta/main.yml` (`role_name: dolt_sql_server`), `defaults/`,
`tasks/`, `templates/`, `handlers/`, and the Molecule `converge.yml` /
`verify.yml`. Do not hand-edit `molecule.yml` or `prepare.yml` (canonical).

## Local validation — Molecule (containerisable surface)

```bash
cd roles/dolt_sql_server
molecule test
```

Covers create → prepare → converge → idempotence → verify → destroy. Asserts:

- `dolt --version` reports the pinned `dolt_version` (FR-001).
- `/etc/dolt/config.yaml` has `host: 127.0.0.1` (FR-007).
- `dolt-sql-server.service` unit present with `Restart=always` and
  `WantedBy=multi-user.target`.
- **Functional smoke test**: server launched directly from the config binds to
  `127.0.0.1:3306` (verified via `ss -tlnp`, asserted NOT `0.0.0.0`) and
  answers `SELECT 1` (FR-004, FR-007).
- Idempotence: second converge reports no changes (FR-005).

The two podman schema warnings are expected and acceptable.

## VM validation — systemd boot & restart (Principle III)

The plain Molecule container has no PID1 systemd, so FR-002 (start on boot)
and FR-003 (auto-restart) are validated on a Vagrant/cloud VM. Follow
`CONTRIBUTING.md` to isolate the role in `configure-linux-roles.yml`, then:

```bash
# 1. Provision a fresh local VM and run the playbook (see CONTRIBUTING.md)

# 2. Service enabled + active after provisioning (FR-002, SC-002)
systemctl is-enabled dolt-sql-server   # → enabled
systemctl is-active  dolt-sql-server   # → active

# 3. Loopback-only binding (FR-007)
ss -tlnp | grep 3306                   # bound to 127.0.0.1:3306, not 0.0.0.0

# 4. Survives reboot, ready before login (FR-002, SC-002)
sudo reboot
# after reconnect:
systemctl is-active dolt-sql-server    # → active

# 5. Auto-restart after crash (FR-003, SC-005)
sudo systemctl kill -s SIGKILL dolt-sql-server
sleep 3
systemctl is-active dolt-sql-server    # → active (restarted)

# 6. Idempotent re-provision does not disrupt the service (FR-005, SC-003)
#    re-run the playbook; confirm no service restart and changed=0 for the role
```

## Developer opt-in (post-provisioning, not part of the role — US2)

```bash
cd /path/to/git/repo            # has >=1 commit
bd init --server                # connects to 127.0.0.1:3306
bd create --title="..." --type=task
dolt sql-client --host 127.0.0.1 --port 3306 --user root \
  --execute "SHOW DATABASES;"   # repo-prefix DB confirms server-backed storage
```

## Wire into provisioning

Add `dolt_sql_server` to the mandatory `roles:` block of
`configure-linux-roles.yml` so it runs during base VM setup (FR-001).

## Keep the version pin current

`dolt_version` is tracked by the version-update playbooks (GitHub-release
source `dolthub/dolt`). Detect drift and apply updates:

```bash
# Report stale pins (exits non-zero if any tool, incl. Dolt, is stale)
ansible-playbook playbooks/update-versions/query-versions.yml

# Rewrite pins in role defaults (no commit created)
ansible-playbook playbooks/update-versions/perform-updates.yml
git diff roles/dolt_sql_server/defaults/main.yml   # review, then commit
```

Wiring this in requires adding a Dolt entry to both playbooks and a row to
`docs/architecture/version-update-playbooks.md`; the GitHub-release fetch task
is reused unchanged.
