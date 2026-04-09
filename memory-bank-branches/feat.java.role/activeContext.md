# Active Context: Java Role

**Primary source of truth**: [`specs/005-java-role/`](../../../../specs/005-java-role/)

## Current Status

**Phase**: Extended — spec/doc/role updates required before PR can be opened.

The java role implementation and acceptance tests are complete. Two further
changes are needed: (1) fix `JAVA_HOME` in the `android_studio` role code,
and (2) update all spec/doc/role files that reference the old snap JBR or
the old dependency model.

## What Is Done

- `roles/java/defaults/main.yml` — `java_sdkman_identifier: "21.0.7-tem"`
- `roles/java/meta/main.yml` — `galaxy_info` block
- `roles/java/tasks/main.yml` — three-task per-user sequence
- `roles/java/DESIGN.md` — design decisions documented
- `configure-linux-roles.yml` — `java` grouped under `# Flutter Development`
  before `android_studio` (commit `022fb88`)
- All spec artifacts in `specs/005-java-role/`
- Markdownlint fixes applied; all acceptance scenarios SC-001–SC-005 passed

## Immediate Next Action

Implement the `android_studio` JAVA_HOME code fix, then work through the
complete change inventory below, then open the PR.

## Pending Work: Code Fix

### `roles/android_studio/tasks/main.yml`

Three tasks hard-code `JAVA_HOME: /snap/android-studio/current/jbr`. Replace
in all three `environment:` blocks with:

```yaml
environment:
  # Uses Temurin JDK installed by the java role via sdkman.
  JAVA_HOME: "/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}"
```

Tasks affected (by description):

- "Detect latest Android API level" (shell task)
- "Detect latest build-tools version" (shell task)
- "Install SDK components" (community.general.android_sdk task)

No changes needed in `roles/flutter/tasks/main.yml`.

## Pending Work: Complete Change Inventory

### Spec files — `specs/003-android-studio-role/`

- **`spec.md`**: Assumptions (remove snap JBR claim; add java role prerequisite);
  add FR-013 (JAVA_HOME must use sdkman Temurin JDK path).
- **`research.md`**: Decision 4 — update Java source from snap JBR to Temurin
  JDK via java role; note versioned path rationale.
- **`plan.md`**: Technical Context Constraints (remove JBR reference; add Temurin
  JDK); SDK Pre-Provisioning Design steps 3 and 4 (update JAVA_HOME source).
- **`tasks.md`**: T010a (update JAVA_HOME description); T011 (update Java source);
  US4 Phase Dependencies (remove JBR from rationale).

### Spec files — `specs/004-flutter-role/`

- **`spec.md`**: FR-010 (add `java` as prerequisite alongside `android_studio`);
  Assumptions (add `java` role runs before `android_studio` and `flutter`).
- **`research.md`**: Android SDK Components section — note JDK now comes from
  `java` role, not the snap.

### Spec files — `specs/005-java-role/`

- **`tasks.md`**: T013 description fix ("after the `flutter` entry" →
  "before `android_studio` in the Flutter Development group"); mark all
  tasks `[x]` (all are complete).

### Role files — `roles/android_studio/`

- **`README.md`**: Requirements — add java role prerequisite; Dependencies —
  replace "none" with java role prerequisite note.
- **`DESIGN.md`**: JAVA_HOME section (lines 42–52) — full rewrite: replace snap
  JBR path with sdkman Temurin JDK path and rationale (versioned path, not
  `current/` symlink; `java_sdkman_identifier` from `roles/java/defaults/main.yml`).

### Role files — `roles/flutter/`

- **`README.md`**: Requirements — add java role; Dependencies — add `java` as
  third prerequisite; Example Playbook — add `java` before `android_studio`.
- **`DESIGN.md`**: `meta/main.yml — Empty Dependencies` section — add `java`
  to the list of prerequisites documented in README.md.

### Role files — `roles/java/`

- **`README.md`**: **MISSING — must be created.** All other roles have one.
  Content: role purpose, requirements, role variables table
  (`java_sdkman_identifier`), dependencies (none at meta level), example
  playbook, license, author.

### Files with no changes needed

- All `meta/main.yml` files (per project convention, meta dependencies unused)
- `roles/java/DESIGN.md` (accurate; upstream consumers not documented here)
- `specs/003/.../quickstart.md`, `tasks.md` (no JBR references beyond above)
- `specs/004/.../plan.md`, `tasks.md`, `data-model.md` (no JBR references;
  flutter tasks.md T004 note about README prerequisites is addressed via the
  `roles/flutter/README.md` update, not a tasks.md change)
- `specs/005-.../spec.md`, `research.md`, `plan.md`, `data-model.md`

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
