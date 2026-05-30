# Phase 1 Data Model: Dolt SQL Server Ansible Role

This role configures infrastructure, not application data. The "entities" are
the role's configuration surface (variables) and the on-host artefacts it
manages. Spec Key Entities map to the managed artefacts below.

## Role variables (`defaults/main.yml`)

| Variable | Type | Default | Validation | Purpose |
| --- | --- | --- | --- | --- |
| `dolt_version` | string | `v2.0.8` | non-empty; `v`-prefixed upstream tag | Pinned Dolt release to install (D2). `v`-prefixed (GitHub `tag_name`) — embeds in download URL; version assert strips `^v`. Tracked by `playbooks/update-versions/` (D8). |
| `dolt_install_path` | path | `/usr/local/bin/dolt` | absolute path | Installed binary location. |
| `dolt_listen_host` | string | `127.0.0.1` | MUST be a loopback address | Listener bind address (FR-007). Asserted loopback. |
| `dolt_listen_port` | int | `3306` | 1–65535 | Listener port; default matches `bd init --server`. |
| `dolt_data_dir` | path | `/var/lib/dolt` | absolute path | Server data directory; role-owned, repo-agnostic. |
| `dolt_config_dir` | path | `/etc/dolt` | absolute path | Holds rendered `config.yaml`. |
| `dolt_config_path` | path | `{{ dolt_config_dir }}/config.yaml` | absolute path | `--config` argument. |
| `dolt_service_user` | string | `dolt` | valid system username | Unprivileged user running the service. |
| `dolt_service_name` | string | `dolt-sql-server` | systemd unit name | Unit + handler reference. |
| `dolt_readiness_timeout` | int (s) | `30` | > 0 | `wait_for` bound on port readiness (D5). |

### Validation rules (Fail Loud — Principle XII)

- `assert` `dolt_version` is defined and non-empty before download.
- `assert` `dolt_listen_host` resolves to a loopback address (`127.0.0.0/8` or
  `localhost`) — guards FR-007 against accidental `0.0.0.0`.
- `assert` `dolt_listen_port` is an integer in range.
- After start (where systemd present) or after smoke-launch (container),
  `wait_for` `{{ dolt_listen_host }}:{{ dolt_listen_port }}` then `assert`
  reachable; failure message names host:port.

## Managed artefacts (state transitions)

### 1. Dolt binary

- **Absent → Present**: download tarball for `ansible_facts['architecture']`,
  extract, place at `dolt_install_path` (mode `0755`). Guarded by `stat` +
  version check.
- **Present (correct version) → Present**: no-op (idempotent).
- **Present (wrong version) → Present (pinned)**: re-download/replace.

Maps to spec entity **VM Provisioning** (install software) and FR-001.

### 2. Server config (`/etc/dolt/config.yaml`)

- **Absent → Present**: rendered from `config.yaml.j2` with loopback listener +
  data_dir.
- **Changed**: re-rendered → notifies restart handler.
- **Unchanged**: no-op, no restart (FR-005 / SC-003).

Maps to spec entity **Shared Write Service** (configuration) and FR-007.

### 3. Service user + data dir

- `dolt` system user created (`system: true`, no login shell).
- `dolt_data_dir` and `dolt_config_dir` created, owned by `dolt`.

### 4. systemd unit (`/etc/systemd/system/dolt-sql-server.service`)

- **Absent → Present + enabled + started**: rendered from
  `dolt-sql-server.service.j2`; `daemon_reload`; `enabled: true`;
  `state: started`. Only where `service_mgr == 'systemd'` (D6).
- **Changed**: re-render → `daemon_reload` + restart via handler.
- **Unchanged**: no-op, running service untouched (FR-005).

Maps to spec entity **Shared Write Service** (lifecycle) and FR-002/FR-003.

## Out-of-model (explicitly NOT managed — FR-006)

- Databases / `dolt init` — owned by `bd bootstrap`.
- Data restore — owned by `bd dolt pull` / `bd bootstrap`.
- Data backup — owned by `bd dolt push`.
- Per-repository `bd init --server` configuration — developer opt-in (US2).
