# Implementation Plan: Rootless Podman Ansible Role

**Branch**: `006-podman-rootless-role` | **Date**: 2026-04-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-podman-rootless-role/spec.md`

## Summary

Create `roles/podman/` — an Ansible role that installs Podman from the Ubuntu
apt repository and configures rootless container operation for every user in
`desktop_user_names` by managing `/etc/subuid` and `/etc/subgid` with
`ansible.builtin.lineinfile`, then running `podman system migrate` per user
so the new user-namespace mapping takes effect immediately.

## Technical Context

**Language/Version**: YAML — Ansible 2.19+

**Primary Dependencies**: `ansible.builtin.*` (no Galaxy collections needed);
Ubuntu `podman` apt package

**Storage**: `/etc/subuid`, `/etc/subgid` (system files managed by
`lineinfile`)

**Testing**: Local Vagrant + Docker VM (Linux AMD64);
`configure-linux-roles.yml` with only the `podman` role active

**Target Platform**: Ubuntu Linux 22.04 LTS and later (AMD64 and ARM64)

**Project Type**: Ansible role (infrastructure automation)

**Performance Goals**: N/A — provisioning tool, not a service

**Constraints**: Zero changed tasks on second run (idempotency); no external
PPA; no docker shim; no systemd lingering; no registries.conf changes

**Scale/Scope**: Per-user loop over `desktop_user_names`; single role, ~5 tasks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
| --- | --- | --- |
| I. Idempotency | PASS | `apt` module is idempotent; `lineinfile` with `regexp: ^username:` is idempotent; `podman system migrate` is guarded with `changed_when: false` so the task always reports `ok` (never `changed`), making it safe to re-run |
| II. Role-First Organisation | PASS | New capability implemented as a standalone role in `roles/podman/` |
| III. Test Locally Before Cloud | PASS (reminder) | Must be validated on local VM before any cloud target |
| IV. Simplicity (YAGNI) | PASS | No docker shim, no lingering, no registries.conf, no pre-flight version assert |
| V. Conventional Commits | PASS (reminder) | Commits must use `feat:` prefix for role creation |
| VI. Markdown Quality Standards | PASS (reminder) | README.md and DESIGN.md must comply; `format-markdown` skill applied after creation |

No constitution violations. Complexity Tracking table is empty.

## Project Structure

### Documentation (this feature)

```text
specs/006-podman-rootless-role/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command — NOT created by /speckit.plan)
```

No `contracts/` directory is generated. This role exposes no external APIs,
endpoints, or CLI schemas; it is purely an internal infrastructure automation
artifact.

### Source Code (repository root)

```text
roles/podman/
├── defaults/
│   └── main.yml          # subuid_start, subuid_count, subgid_start, subgid_count
├── meta/
│   └── main.yml          # galaxy_info: author, description, platforms, license
├── tasks/
│   └── main.yml          # install + per-user subuid/subgid + podman system migrate
├── README.md             # purpose, variables table, example playbook, license
└── DESIGN.md             # non-obvious design decisions (lineinfile strategy, migrate guard)
```

**Structure Decision**: Single-role layout matching the established convention
in `roles/java/`, `roles/android_studio/`, and `roles/flutter/`. No handlers
directory (no service restart needed). No templates directory (no Jinja2
templates needed). No files directory.

## Complexity Tracking

No constitution violations requiring justification.
