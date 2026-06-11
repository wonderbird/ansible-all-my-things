# Implementation Plan: Configure Basic Profile for Tart VMs

**Branch**: `010-configure-basic-profile` | **Date**: 2026-06-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-configure-basic-profile/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Provide a single orchestration playbook, `configure-profile.yml`, that
brings a freshly created tart Linux VM (from `create-vm.yml`) to a
development-ready baseline with no extra-vars: user accounts and SSH access,
OS package/timezone baseline, Node.js toolchain for desktop users, the five
standard development tool roles (podman, ruby, python, dolt_sql_server,
claude_code), and a conditional reboot. The implementation is a thin
composition layer — three new files totaling ~25 lines, all `import_playbook`
/ `roles:` / group_vars, zero new implementation logic, zero new roles, zero
new Galaxy collections.

## Technical Context

**Language/Version**: Ansible (YAML), ansible-core (project default; see
`requirements.txt`: `ansible-core>=2.19.0`)
**Primary Dependencies**: existing roles (`podman`, `ruby`, `python`,
`dolt_sql_server`, `claude_code`) and existing playbooks
(`playbooks/setup-users.yml`, `playbooks/setup-basics.yml`,
`playbooks/setup-nodejs.yml`, `playbooks/reboot-if-required.yml`) — all
already present; zero new Galaxy collections
**Storage**: N/A (no new persistent state beyond the new static
`inventories/group_vars/tart/vars.yml`)
**Testing**: Each of the 5 development tool roles already has a passing
`molecule/default/` scenario (run via `scripts/test-molecule-all.sh`); no new
Molecule scenarios are needed for this feature. End-to-end validation of
`configure-profile.yml` happens by running it against a real tart VM
created by `create-vm.yml` (Constitution Principle III) — mirroring how
`create-vm.yml`/`destroy-vm.yml` are validated, since this is an orchestration
playbook composed entirely of already-validated roles/playbooks.
**Target Platform**: tart-provisioned Ubuntu Linux VM (managed host, `tart`
inventory group); control node macOS ARM64 (per README's known test hosts)
**Project Type**: Ansible playbook orchestration (no new roles)
**Performance Goals**: N/A
**Constraints**: zero new Galaxy collections (FR-021); minimal increment —
pure composition of existing, already-tested building blocks (Principle IV)
**Scale/Scope**: 3 new files (~25 lines total combined), 0 new/modified
roles, 0 modified existing playbooks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Idempotency | PASS | Composes only already-idempotent, already-tested playbooks/roles. The 3 new files contain no tasks of their own (pure `import_playbook` / `roles:` / group_vars) — nothing new to break idempotency. FR-020/SC-006 verified end-to-end on a real tart VM. |
| II. Role-First Organisation | PASS | All five installed capabilities (podman, ruby, python, dolt_sql_server, claude_code) are existing roles, each with an existing `molecule/default/` scenario — no new Molecule work in scope. The two new playbooks contain zero implementation logic (only `import_playbook` and a `roles:` list), satisfying "playbooks MUST only orchestrate roles". No new versioned-tool pins → version-update registration N/A. |
| III. Test Locally Before Cloud | PASS | Validated against a local tart VM created via `create-vm.yml` before any cloud use (this feature is not invoked from any cloud playbook). |
| IV. Simplicity (YAGNI) | PASS | Smallest possible increment: 3 small files, pure composition. Explicitly drops the unused `ansible.posix` collection added by an earlier PoC (it is referenced nowhere in the repo). |
| V. Conventional Commits & Traceability | N/A (planning phase) | Applies at commit time per the `commit` skill. |
| VI. Markdown Quality Standards | PASS | All new/updated Markdown (this plan and Phase 1 docs) will be checked with `format-markdown` at task close. |
| VII. Structured Problem Solving | N/A (planning phase) | `fix-problem` invoked only if an unexpected obstacle arises during implementation. |
| VIII. No Untracked Technical Debt | PASS | No known follow-ups identified by this plan; any findings during implementation will be tracked per the constitution. |
| IX. CI/CD Pipeline Security | N/A | No CI/CD workflow changes in this feature. |
| X. No External-System References | PASS | No beads issue IDs or tracker references in any new durable artefact. |
| XI. Avoid Duplication (DRY) | PASS | Reuses the `configure-linux.yml` / `configure-linux-roles.yml` / `vagrant_tart` group_vars patterns rather than inventing new ones. `admin_user_on_fresh_system: "admin"` mirrors the existing `vagrant_tart` group_vars entry exactly (same value, analogous group). |
| XII. Fail Loud | PASS | No new failure paths introduced; reused playbooks/roles already implement fail-loud behaviour (e.g. `my_ansible_user_password`/`my_ssh_public_key` defaults that fail with actionable messages in `setup-users.yml`). |
| XIII. No Empty Artefacts | PASS | All 3 new files carry real, functional content (no placeholders, no `.gitkeep`). |

**Result**: All applicable gates PASS. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/010-configure-basic-profile/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md         # Phase 1 output (/speckit.plan command)
├── quickstart.md          # Phase 1 output (/speckit.plan command)
├── contracts/             # Phase 1 output (/speckit.plan command)
│   └── configure-basic-profile.md
└── tasks.md              # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository)

```text
playbooks/configure-profile.yml        # NEW: top-level orchestrator playbook
                                          # (import_playbook chain, mirrors configure-linux.yml)

playbooks/configure-profile-roles.yml  # NEW: roles-application playbook
                                          # (hosts: tart; roles: podman, ruby, python,
                                          #  dolt_sql_server, claude_code;
                                          #  mirrors configure-linux-roles.yml)

inventories/
└── group_vars/
    └── tart/
        └── vars.yml                     # NEW: admin_user_on_fresh_system: "admin"
                                          # (mirrors inventories/group_vars/vagrant_tart/vars.yml)

# Reused, unmodified:
playbooks/setup-users.yml
playbooks/setup-basics.yml
playbooks/setup-nodejs.yml
playbooks/reboot-if-required.yml
roles/podman/
roles/ruby/
roles/python/
roles/dolt_sql_server/
roles/claude_code/
```

**Structure Decision**: `playbooks/` playbook layout, mirroring the existing
`configure-linux.yml` / `configure-linux-roles.yml` pair's structure, scoped
down to the basic-profile subset of playbooks and roles. The new group_vars file
follows the existing per-inventory-group `vars.yml` convention (one directory
per group under `inventories/group_vars/`), as already used by
`vagrant_tart`, `windows`, `hcloud_linux`, `vagrant_docker`, and
`aws_ec2_linux`.

## Complexity Tracking

> No entries — Constitution Check has no violations to justify.
