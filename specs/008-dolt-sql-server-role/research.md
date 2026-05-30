# Phase 0 Research: Dolt SQL Server Ansible Role

All NEEDS CLARIFICATION items from Technical Context resolved below.

## D1 — Server mode vs embedded mode (Branch A vs Branch B)

**Decision**: Implement server mode (Branch B): a system-wide `dolt sql-server`
as a systemd service.

**Rationale**: A Step-0 spike showed embedded Dolt already serialised 10/10
concurrent writes across sibling worktrees on the developer machine (Branch A),
because beads resolves `.beads/` to the git root so worktrees share one DB.
However, that result was **never re-confirmed on a fresh VM** (no VM was
available), so Branch A remained provisional. The feature spec (the
authoritative input to this plan) selects the server-mode guarantee: FR-001..
FR-007 require an installed binary, an auto-starting systemd service, loopback
binding, and readiness for `bd init --server`. Server mode removes the
dependence on a single shared embedded DB file and makes the concurrent-write
guarantee architectural rather than incidental.

**Alternatives considered**: Branch A (embedded only, no role) — rejected as
provisional/unconfirmed on fresh VMs and not what the spec mandates. If a fresh
VM later proves embedded mode sufficient, the role can be retired; that is a
separate decision outside this plan.

## D2 — Dolt binary installation method

**Decision**: Download the architecture-specific release tarball
(`dolt-linux-amd64.tar.gz` / `dolt-linux-arm64.tar.gz`) for a **pinned**
version via `ansible.builtin.get_url`, extract with `ansible.builtin.unarchive`,
and place the `dolt` binary at `/usr/local/bin/dolt`. Architecture is selected
from `ansible_facts['architecture']` (`x86_64` → amd64, `aarch64` → arm64).
Guard every step on a `stat` of the installed binary and the target version so
re-runs are no-ops.

**Rationale**: A pinned tarball is deterministic and idempotent — the
constitution favours reproducibility (Principle I) and loud, predictable
behaviour (Principle XII). The upstream `install.sh` always fetches `latest`,
which is non-deterministic across VM rebuilds and would silently upgrade the
server. The tarball path lets the role assert the exact version it installed.
`dolt` is a single static Go binary (no runtime deps), so extraction + placement
is sufficient.

**Alternatives considered**:

- Official `install.sh` piped to bash — rejected: pulls `latest`
  (non-deterministic), runs an opaque remote script (supply-chain + Fail-Loud
  concerns).
- `apt` package — rejected: Dolt is not in Ubuntu repos.

**Key facts**: latest release at planning time is `v2.0.8`; binaries published
for linux amd64 and arm64; install target `/usr/local/bin`. Pin the version in
`defaults/main.yml` as `dolt_version`.

## D3 — `dolt sql-server` configuration (loopback-only)

**Decision**: Render `config.yaml` from a template and start the server with
`dolt sql-server --config=<path>`. Bind to loopback only:

```yaml
listener:
  host: 127.0.0.1
  port: 3306
data_dir: /var/lib/dolt
```

**Rationale**: Satisfies FR-007 (localhost only) directly — `host: 127.0.0.1`
means the listener never accepts off-host connections. Port 3306 is Dolt's
default MySQL-compatible port and what `bd init --server` expects by default,
so no extra client config is needed (FR-004). `data_dir` under `/var/lib/dolt`
is a conventional, role-owned location separate from any repo.

**Authentication**: Dolt creates a default `root` user with **no password** on
first run; auth is managed via SQL (`CREATE USER`/`GRANT`), not config fields.
Loopback-only binding makes the no-password root acceptable for a single-user
agent VM (no off-host reachability). The role provides no credentials beyond
this default (FR-004); it does not run `dolt init` or create databases (FR-006).

**Alternatives considered**: `0.0.0.0` bind — rejected, violates FR-007.
Non-default port — rejected, would force every `bd init --server` to carry
custom host/port (YAGNI, Principle IV).

## D4 — systemd unit design

**Decision**: Install a `dolt-sql-server.service` unit, `enabled: true`,
`state: started`, run as a dedicated unprivileged system user `dolt` with
`WorkingDirectory`/`data_dir` it owns. Key directives:

```ini
[Unit]
Description=Dolt SQL Server
After=network.target

[Service]
Type=simple
User=dolt
ExecStart=/usr/local/bin/dolt sql-server --config=/etc/dolt/config.yaml
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
```

**Rationale**: `WantedBy=multi-user.target` + `enabled` gives auto-start on
every boot, including the first boot after provisioning (FR-002). `Restart=
always` gives crash recovery (FR-003, SC-005). A dedicated `dolt` system user
follows least privilege. Config changes notify a handler that runs
`daemon_reload` then restarts only when the unit/config actually changed, so an
unchanged re-provision leaves the running service untouched (FR-005, SC-003).

**Alternatives considered**: user-level (`--user`) service with lingering —
rejected: more moving parts (linger enablement) for no benefit on a
single-purpose VM (YAGNI). `Type=notify` — rejected: Dolt does not implement
sd_notify; `simple` + a `wait_for` readiness gate is sufficient.

## D5 — Readiness verification (Fail Loud)

**Decision**: After starting the service, gate readiness with
`ansible.builtin.wait_for` on `127.0.0.1:3306` (bounded timeout), and `assert`
the port is listening. In Molecule's functional smoke test, additionally run a
trivial `SELECT 1` against the loopback listener and assert success.

