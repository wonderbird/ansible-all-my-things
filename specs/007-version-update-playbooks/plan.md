# Implementation Plan: Version Update Playbooks

**Branch**: `007-version-update-playbooks` | **Date**: 2026-05-12 | **Spec**:
[spec.md](spec.md)
**Input**: Feature specification from
`/specs/007-version-update-playbooks/spec.md`

## Summary

A maintenance playbook that refreshes stale version pins across role defaults
files — fetching current versions and paired checksums from each tool's upstream
source, and reporting what it moved. It runs on the control node (localhost). No
automation beyond file updates; the operator retains full control over
committing.

## Technical Context

**Language/Version**: Ansible-core >= 2.19.0
**Primary Dependencies**: `ansible.builtin` modules only (HTTP requests, file
reads and writes, facts, asserts); `community.general.version_sort` (already in
`requirements.yml`)
**Storage**: Local filesystem — role `defaults/main.yml` files modified in-place
**Testing**: localhost harnesses under `playbooks/update-versions/tests/`, run by
`.github/workflows/version-update-lint.yml`; no Molecule scenario (the playbook
runs on localhost, not managed hosts)
**Target Platform**: Control node (localhost, Linux)
**Project Type**: Ansible maintenance playbooks
**Performance Goals**: N/A — on-demand maintenance run; no SLA
**Constraints**: Unauthenticated GitHub API (60 req/hr); Android HTML scraping
is fragile (isolated per FR-007); SHA-1 checksum for Android (accepted risk per
TD-009); SDKMAN API response format — see research.md
**Scale/Scope**: the tools in `vars/tools.yml`, one maintenance playbook, one
concept document

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I — Idempotency | PASS | `tasks/write-pins.yml` writes a pin only when it matches exactly one line and fails otherwise; a second run when already current makes no modifications. |
| II — Role-First Organisation | JUSTIFIED VIOLATION | Maintenance playbooks are procedural operator tools, not infrastructure configuration. See Complexity Tracking. |
| III — Test Locally Before Cloud | N/A | Playbooks target localhost only; no managed hosts involved. |
| IV — Simplicity (YAGNI) | PASS | Minimal design. Shared task files avoid duplication. No premature abstraction. Android isolated per FR-007 without over-engineering. |
| V — Conventional Commits | DEFERRED | Applies at commit time per `commit` skill. |
| VI — Markdown Quality Standards | DEFERRED | `format-markdown` skill invoked after concept doc is finalised. |
| VII — Structured Problem Solving | NOTED | `fix-problem` skill invoked if unexpected obstacles arise during implementation. |

## Project Structure

### Documentation (this feature)

```text
specs/007-version-update-playbooks/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
└── quickstart.md        # Phase 1 output
```

### Source Code (repository root)

```text
playbooks/update-versions/
├── perform-updates.yml          # Apply updates to role defaults files; no commits
├── vars/
│   └── tools.yml                     # The tracked-tool registry the playbook reads
├── tasks/                       # shared task files, including the fetch-*.yml files under tasks/
└── tests/                       # localhost harnesses for the shared task files

docs/architecture/
└── version-update-playbooks.md  # Concept documentation (section structure per agreed template)
```

The shared task files are described in
[`docs/architecture/version-update-playbooks.md`](../../docs/architecture/version-update-playbooks.md),
section Chosen Solution.

**Structure Decision**: Maintenance playbooks follow the established
`playbooks/<operation>/` convention (mirrors `playbooks/backup/` and
`playbooks/restore/`). Shared upstream-fetching logic lives in
`playbooks/update-versions/tasks/` and is imported by `perform-updates.yml`,
satisfying FR-006 (no duplication). The tools are declared in
`playbooks/update-versions/vars/tools.yml`, which the playbook loops over, so it
contains no per-tool tasks. `fetch-github-release.yml` is parametrized for reuse
by every tool published as a GitHub release. Android fetching is isolated in its
own task file (FR-007). Concept documentation lives at
`docs/architecture/<feature>.md` as a top-level technical-concept file (sibling
to `solution-strategy.md`), per the feature-level decision recorded in beads
task `ansible-all-my-things-gz5` (technical concepts → `docs/architecture/`).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Principle II — inline task logic in maintenance playbooks | Procedural operator tools that query external APIs and modify local files do not fit the role abstraction. The backup/restore playbooks establish this same precedent. | Wrapping in a role would add a layer of indirection with no reuse benefit across different orchestration contexts, violating Principle IV (YAGNI). |
