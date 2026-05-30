# Contract: Dolt SQL Server Config (`config.yaml`)

Rendered from `templates/config.yaml.j2` to `{{ dolt_config_path }}`
(default `/etc/dolt/config.yaml`). Defines the listener and storage contract
required by FR-004 and FR-007.

## Config contract

```yaml
listener:
  host: {{ dolt_listen_host }}   # default 127.0.0.1 — loopback only
  port: {{ dolt_listen_port }}   # default 3306
data_dir: {{ dolt_data_dir }}    # default /var/lib/dolt
```

## Guarantees

| Field | Value | Requirement |
| --- | --- | --- |
| `listener.host` | `127.0.0.1` (loopback) | FR-007 — not reachable off-host. Asserted loopback before render. |
| `listener.port` | `3306` (default) | FR-004 — matches `bd init --server` default; no client override needed. |
| `data_dir` | `/var/lib/dolt` | Role-owned, repo-agnostic storage. |

## Authentication

- Dolt auto-creates user `root` with **no password** on first run.
- Acceptable because the listener is loopback-only (FR-007): no off-host
  connection is possible.
- The role provides no additional credentials or config (FR-004); it does not
  run `dolt init` or create databases (FR-006).

## Client contract (informational — performed by developer, not the role)

A developer opts a repository in with a single command (US2, SC-004):

```bash
bd init --server          # uses default 127.0.0.1:3306, root, no password
```

Direct verification that storage landed in Dolt (US2 Independent Test):

```bash
dolt sql-client --host 127.0.0.1 --port 3306 --user root \
  --execute "SHOW DATABASES;"      # repository prefix DB present
```
