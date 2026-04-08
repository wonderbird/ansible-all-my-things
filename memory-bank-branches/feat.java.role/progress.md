# Progress: Java Role

**Primary source of truth**: [`specs/005-java-role/`](../../../../specs/005-java-role/)

## What Works

All role files are implemented and committed:

- `roles/java/defaults/main.yml` — variable default in place
- `roles/java/meta/main.yml` — galaxy_info present
- `roles/java/tasks/main.yml` — three-task per-user sequence with correct
  idempotency guards
- `roles/java/DESIGN.md` — non-obvious decisions documented
- `configure-linux-roles.yml` — `java` role integrated (after `flutter`)

All acceptance tests passed:

- SC-001: `java -version` outputs "Temurin" on AMD64 (hobbiton)
- SC-002: zero `changed` tasks on second run (hobbiton)
- SC-003: `java -version` outputs "Temurin" on ARM64 (lorien/Tart VM)
- SC-004: version override (`21.0.6-tem`) installs new version alongside
  default; old `creates:` guard remains satisfied
- SC-005: role ran in isolation without errors

Markdownlint clean on all modified `.md` files (T016 complete).

## What Is Left

Open a pull request to merge `005-java-role` into `main`.

## Current Status

**Implementation: COMPLETE** | **Acceptance Testing: COMPLETE** |
**Commits: COMPLETE**

## Known Issues

None.

## Evolution of Decisions

Key decisions (sdkman URL, version-specific idempotency guard, no PATH
modification, ARM64 support, no Molecule, `SDKMAN_DIR` env var) are
documented with rationale and rejected alternatives in
[`specs/005-java-role/research.md`](../../../../specs/005-java-role/research.md).

SPDX header in markdown files must use HTML comment syntax
(`<!-- SPDX-License-Identifier: MIT-0 -->`), not the YAML `#` prefix —
discovered during T016 markdownlint run.