**Rationale**: FR-004/SC-002 require the server be ready to accept
`bd init --server` immediately after provisioning. A bounded `wait_for` + assert
fails loudly (Principle XII) with the host:port in the message if the server
never comes up, rather than allowing a later silent connection failure.

## D6 — Molecule strategy under the canonical plain container

**Decision**: Keep the canonical `molecule.yml` (podman, `ubuntu:24.04`, no
PID1 systemd). Molecule validates the containerisable surface:

1. `dolt` binary installed and reports the pinned version (FR-001).
2. `/etc/dolt/config.yaml` rendered with `host: 127.0.0.1` (FR-007).
3. `dolt-sql-server.service` unit file present and well-formed.
4. **Functional smoke test**: launch `dolt sql-server --config` directly (not
   via systemd) in the container, `wait_for` the port, run `SELECT 1`, and
   assert the listener is bound to `127.0.0.1` and **not** `0.0.0.0`
   (inspect `ss -tlnp`). This exercises real install + config + loopback
   binding (FR-001, FR-004, FR-007) without PID1 systemd.

The systemd `enable`/start tasks in the role are guarded on systemd presence
(`ansible_facts['service_mgr'] == 'systemd'`). In the plain container they are
skipped (explicit environment condition, documented — not a silent skip of a
required value); on a real VM `service_mgr` is `systemd` and they run.

**FR-002 (start on boot) and FR-003 (auto-restart)** require PID1 systemd and
are validated on a Vagrant/cloud VM per Constitution Principle III, with the
procedure documented in `quickstart.md`.

**Rationale**: The canonical scaffold is shared and must not be degraded for
one role (DRY, Principle XI; molecule-testing skill rule). Splitting validation
— containerisable parts in Molecule, boot behaviour on a VM — is exactly the
fallback Principle III authorises. The functional smoke test still proves the
binary and loopback config genuinely work, so the container test is meaningful,
not a stub.

**Alternatives considered**: privileged systemd container image — rejected,
requires changing canonical `molecule.yml` (forbidden per-role; harmful
globally). Skipping functional validation and only checking file presence —
rejected, would not prove the server actually starts or binds correctly.

## D7 — Wiring into provisioning

**Decision**: Add `dolt_sql_server` to the mandatory `roles:` block of
`configure-linux-roles.yml`, after `podman`/`claude_code`/`tmux`. No tag.

**Rationale**: FR-001 requires install as part of standard base setup; the
mandatory block runs on every Linux provision. The role is container-friendly
for its install/config parts and degrades safely where systemd is absent, so it
needs no `not-supported-on-vagrant-arm64` tag.

## D8 — Version-pin maintenance (no silent drift)

**Decision**: Register `dolt_version` with the existing version-update
playbooks (`playbooks/update-versions/`). Dolt is a GitHub-release tool
(`dolthub/dolt`), so reuse the parametrized `tasks/fetch-github-release.yml`
with `github_repo: dolthub/dolt`. Version-only pin (no checksum), matching the
gitmux / Nerd Fonts precedent. Concrete changes (implemented in the tasks
phase, not this plan):

- `query-versions.yml`: slurp `roles/dolt_sql_server/defaults/main.yml`,
  extract `current_dolt_version`, `include_tasks fetch-github-release.yml`
  with `github_repo: dolthub/dolt`, save `fetched_dolt_tag`, add a status
  report, and extend the fail-if-stale condition.
- `perform-updates.yml`: fetch the same tag and
  `ansible.builtin.replace` the `dolt_version` line in the role defaults.
- `docs/architecture/version-update-playbooks.md`: add a Dolt row to the
  tracked-tools table (Role `dolt_sql_server`, version_key `dolt_version`,
  checksum_key —, source GitHub Releases API `dolthub/dolt`).

**Pin format**: store the upstream tag verbatim, `dolt_version: "v2.0.8"`
(the `tag_name` returned by the GitHub API, `v`-prefixed like
`tmux_gitmux_version: "v0.11.5"`). The release-download URL embeds the tag,
so the `v` is required for the install URL. `dolt --version` prints the
number without the `v`, so Molecule's version assertion compares against
`dolt_version | regex_replace('^v', '')`.

**Rationale**: The version-update design (FR-001/FR-002) exists precisely so
pins do not drift behind upstream security releases. A new pinned tool that is
not registered would be invisible to `query-versions.yml` and silently rot —
the exact failure the design prevents. Reusing `fetch-github-release.yml`
satisfies FR-006 (no duplicated fetch logic) and Principle XI (DRY).

**Alternatives considered**:

- Add a checksum (sha256) pin + verified `get_url` — rejected for now: no
  GitHub-release tool in the repo carries a checksum_key, and the update
  tooling has no GitHub-asset checksum fetch path. Adding one would extend the
  shared fetch task for a single tool (YAGNI, Principle IV). Loopback-only
  exposure and HTTPS download keep risk acceptable; revisit if a checksum
  fetch path is added for the GitHub-release class generally.
- Leave `dolt_version` untracked — rejected: reintroduces silent drift,
  contradicting the version-update design's reason for existing.

## Open follow-ups (tracked as issues, not blockers of this plan)

- Fresh-VM re-confirmation of Branch A vs Branch B (was provisional in the
  spike). If embedded mode is proven sufficient on a fresh VM, revisit whether
  the role is still required.
- Post-merge data migration (`bd backup sync` + `bd backup restore --force`)
  is a session/runtime action, out of role scope (FR-006).
