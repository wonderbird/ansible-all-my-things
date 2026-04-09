# Progress: Java Role

**Primary source of truth**: [`specs/005-java-role/`](../../../../specs/005-java-role/)

## What Works

All java role files are implemented and committed:

- `roles/java/defaults/main.yml` — variable default in place
- `roles/java/meta/main.yml` — galaxy_info present
- `roles/java/tasks/main.yml` — three-task per-user sequence with correct
  idempotency guards
- `roles/java/DESIGN.md` — non-obvious decisions documented
- `configure-linux-roles.yml` — `java` before `android_studio` in the
  `# Flutter Development` group (commit `022fb88`)

All acceptance tests passed (SC-001–SC-005): Temurin on AMD64 and ARM64,
idempotency, version override, isolated role run, markdownlint clean.

## What Is Left

### Code

1. Fix `JAVA_HOME` in `roles/android_studio/tasks/main.yml` — replace
   `JAVA_HOME: /snap/android-studio/current/jbr` with
   `JAVA_HOME: "/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}"`
   in all three `environment:` blocks (Detect API level, Detect build-tools,
   Install SDK components).

### Spec files — `specs/003-android-studio-role/`

2. `spec.md` — Assumptions + new FR-013
3. `research.md` — Decision 4
4. `plan.md` — Constraints + SDK steps 3–4
5. `tasks.md` — T010a, T011, US4 dependency note

### Spec files — `specs/004-flutter-role/`

6. `spec.md` — FR-010 + Assumptions
7. `research.md` — Android SDK Components JDK note

### Spec files — `specs/005-java-role/`

8. `tasks.md` — T013 description + mark all tasks `[x]`

### Role files — `roles/android_studio/`

9. `README.md` — Requirements + Dependencies
10. `DESIGN.md` — JAVA_HOME section rewrite

### Role files — `roles/flutter/`

11. `README.md` — Requirements + Dependencies + Example Playbook
12. `DESIGN.md` — meta/main.yml section

### Role files — `roles/java/`

13. `README.md` — **CREATE** (missing; all other roles have one); content:
    purpose, requirements, variables table (`java_sdkman_identifier`),
    no meta dependencies, example playbook, license, author.

### Pull Request

14. Open PR to merge `005-java-role` into `main`.

## Current Status

**Java role: COMPLETE** | **configure-linux-roles.yml: COMPLETE** |
**android_studio JAVA_HOME fix: PENDING** |
**Spec/doc updates (items 2–13): PENDING** | **PR: NOT OPENED**

## Known Issues

`roles/android_studio/tasks/main.yml` still uses the snap-bundled JBR path.
`roles/java/README.md` does not exist (all other roles have one).

## Evolution of Decisions

- sdkman URL: `https://get.sdkman.io` (`/download` returns 404).
- Version-specific `creates:` guard (not `current/`) prevents silent skip
  on JDK identifier change.
- JAVA_HOME for android_studio: inline versioned sdkman path using
  `java_sdkman_identifier`; no new defaults variable; no `current/` symlink.
  Confirmed by Ansible expert review.
- `args: executable: /bin/bash` does not source `~/.bashrc` — sdkman
  JAVA_HOME unavailable in non-interactive Ansible shells.
- SPDX in markdown: `<!-- SPDX-License-Identifier: MIT-0 -->` (not `#`).
- `configure-linux-roles.yml` FR-008 reference removed — same label maps
  to different requirements across specs.
