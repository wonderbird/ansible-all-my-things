# dolt_sql_server

Installs the [Dolt](https://github.com/dolthub/dolt) binary at a pinned version
and runs `dolt sql-server` as a systemd service on Ubuntu. The server binds to
loopback (`127.0.0.1:3306`) and restarts on failure. Multiple parallel agent
sessions on the same VM can write task-tracking data simultaneously without
lock-contention failures.

**Boundary**: this role installs the binary and manages the service only. It
does not initialize databases, restore or back up data, or configure any
repository's task-tracking settings — those are session-level operations.

See [`specs/008-dolt-sql-server-role/quickstart.md`](../../specs/008-dolt-sql-server-role/quickstart.md)
for build, test, and validation procedures.

## Variables

All variables have safe defaults. None are required from the caller.

| Variable | Type | Default | Description |
| -------- | ---- | ------- | ----------- |
| `dolt_version` | string | `"v2.0.8"` | Pinned Dolt release tag (`v`-prefixed). |
| `dolt_install_path` | string | `/usr/local/bin/dolt` | Path where the `dolt` binary is placed. |
| `dolt_listen_host` | string | `127.0.0.1` | Listener address. Must be `127.0.0.1` (loopback only; asserted). |
| `dolt_listen_port` | integer | `3306` | Listener port. Must be 1–65535 (asserted). |
| `dolt_data_dir` | string | `/var/lib/dolt` | Server data directory. |
| `dolt_config_dir` | string | `/etc/dolt` | Directory containing `config.yaml`. |
| `dolt_config_path` | string | `"{{ dolt_config_dir }}/config.yaml"` | Full path to the rendered server config. |
| `dolt_service_user` | string | `dolt` | System user the service runs as. |
| `dolt_service_name` | string | `dolt-sql-server` | Systemd service unit name. |
| `dolt_readiness_timeout` | integer | `30` | Seconds to wait for the server to accept connections after start. |

Overriding `dolt_listen_host` to a non-loopback address is rejected by an
`assert` (FR-007).

## Postconditions

On a successful run against a systemd host:

- `dolt` binary at `dolt_install_path` reports the pinned version.
- `dolt-sql-server.service` is **enabled** (starts on every boot) and
  **active**, with `Restart=always` (auto-restarts on failure).
- Server listens on `127.0.0.1:3306` only — not on any external interface.
- Server accepts connections and is ready for `bd init --server` with no
  additional server-side configuration.
- Re-running the role on an already-provisioned host makes no changes and does
  not restart the running service.

## Developer opt-in (US2)

After provisioning, a developer opts a git repository into Dolt-backed task
tracking with a single command:

```bash
cd /path/to/git/repo      # repository must have at least one commit
bd init --server           # connects to 127.0.0.1:3306, root, no password
```

Verify that tasks are stored in Dolt (not an embedded fallback):

```bash
bd create --title="Test task" --type=task
dolt sql-client --host 127.0.0.1 --port 3306 --user root \
  --execute "SHOW DATABASES;"   # repository-prefix database should be present
```

This is a per-repository developer action. The role does not perform it
automatically and has no knowledge of any specific repository.

## Non-goals

- Database initialization (`dolt init`) — handled by `bd bootstrap` at session start.
- Data restore or backup — handled by `bd dolt push` / `bd dolt pull`
  at session boundaries.
- Repository task-tracking configuration (`bd init --server`) — a
  one-time developer action.
- Multi-host or remote server setup — the service is local to each VM.
