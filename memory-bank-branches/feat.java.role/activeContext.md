# Active Context: Java Role

**Primary source of truth**: [`specs/005-java-role/`](../../../../specs/005-java-role/)

## Current Status

**Phase**: Acceptance Testing

Implementation is **complete and reviewed**. All role files are in place and
the role is integrated into `configure-linux-roles.yml`. The next step is to
run the acceptance tests against a local Vagrant VM.

## What Is Done

- `roles/java/defaults/main.yml` — `java_sdkman_identifier: "21.0.7-tem"`
- `roles/java/meta/main.yml` — `galaxy_info` block
- `roles/java/tasks/main.yml` — three-task per-user sequence
- `roles/java/DESIGN.md` — design decisions documented
- `configure-linux-roles.yml` — `java` role added (after `flutter`)
- All spec artifacts in `specs/005-java-role/`

## Immediate Next Action

Run acceptance tests following
[`specs/005-java-role/quickstart.md`](../../../../specs/005-java-role/quickstart.md).

Outstanding validation tasks (T008, T010, T012, T014, T015, T016) are tracked
in [`specs/005-java-role/tasks.md`](../../../../specs/005-java-role/tasks.md).

## Active Decisions and Considerations

- The sdkman download URL is `https://get.sdkman.io/download` (direct endpoint;
  the bare `https://get.sdkman.io` redirects).
- `SDKMAN_DIR` environment variable is set on the sdkman install task to ensure
  the correct target directory.
- No `no_log: true` anywhere in the role (per spec Assumptions).

## Patterns to Preserve

- `creates:` guard for the JDK task MUST reference the version-specific path,
  not `current/` — see
  [`specs/005-java-role/research.md`](../../../../specs/005-java-role/research.md).
- No `become: true` at task level — play-level `become` is inherited.
- All YAML files start with `#SPDX-License-Identifier: MIT-0`.
