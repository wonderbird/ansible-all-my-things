# Progress — feat.podman.role

## What Works

### SDD Workflow Phases 1–3 — Complete

- **Spec** (`specs/006-podman-rootless-role/spec.md`) — 12 functional
  requirements (FR-001–FR-012), 3 user stories, 4 acceptance criteria
  (SC-001–SC-004); all clarification findings resolved
- **Plan** (`specs/006-podman-rootless-role/plan.md`) — constitution check
  passed (all 6 principles), source layout defined, design decisions
  documented in `research.md` and `data-model.md`
- **Tasks** (`specs/006-podman-rootless-role/tasks.md`) — 21 tasks
  (T001–T021); all checked including T020 (acceptance test)
- **Implementation** (`roles/podman/`) — all role files created and verified
- **Code review** — all findings (H1, H2, M1, M2, L1, L2, L3) fixed

### Files Created / Modified

| File | Status |
| --- | --- |
| `roles/podman/defaults/main.yml` | Created ✓ |
| `roles/podman/meta/main.yml` | Created ✓ |
| `roles/podman/tasks/main.yml` | Created ✓ |
| `roles/podman/README.md` | Created ✓ |
| `roles/podman/DESIGN.md` | Created ✓ |
| `configure-linux-roles.yml` | Modified (podman added) ✓ |
| `CLAUDE.md` | Modified (Active Technologies updated) ✓ |
| `specs/006-podman-rootless-role/` | All 6 spec artifacts ✓ |
| `roles/java/tasks/main.yml` | Modified (prerequisites task added) ✓ |
| `roles/java/molecule/default/molecule.yml` | Created ✓ |
| `roles/java/molecule/default/prepare.yml` | Created ✓ |
| `roles/java/molecule/default/converge.yml` | Created ✓ |
| `roles/java/molecule/default/verify.yml` | Created ✓ |
| `requirements.txt` | Modified (molecule deps added) ✓ |
| `specs/005-java-role/spec.md` | Modified (FR-013–FR-019, SC-005) ✓ |
| `specs/005-java-role/plan.md` | Modified (Molecule references) ✓ |
| `specs/005-java-role/tasks.md` | Modified (T017–T023) ✓ |

## What's Left to Build

### T020 — Acceptance Test Against Hetzner VM (COMPLETE)

All four acceptance criteria passed against `hobbiton` (Hetzner Cloud,
Ubuntu, `galadriel` user):

- [X] SC-001: `podman --version` → `podman version 4.9.3`
- [X] SC-002: `podman build -t devcontainer .devcontainer/` → build succeeded
- [X] SC-002b: `podman run --rm devcontainer ansible --version`
  → `ansible [core 2.20.4]`
- [X] SC-003: second role run → zero `changed` tasks
- [X] SC-004: `/etc/subuid` and `/etc/subgid` contain `galadriel:100000:65536`

**Finding**: the build context must be `.devcontainer/` (not `.`), because
all `COPY` source files reside in `.devcontainer/`. Documentation corrected
in `spec.md`, `quickstart.md`, and `productContext.md`.

### After T020 (Podman role)

- [X] Check T020 in `tasks.md`

### Molecule + Java Role Extension (T017–T023)

- [X] T017: Added `zip`/`unzip`/`curl` prerequisite task as first task in
  `roles/java/tasks/main.yml`
- [X] T018: Created `roles/java/molecule/default/molecule.yml` (podman
  driver, ubuntu:24.04 platform)
- [X] T019: Created `roles/java/molecule/default/prepare.yml` (python3,
  sudo, testuser via raw + user module)
- [X] T020: Created `roles/java/molecule/default/converge.yml`
- [X] T021: Created `roles/java/molecule/default/verify.yml` (java
  -version → Temurin assertion)
- [X] T022: Updated `requirements.txt` with molecule dependencies;
  `ansible>=4.0.0` tightened to `ansible-core>=2.19.0`
- [X] Committed and pushed all changes
- [ ] T023: Run `molecule test` — acceptance test (Phase 4)
- [ ] Create PR to merge `006-podman-rootless-role` into `main`

## Current Status

**Branch**: `006-podman-rootless-role`
**Phase**: 4 — Acceptance Test pending (T023); all implementation complete
**Blocker**: none

## Known Issues

None identified during implementation or code review.

## Evolution of Project Decisions

1. Initially assumed `ansible.builtin.user` could manage subuid/subgid —
   confirmed via expert subagent that no released Ansible version supports
   this; pivoted to `lineinfile`
2. `test/docker/Dockerfile` dropped from scope after learning the rootless
   constraint (systemd-in-container needs privileged / rootful mode)
3. Overlapping subuid ranges (all users share start=100000) is intentional
   for the single-person workstation use case — documented in DESIGN.md D4
