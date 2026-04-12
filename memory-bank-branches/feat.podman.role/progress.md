# Progress — feat.podman.role

## What Works

### SDD Workflow Phases 1–4 — Complete

- **Spec** (`specs/006-podman-rootless-role/spec.md`) — FR-001–FR-012, 3
  user stories, SC-001–SC-004; all clarification findings resolved
- **Plan** (`specs/006-podman-rootless-role/plan.md`) — constitution check
  passed, source layout and design decisions documented
- **Tasks** (`specs/006-podman-rootless-role/tasks.md`) — T001–T021 all ✓
- **Implementation** (`roles/podman/`) — all role files created and verified
- **Code review** — all findings (H1, H2, M1, M2, L1, L2, L3) fixed
- **T020 acceptance test** — all SC-001–SC-004 passed on `hobbiton`
- **T023 molecule test** — `molecule test` passes for `roles/java/`

### Molecule + Java Role (T017–T023) — All Complete

| Task | Description | Status |
| --- | --- | --- |
| T017 | Add zip/unzip/curl prerequisite to java role | ✓ |
| T018 | Create molecule.yml (podman driver, ubuntu:24.04) | ✓ |
| T019 | Create prepare.yml (python3, sudo, testuser) | ✓ |
| T020 | Create converge.yml | ✓ |
| T021 | Create verify.yml (java -version → Temurin) | ✓ |
| T022 | Update requirements.txt with molecule deps | ✓ |
| T023 | Run molecule test — acceptance test | ✓ |

### Molecule Fixes (post-generation)

| Fix | File | Symptom resolved |
| --- | --- | --- |
| Added namespace + role_name | `meta/main.yml` | Galaxy naming error |
| Added ANSIBLE_ROLES_PATH | `molecule.yml` | Role not found in syntax check |
| Split raw tasks; become: false | `prepare.yml` | sudo not found / apt error |
| Removed Remove sdkman installer | `tasks/main.yml` | Idempotence failure |
| Explicit test_sequence | `molecule.yml` | Missing-phase warnings |
| ansible_facts['env'] | `verify.yml` | Deprecation warning |

### Standards Work

- Constitution amended to v1.2.0 (Molecule testing standard)
- Rule `340-molecule-testing.mdc` created and registered in `CLAUDE.md`
- `CONTRIBUTING.md` restructured (Molecule primary, Vagrant fallback)

## What's Left to Build

Review findings from 2026-04-12 technical code review (see `REVIEW-FINDINGS.md`):

- [ ] **M1** — Document Molecule exemption for `roles/podman/` in `DESIGN.md`
      (podman-in-podman problem prevents full Molecule test; `apt` + `lineinfile`
      tasks could be partially tested)
- [ ] **M2** — Remove `-qq` from `apt-get update -qq` in
      `roles/java/molecule/default/prepare.yml` to align with rule 340 template
- [ ] **L1** — Add `namespace: wonderbird` and `role_name: podman` to
      `roles/podman/meta/main.yml`
- [ ] **L2** — Conditionally delete `/tmp/sdkman-install.sh` in
      `roles/java/tasks/main.yml` (register install result; `when: changed`)
- [ ] **I1** — Add `update_cache: false` to podman `apt` task in
      `roles/podman/tasks/main.yml`
- [ ] **I2** — Add `become: false` comment to raw tasks in
      `roles/java/molecule/default/prepare.yml`
- [ ] Create PR to merge `006-podman-rootless-role` into `main`

## Current Status

**Branch**: `006-podman-rootless-role`
**Phase**: Post-review remediation — 6 findings to address before PR
**Blocker**: none (review findings are improvements, not blockers — but should
be resolved before merge per project quality standards)

## Known Issues

None beyond the review findings listed above.

## Evolution of Project Decisions

1. `ansible.builtin.user` cannot manage subuid/subgid — pivoted to
   `lineinfile`
2. `test/docker/Dockerfile` dropped from scope (needs rootful mode)
3. Overlapping subuid ranges intentional for single-person workstation
   (YAGNI) — documented in DESIGN.md D4
4. `&&` in YAML `>` folded scalars unreliable with Podman connection plugin
   — split into separate `raw` tasks
5. `apt-get update -qq` fails in Ubuntu 24.04 apt 2.7.x — flag must precede
   subcommand; simplest fix is removing `-qq` entirely
6. Unconditional installer cleanup breaks idempotence — removed the task
