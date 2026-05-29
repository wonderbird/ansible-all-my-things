# Implementation Plan: Version Update Playbooks

**Branch**: `007-version-update-playbooks` | **Date**: 2026-05-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-version-update-playbooks/spec.md`

## Summary

Maintenance playbooks that detect stale version pins across role defaults files and apply updates — fetching current versions and paired checksums from each tool's upstream source. Two playbooks share upstream-fetching task files and run on the control node (localhost). No automation beyond file updates; the operator retains full control over committing.

## Technical Context

**Language/Version**: Ansible-core >= 2.19.0
**Primary Dependencies**: `ansible.builtin.uri`, `ansible.builtin.replace`, `ansible.builtin.set_fact`, `ansible.builtin.debug` (built-in); `community.general.version_sort` (already in `requirements.yml`)
**Storage**: Local filesystem — role `defaults/main.yml` files modified in-place
**Testing**: Manual verification against a known-stale pin; no Molecule scenario (maintenance playbooks run on localhost, not managed hosts)
**Target Platform**: Control node (localhost, Linux)
**Project Type**: Ansible maintenance playbooks
**Performance Goals**: N/A — workload is 5 API calls + small file edits; no SLA required
**Constraints**: Unauthenticated GitHub API (60 req/hr); Android HTML scraping is fragile (TD-009); SHA-1 checksum for Android (accepted risk per TD-009); SDKMAN API response format — see research.md
**Scale/Scope**: 5 tracked tools, 2 playbooks, 1 concept document

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I — Idempotency | PASS | `ansible.builtin.replace` is idempotent: no match = no change. Second run when already current = no modifications. |
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
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks — not created here)
```

### Source Code (repository root)

```text
playbooks/update-versions/
├── query-versions.yml           # Detect version drift; report to stdout; exit non-zero if stale
├── perform-updates.yml          # Apply updates to role defaults files; no commits
└── tasks/
    ├── fetch-flutter-version.yml     # Flutter release manifest JSON → version + sha256
    ├── fetch-github-release.yml      # GitHub /releases/latest API → tag_name (parametrized; used for gitmux + nerd-fonts)
    ├── fetch-java-version.yml        # SDKMAN REST API → latest same-major patch for tem distribution
    └── fetch-android-version.yml     # HTML scrape developer.android.com → build number + sha1 (isolated per FR-007)

docs/architecture/
└── version-update-playbooks.md  # Concept documentation (section structure per agreed template)
```

**Structure Decision**: Maintenance playbooks follow the established `playbooks/<operation>/` convention (mirrors `playbooks/backup/` and `playbooks/restore/`). Shared upstream-fetching logic lives in `playbooks/update-versions/tasks/` and is imported by both top-level playbooks, satisfying FR-006 (no duplication). `fetch-github-release.yml` is parametrized for reuse across gitmux and nerd-fonts (same API, same response shape). Android fetching is isolated in its own task file (FR-007). Concept documentation lives at `docs/architecture/<feature>.md` as a top-level technical-concept file (sibling to `solution-strategy.md`), per the feature-level decision recorded in beads task `ansible-all-my-things-gz5` (technical concepts → `docs/architecture/`).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Principle II — inline task logic in maintenance playbooks | Procedural operator tools that query external APIs and modify local files do not fit the role abstraction. The backup/restore playbooks establish this same precedent. | Wrapping in a role would add a layer of indirection with no reuse benefit across different orchestration contexts, violating Principle IV (YAGNI). |
