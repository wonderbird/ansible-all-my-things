# Active Context: Java Role

**Primary source of truth**: [`specs/005-java-role/`](../../../../specs/005-java-role/)

## Current Status

**Phase**: Complete — open pull request to merge into `main`.

Implementation is complete, all acceptance tests passed, all commits done.

## What Is Done

- `roles/java/defaults/main.yml` — `java_sdkman_identifier: "21.0.7-tem"`
- `roles/java/meta/main.yml` — `galaxy_info` block
- `roles/java/tasks/main.yml` — three-task per-user sequence
- `roles/java/DESIGN.md` — design decisions documented
- `configure-linux-roles.yml` — `java` role added (after `flutter`)
- All spec artifacts in `specs/005-java-role/`
- Markdownlint fixes applied to all `specs/005-java-role/*.md` and
  `.markdownlint.json`

## Acceptance Test Results

| Task | Criterion | Result |
| ---- | --------- | ------ |
| T008 | SC-001: `java -version` shows "Temurin" (AMD64, hobbiton) | PASS |
| T010/T014 | SC-002: zero changed on second run (hobbiton) | PASS |
| T012 | SC-004: version override installs new version | PASS |
| T015 | SC-003: ARM64 (lorien) — `java -version` shows "Temurin" | PASS |
| T016 | Markdownlint clean on all modified `.md` files | PASS |

## Immediate Next Action

Open a pull request to merge `005-java-role` into `main`.

## Active Decisions and Considerations

- The sdkman download URL is `https://get.sdkman.io` — the `/download`
  endpoint returned 404 in production; corrected to match `research.md`.
- No `no_log: true` anywhere in the role (per spec Assumptions).
- SPDX license header `#SPDX-License-Identifier: MIT-0` applies to YAML
  files only (FR-008). Markdown files use
  `<!-- SPDX-License-Identifier: MIT-0 -->` to avoid MD018/MD041 errors.

## Patterns to Preserve

- `creates:` guard for the JDK task MUST reference the version-specific
  path, not `current/` — see
  [`specs/005-java-role/research.md`](../../../../specs/005-java-role/research.md).
- No `become: true` at task level — play-level `become` is inherited.
- All YAML files start with `#SPDX-License-Identifier: MIT-0`.
