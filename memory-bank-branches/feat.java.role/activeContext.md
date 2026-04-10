# Active Context: Java Role

**Primary source of truth**: [`specs/005-java-role/`](../../../../specs/005-java-role/)

## Current Status

**Phase**: Ready to open PR. All implementation, spec/doc updates, and
acceptance tests are complete.

## What Is Done

- `roles/java/defaults/main.yml` — `java_sdkman_identifier: "21.0.7-tem"`
- `roles/java/meta/main.yml` — `galaxy_info` block
- `roles/java/tasks/main.yml` — three-task per-user sequence
- `roles/java/DESIGN.md` — design decisions documented
- `roles/java/README.md` — created (was missing; all other roles have one)
- `configure-linux-roles.yml` — `java` before `android_studio` in the
  `# Flutter Development` group (commit `022fb88`)
- `roles/android_studio/tasks/main.yml` — JAVA_HOME fixed in all three
  `environment:` blocks: replaced snap JBR path with sdkman Temurin path
  `/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}`
  (commit `03cf232`)
- All spec artifacts in `specs/005-java-role/` updated and complete
- `specs/003-android-studio-role/` — spec, research, plan, tasks updated
  (JBR → Temurin; FR-013 added)
- `specs/004-flutter-role/` — spec, research updated (`java` prerequisite)
- `roles/android_studio/README.md` and `DESIGN.md` — java role documented
- `roles/flutter/README.md` and `DESIGN.md` — java role added as prerequisite
- Markdownlint clean; all acceptance tests passed (see below)

## Acceptance Tests Passed (2026-04-10, hobbiton AMD64)

### Java role in isolation (SC-001 – SC-005)

- SC-001: `java -version` → "Temurin-21.0.7" for user galadriel ✓
- SC-002: Zero `changed` tasks on second run ✓
- SC-003: AMD64 confirmed ✓ (ARM64 passed in prior session)
- SC-004: Version matches `21.0.7-tem` ✓
- SC-005: Isolated role run completed without error ✓

### Full provisioning stack (hobbiton freshly destroyed and reprovisioned)

- Android Studio `2025.1.3.7-wallpapers` snap installed ✓
- Android SDK: cmdline-tools/latest, platforms/android-37.0,
  build-tools/37.0.0 present ✓
- `sdkmanager --version` with Temurin JAVA_HOME → `20.0` ✓
  (confirms JAVA_HOME fix works end-to-end)
- Flutter 3.41.6 installed ✓
- `flutter doctor` Chrome/web target ✓
- Android toolchain license warning — pre-existing, not caused by this
  branch; `flutter doctor --android-licenses` resolves it interactively

## Immediate Next Action

Open the PR to merge `005-java-role` into `main`.

## Key Decisions (Expert-Reviewed)

- **JAVA_HOME**: inline in all three `environment:` blocks; no new defaults
  variable; use `java_sdkman_identifier` (not `current/` symlink) for
  stability against user `sdk default java` changes.
- **`{{ item }}` in defaults/main.yml**: never do this — looks like a bug
  and breaks outside loops.
- **`args: executable: /bin/bash`**: does NOT source `~/.bashrc`; sdkman
  JAVA_HOME is not available in non-interactive Ansible shells without
  explicit path or inline sourcing.

## Patterns to Preserve

- `creates:` guard for the JDK task MUST reference the version-specific
  path, not `current/`.
- No `become: true` at task level — play-level `become` is inherited.
- All YAML files start with `#SPDX-License-Identifier: MIT-0`.
