# Contract: Role Interface (`dolt_sql_server`)

The role's public contract: how callers invoke it and what they may override.

## Invocation

```yaml
# configure-linux-roles.yml (mandatory roles block)
roles:
  - podman
  - claude_code
  - tmux
  - dolt_sql_server      # added by this feature
```

Or standalone:

```yaml
- hosts: linux
  become: true
  roles:
    - role: dolt_sql_server
```

## Inputs (overridable variables)

All inputs have safe defaults (see `data-model.md`). None are required from the
caller. Commonly overridden:

| Variable | Default | When to override |
| --- | --- | --- |
| `dolt_version` | `v2.0.8` | Pin a different Dolt release (`v`-prefixed upstream tag). |
| `dolt_data_dir` | `/var/lib/dolt` | Relocate server data. |
| `dolt_listen_port` | `3306` | Avoid a port clash (rare). |

Overriding `dolt_listen_host` to a non-loopback value is rejected by an
`assert` (FR-007).

## Guarantees (postconditions)

On success against a systemd host:

1. `dolt` binary at `/usr/local/bin/dolt` reports the pinned version
   (`dolt_version` with the leading `v` stripped) (FR-001).
2. `dolt-sql-server.service` is **enabled** (starts on boot, FR-002) and
   **active** (FR-002), with `Restart=always` (FR-003).
3. Server listens on `127.0.0.1:3306` only — not on any external interface
   (FR-007).
4. Server accepts connections / is ready for `bd init --server` with no
   further server-side configuration (FR-004).
5. Re-running the role on an already-provisioned host makes no changes and does
   not restart the running service (FR-005 / SC-003).

## Version maintenance

`dolt_version` is tracked by `playbooks/update-versions/` as a GitHub-release
tool (`dolthub/dolt`). `query-versions.yml` reports it stale when a newer
release exists; `perform-updates.yml` rewrites the pin in `defaults/main.yml`.
The maintainer reviews `git diff roles/` and commits manually. See
`docs/architecture/version-update-playbooks.md`.

## Non-goals (FR-006)

The role does NOT run `dolt init`, create databases, restore, or back up data,
and does NOT configure any repository's `bd` settings.

## Failure modes (Fail Loud — Principle XII)

| Condition | Behaviour |
| --- | --- |
| `dolt_version` empty/undefined | `assert` fails before download. |
| `dolt_listen_host` non-loopback | `assert` fails (protects FR-007). |
| Tarball download fails | `get_url` fails the play (no silent fallback). |
| Server not listening within `dolt_readiness_timeout` | `wait_for` + `assert` fail naming `host:port`. |
