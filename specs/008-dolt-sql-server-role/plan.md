# Implementation Plan: Dolt SQL Server Ansible Role

**Branch**: `008-dolt-sql-server-role` | **Date**: 2026-05-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-dolt-sql-server-role/spec.md`

## Summary

Provide a shared, concurrent-write task-tracking backend on each ephemeral
agent VM by installing the Dolt binary and running `dolt sql-server` as a
systemd service that starts on every boot, binds to loopback only, and
restarts on failure. The role installs and starts the server only; it does
not initialise databases, restore, or back up data (those belong to
`bd bootstrap` / `bd dolt push` at session start/end). Delivered as a new
role `roles/dolt_sql_server` wired into `configure-linux-roles.yml`, with a
Molecule scenario covering the containerisable surface and a Vagrant/cloud-VM
procedure for the systemd-on-boot behaviour that a plain container cannot
exercise. The pinned `dolt_version` is registered with the existing
version-update playbooks (`playbooks/update-versions/`) as a GitHub-release
tool so the pin does not silently drift behind upstream security releases.

## Technical Context

**Language/Version**: YAML — Ansible 2.19+ (`min_ansible_version: 2.19`)
**Primary Dependencies**: `ansible.builtin` (apt, get_url, unarchive, template,
systemd_service, user, file, stat, wait_for, assert); no new Galaxy
collections required
**Storage**: Dolt SQL server data directory on the VM (e.g.
`/var/lib/dolt`); ephemeral — recreated each VM, hydrated by `bd bootstrap`
**Testing**: Molecule (podman driver, `docker.io/library/ubuntu:24.04`) for
the containerisable surface; Vagrant/cloud VM for systemd-on-boot per
Constitution Principle III
**Target Platform**: Ubuntu Linux (jammy, noble) on AWS EC2 / Hetzner /
local Vagrant; arch amd64 and arm64
**Project Type**: Ansible role (single-purpose infrastructure automation)
**Performance Goals**: Server ready within the normal VM boot sequence
(SC-002); concurrent writes from parallel sessions with zero lock-contention
failures (SC-001) — guaranteed architecturally by server mode, not benchmarked
**Constraints**: Loopback-only listener (FR-007); idempotent re-provisioning
without service disruption (FR-005); no credentials/config beyond what the
role provides (FR-004); install + service only — no DB init/restore/backup
(FR-006)
**Scale/Scope**: One server per VM, single OS user, single localhost port
(3306). Not a remote/shared server.
**Version maintenance**: `dolt_version` pinned in `defaults/main.yml` and
tracked by `playbooks/update-versions/` — GitHub-release source
(`dolthub/dolt`), reusing `tasks/fetch-github-release.yml`; version-only (no
checksum), matching the gitmux / Nerd Fonts precedent in
`docs/architecture/version-update-playbooks.md`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
| --- | --- | --- |
| I. Idempotency (NON-NEGOTIABLE) | PASS | Pinned-version tarball install guarded by `stat`/`creates`; `template` + `systemd_service` are natively idempotent; no `blockinfile` newline params. Re-run does not disrupt running service (FR-005). |
| II. Role-First Organisation | PASS | Standalone role `roles/dolt_sql_server`; playbook only orchestrates. Molecule scenario in `molecule/default/`. Systemd-on-boot validated on VM (Principle III) — see Complexity Tracking. |
| III. Test Locally Before Cloud | PASS | `molecule test` covers install/config/unit/loopback + functional server smoke test; VM procedure in quickstart covers systemd boot/restart. |
| IV. Simplicity (YAGNI) | PASS | Single server, single user, defaults only. No remote-server, no Dolt Hub, no multi-DB provisioning. Version pinned as one variable. |
| V. Conventional Commits & Traceability | PASS | `commit` skill invoked before each commit. |
| VI. Markdown Quality | PASS | `format-markdown` run at task close. |
| VII. Structured Problem Solving | PASS | `fix-problem` invoked on obstacles. |
| VIII. No Untracked Technical Debt | PASS | Findings tracked as blocking issues at source priority. |
| IX. CI/CD Pipeline Security | N/A | No CI workflow or artefact publish introduced by this role. |
| X. No External-System References | PASS | No beads IDs in role files, templates, or these specs. |
| XI. Avoid Duplication (DRY) | PASS | Reuses canonical Molecule scaffold; config/unit values centralised in `defaults/main.yml`; no copied logic. Version-update integration reuses the parametrized `fetch-github-release.yml` (no new fetch logic) per FR-006 of the version-update design. |
| XII. Fail Loud | PASS | `assert` validates required vars and server readiness (`wait_for` the loopback port); no `default('')`/`ignore_errors` masking; systemd guard is an explicit environment condition, not a silent skip of a required value. |

**Initial gate: PASS.** One containerisation limitation justified in
Complexity Tracking (systemd-on-boot needs PID1 systemd, unavailable in the
canonical plain container).

## Project Structure

### Documentation (this feature)

```text
specs/008-dolt-sql-server-role/
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── systemd-service.md
│   ├── server-config.md
│   └── role-interface.md
├── checklists/
│   └── requirements.md  # pre-existing
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
roles/dolt_sql_server/
├── README.md                     # role usage + boundary
├── defaults/main.yml             # dolt_version, port, host, data_dir, user, paths
├── meta/main.yml                 # galaxy_info (namespace: wonderbird), platforms
├── handlers/main.yml             # restart dolt-sql-server (daemon_reload + restart)
├── tasks/main.yml                # install binary → config → unit → enable/start
├── templates/
│   ├── config.yaml.j2            # dolt sql-server config (loopback listener)
│   └── dolt-sql-server.service.j2 # systemd unit (Restart=always)
└── molecule/default/
    ├── molecule.yml              # canonical (podman, ubuntu:24.04)
    ├── prepare.yml               # canonical bootstrap
    ├── converge.yml              # apply role
    └── verify.yml                # assert install/config/unit/loopback + smoke test

