# Progress: Java Role

**Primary source of truth**: [`specs/005-java-role/`](../../../../specs/005-java-role/)

## What Works

All java role files are implemented and committed:

- `roles/java/defaults/main.yml` — variable default in place
- `roles/java/meta/main.yml` — galaxy_info present
- `roles/java/tasks/main.yml` — three-task per-user sequence with correct
  idempotency guards
- `roles/java/DESIGN.md` — non-obvious decisions documented
- `roles/java/README.md` — created (commit `03cf232`)
- `configure-linux-roles.yml` — `java` before `android_studio` in the
  `# Flutter Development` group (commit `022fb88`)

All spec and role doc updates committed (commit `03cf232`):

- `roles/android_studio/tasks/main.yml` — JAVA_HOME fixed (snap JBR →
  sdkman Temurin path) in all three `environment:` blocks
- `roles/android_studio/README.md`, `DESIGN.md` — java role documented
- `roles/flutter/README.md`, `DESIGN.md` — java role added as prerequisite
- `specs/003-android-studio-role/` — spec, research, plan, tasks updated
- `specs/004-flutter-role/` — spec, research updated
- `specs/005-java-role/tasks.md` — T013 fixed, all tasks marked `[x]`

All acceptance tests passed (2026-04-10, hobbiton AMD64):

- SC-001–SC-005 for java role in isolation ✓
- Full stack: java → android_studio → flutter provisioned and verified ✓
- JAVA_HOME fix verified: `sdkmanager --version` with Temurin JAVA_HOME ✓

## What Is Left

### Pull Request

Open PR to merge `005-java-role` into `main`.

## Current Status

**Java role: COMPLETE** | **android_studio JAVA_HOME fix: COMPLETE** |
**Spec/doc updates: COMPLETE** | **Acceptance tests: COMPLETE** |
**PR: NOT OPENED**

## Known Issues

Android toolchain license warning in `flutter doctor` — pre-existing
condition, not caused by this branch. Resolved interactively via
`flutter doctor --android-licenses`.

## Evolution of Decisions

- sdkman URL: `https://get.sdkman.io` (`/download` returns 404).
- Version-specific `creates:` guard (not `current/`) prevents silent skip
  on JDK identifier change.
- JAVA_HOME for android_studio: inline versioned sdkman path using
  `java_sdkman_identifier`; no new defaults variable; no `current/` symlink.
  Confirmed by Ansible expert review and end-to-end test on hobbiton.
- `args: executable: /bin/bash` does not source `~/.bashrc` — sdkman
  JAVA_HOME unavailable in non-interactive Ansible shells.
- SPDX in markdown: `<!-- SPDX-License-Identifier: MIT-0 -->` (not `#`).
- `configure-linux-roles.yml` FR-008 reference removed — same label maps
  to different requirements across specs.
