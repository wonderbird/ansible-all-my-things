# Tasks: Dolt SQL Server Ansible Role

**Input**: Design documents from `/specs/008-dolt-sql-server-role/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/, quickstart.md

**Tests**: No separate test tasks — Molecule verify.yml assertions
are part of the role implementation (not TDD pre-write; spec does
not request it).

**Organization**: Tasks grouped by user story for independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no shared dependencies)
- **[Story]**: US1 = SQL Server Starts Automatically on VM Boot (P1);
  US2 = Developer Initializes Repository with Dolt Backend (P2)

---

## Phase 1: Setup

**Purpose**: Scaffold the role skeleton using the canonical helper
script. `molecule/default/molecule.yml` and
`molecule/default/prepare.yml` are generated here and MUST NOT be
edited afterwards (canonical per molecule-testing skill).

- [ ] T001 Scaffold role: run `bash scripts/new-role.sh dolt_sql_server`
  to create `roles/dolt_sql_server/` skeleton including canonical
  `molecule/default/molecule.yml` and `molecule/default/prepare.yml`
  — do NOT edit these two files afterwards

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish all role variables and metadata before any
template, task, or Molecule file can reference them. MUST complete
before Phase 3.

**⚠️ CRITICAL**: No US1 or US2 work can begin until this phase is
complete.

- [ ] T002 Create `roles/dolt_sql_server/defaults/main.yml` with
  ten variables: `dolt_version: "v2.0.8"`,
  `dolt_install_path: /usr/local/bin/dolt`,
  `dolt_listen_host: 127.0.0.1`, `dolt_listen_port: 3306`,
  `dolt_data_dir: /var/lib/dolt`, `dolt_config_dir: /etc/dolt`,
  `dolt_config_path: "{{ dolt_config_dir }}/config.yaml"`,
  `dolt_service_user: dolt`, `dolt_service_name: dolt-sql-server`,
  `dolt_readiness_timeout: 30`
- [ ] T003 Create `roles/dolt_sql_server/meta/main.yml` with
  `galaxy_info` (namespace: wonderbird, role_name: dolt_sql_server)
  and platforms: Ubuntu 22.04 (jammy) and 24.04 (noble)

**Checkpoint**: Defaults and metadata in place — Phase 3 can begin.

---

## Phase 3: User Story 1 — SQL Server Starts Automatically (P1)

**Goal**: Dolt binary installed, loopback-only config rendered,
systemd unit deployed and enabled; server starts on every boot;
idempotent re-provisioning does not disrupt running service;
version pin registered with update-version playbooks.

**Independent Test**: `cd roles/dolt_sql_server && molecule test`
— all assertions in verify.yml pass; idempotence step reports
zero changes.

### Implementation for User Story 1

- [ ] T004 [P] [US1] Create config template at
  `roles/dolt_sql_server/templates/config.yaml.j2` rendering
  `listener.host`, `listener.port`, and `data_dir` from role
  variables (contract: server-config.md)
- [ ] T005 [P] [US1] Create systemd unit template at
  `roles/dolt_sql_server/templates/dolt-sql-server.service.j2`
  with `Type=simple`, `User={{ dolt_service_user }}`,
  `ExecStart` launching `dolt sql-server --config={{ dolt_config_path }}`,
  `Restart=always`, `RestartSec=2`,
  `WantedBy=multi-user.target` (contract: systemd-service.md)
- [ ] T006 [US1] Create `roles/dolt_sql_server/handlers/main.yml`
  with handler `Restart dolt-sql-server` running
  `ansible.builtin.systemd_service` with `daemon_reload: true`,
  `name: "{{ dolt_service_name }}"`, `state: restarted`
- [ ] T007 [US1] Implement `roles/dolt_sql_server/tasks/main.yml`
  with the full task sequence:
  (1) `assert` `dolt_version` non-empty, `dolt_listen_host`
  is loopback, and `dolt_listen_port` is an integer in `1–65535`;
  (2) create `dolt` system user (`system: true`, no login shell);
  (3) create `dolt_data_dir` and `dolt_config_dir` owned by
  service user;
  (4) `get_url` arch-specific tarball (`x86_64`→amd64,
  `aarch64`→arm64) guarded by `stat`+version check, then
  `unarchive` and place binary at `dolt_install_path` mode 0755;
  (5) `template` `config.yaml.j2` → `dolt_config_path`, notify
  restart handler;
  (6) `template` service unit →
  `/etc/systemd/system/{{ dolt_service_name }}.service`, notify
  restart handler;
  (7) `systemd_service` `daemon_reload`, `enabled: true`,
  `state: started`, guarded on
  `ansible_facts['service_mgr'] == 'systemd'`;
  (8) `wait_for` host `{{ dolt_listen_host }}` port
  `{{ dolt_listen_port }}` timeout `{{ dolt_readiness_timeout }}`,
  then `assert` port listening with message naming host:port
- [ ] T008 [P] [US1] Create converge.yml at
  `roles/dolt_sql_server/molecule/default/converge.yml`
  applying the `dolt_sql_server` role with `become: true`
- [ ] T009 [US1] Create verify.yml at
  `roles/dolt_sql_server/molecule/default/verify.yml` asserting:
  (1) `dolt --version` output matches `dolt_version` with leading
  `v` stripped (`regex_replace('^v', '')`);
  (2) `/etc/dolt/config.yaml` contains `host: 127.0.0.1`;
  (3) `/etc/systemd/system/dolt-sql-server.service` exists and
  contains `Restart=always` and `WantedBy=multi-user.target`;
  (4) functional smoke test — start `dolt sql-server --config`
  in background, `wait_for` port 3306, run `SELECT 1` via
  `mysql` client (assert exit 0), run `ss -tlnp`, assert
  output contains `127.0.0.1:3306` and NOT `0.0.0.0:3306`
- [ ] T010 [US1] Add `- role: dolt_sql_server` to the mandatory
  `roles:` block in `configure-linux-roles.yml` after `tmux`
  (no tag needed — containerisable parts work without systemd)
- [ ] T011 [P] [US1] Extend query-versions.yml:
  `playbooks/update-versions/query-versions.yml` — slurp
  `roles/dolt_sql_server/defaults/main.yml`, extract
  `current_dolt_version`, include `tasks/fetch-github-release.yml`
  with `github_repo: dolthub/dolt`, save `fetched_dolt_tag`,
  add report line, extend fail-if-stale condition (reuses
  `fetch-github-release.yml` — no new fetch logic per DRY)
- [ ] T012 [P] [US1] Extend perform-updates.yml:
  `playbooks/update-versions/perform-updates.yml` — include
  `tasks/fetch-github-release.yml` with
  `github_repo: dolthub/dolt`, then `ansible.builtin.replace`
  the `dolt_version` line in
  `roles/dolt_sql_server/defaults/main.yml` (reuses existing
  pattern per D8)
- [ ] T013 [P] [US1] Add Dolt row to
  `docs/architecture/version-update-playbooks.md` tracked-tools
  table: Role `dolt_sql_server`, version_key `dolt_version`,
  checksum_key `—`, source `GitHub Releases API dolthub/dolt`

**Checkpoint**: `molecule test` passes all assertions; idempotence
reports zero changes. Version-update playbooks gain Dolt support.
Role wired into provisioning.

---

## Phase 4: User Story 2 — Developer Repository Opt-In (P2)

**Goal**: Role guarantees server accepts `bd init --server` with no
additional server-side configuration (FR-004, SC-004). No new role
code needed — US2 is a developer opt-in enabled by US1's server
running on `127.0.0.1:3306` with no-password root access.

**Independent Test**: Follow quickstart.md § "Developer opt-in"
procedure — `bd init --server`, `bd create`, then
`dolt sql-client --execute "SHOW DATABASES;"` confirms repo-prefix
DB present in Dolt (not an embedded fallback).

### Implementation for User Story 2

- [ ] T014 [US2] Create `roles/dolt_sql_server/README.md`
  documenting: role purpose and boundary (install + service only;
  no DB init/restore/backup per FR-006); all `defaults/main.yml`
  variables with types and defaults; postconditions on success
  (binary at pinned version, service enabled + active,
  loopback-only listener, no-password root accessible);
  developer opt-in procedure (`bd init --server`, verify with
  `dolt sql-client SHOW DATABASES`); link to `quickstart.md`
  for validation steps; explicit non-goals section

**Checkpoint**: README documents the US2 developer opt-in path;
role boundary is clear.

---

## Phase 5: Polish and Cross-Cutting Concerns

- [ ] T015 [P] Run `format-markdown` skill over all changed
  Markdown files: `roles/dolt_sql_server/README.md`,
  `docs/architecture/version-update-playbooks.md`, spec docs
- [ ] T016 Run `molecule test` from `roles/dolt_sql_server/` and
  confirm zero test failures and idempotence step `changed=0`

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 scaffold — BLOCKS
  all user stories
- **US1 (Phase 3)**: Depends on Phase 2 (variable names used in all
  templates and tasks)
  - T004, T005, T008 can start in parallel once T002/T003 are done
  - T006 after T004/T005 are conceptualized
  - T007 after T004, T005, T006
  - T009 after T007
  - T010, T011, T012, T013 can start in parallel after T002/T003
- **US2 (Phase 4)**: Depends on Phase 3 — server must exist before
  README documents it
- **Polish (Phase 5)**: Depends on all Markdown files being
  finalized

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — no dependencies on US2
- **US2 (P2)**: Depends on US1 completion (server must be implemented
  before README documents the developer opt-in); no new role code
  required

### Within Phase 3

- T004, T005: parallel (different template files)
- T006: parallel with T004/T005; logically before T007
- T007: after T004, T005, T006 (references all three)
- T008: parallel with T007 (converge just applies role; trivial)
- T009: after T007 (verify assertions derived from task output)
- T010: independent of T007 (different file)
- T011, T012, T013: parallel with each other and with
  T008/T009/T010 (all different files)

---

## Parallel Examples

```bash
# Parallel group A (templates + handler):
Task T004 — Create templates/config.yaml.j2
Task T005 — Create templates/dolt-sql-server.service.j2

# Parallel group B (version-update integration):
Task T011 — query-versions.yml Dolt entry
Task T012 — perform-updates.yml Dolt entry
Task T013 — version-update-playbooks.md row
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1: Scaffold
2. Complete Phase 2: Defaults + meta (CRITICAL — blocks all work)
3. Complete Phase 3: Full role + Molecule + provisioning wire-up +
   version tracking
4. **STOP and VALIDATE**: `molecule test` passes; idempotence clean;
   version playbooks detect/apply Dolt updates
5. US1 is independently deployable — server runs on provisioned VMs

### Incremental Delivery

1. Phase 1 + Phase 2 → skeleton with variables
2. Phase 3 → complete US1 + Molecule validation + version tracking
   → deploy
3. Phase 4 → README with US2 developer opt-in → document
4. Phase 5 → Markdown lint + final Molecule gate → merge-ready