configure-linux-roles.yml         # add `dolt_sql_server` to roles list

playbooks/update-versions/
├── query-versions.yml            # add Dolt: slurp defaults, fetch, report, fail-if-stale
└── perform-updates.yml           # add Dolt: fetch + replace dolt_version
# tasks/fetch-github-release.yml reused as-is (github_repo: dolthub/dolt)

docs/architecture/version-update-playbooks.md  # add Dolt row to tracked-tools table
```

**Structure Decision**: Standard Ansible role layout produced by
`scripts/new-role.sh dolt_sql_server`, matching `roles/podman`. The role is
added to the mandatory roles block in `configure-linux-roles.yml` (alongside
`podman`, `claude_code`, `tmux`) so it runs during base VM provisioning
(FR-001). `templates/` holds the two rendered artefacts (server config and
systemd unit); `handlers/` performs `daemon_reload` + restart on config
change without disrupting an unchanged service (FR-005). Separately, the two
existing version-update playbooks gain a Dolt entry (detect + apply) and the
version-update architecture doc gains a tracked-tools row; the GitHub-release
fetch task file is reused unchanged.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --- | --- | --- |
| Systemd-on-boot (FR-002/FR-003) validated on a Vagrant/cloud VM rather than in the Molecule container | The canonical Molecule image (`ubuntu:24.04`, no PID1 systemd) cannot exercise `systemctl enable`/start-on-boot/auto-restart. Server install, config, unit-file rendering, loopback binding, and a direct functional smoke test ARE containerisable and remain in Molecule. | (a) Switching the role's `molecule.yml` to a privileged systemd image is forbidden — `molecule.yml` is canonical and changing it per-role (or globally) degrades every other role's scenario for one role's need. (b) Mocking systemd would not validate the real boot behaviour the requirement is about. Principle III explicitly authorises the VM fallback for the non-containerisable slice. |
