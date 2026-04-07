# Active Context: Java Role

## Current Status

**Phase**: Acceptance Testing

Implementation is **complete and reviewed**. All role files are in place and
the role is integrated into `configure-linux-roles.yml`. The next step is to
run the acceptance tests against a local Vagrant VM.

## What Is Done

- `roles/java/defaults/main.yml` — `java_sdkman_identifier: "21.0.7-tem"`
- `roles/java/meta/main.yml` — `galaxy_info` block
- `roles/java/tasks/main.yml` — three-task per-user sequence
  (download, install sdkman, install JDK)
- `roles/java/DESIGN.md` — design decisions documented
- `configure-linux-roles.yml` — `java` role added at line 22 (after `flutter`)
- Spec, plan, research, data-model, tasks, quickstart in `specs/005-java-role/`
- Last commits: `feat: provision sdkman and Temurin JDK per user via new java role`
  and `docs: add spec, plan and tasks for java role`

## Immediate Next Action

Run acceptance tests following `specs/005-java-role/quickstart.md`:

1. Activate only the `java` role in `configure-linux-roles.yml`.
2. Run `ansible-playbook -i inventories/local configure-linux-roles.yml`.
3. Verify SC-001: `java -version 2>&1 | grep -i temurin` on a provisioned user.
4. Verify SC-002: re-run playbook; confirm zero `changed` tasks.
5. Verify SC-003: repeat on ARM64 Vagrant VM.
6. Verify SC-004: JDK version in `java -version` output matches `21.0.7-tem`.
7. Verify SC-005: role runs in isolation without errors.

## Outstanding Tasks (from tasks.md)

The following validation tasks from the spec have not yet been executed:

- **T008** — SC-001: `java -version` contains "Temurin" (AMD64 VM)
- **T010** — SC-002: idempotency — sdkman installer task shows `ok` on second run
- **T012** — SC-004: version-override: changing `java_sdkman_identifier`
  installs new version
- **T014** — SC-002: full second-run zero-changed confirmation
- **T015** — SC-003: ARM64 provisioning validation
- **T016** — markdownlint: verify all modified `.md` files pass

## Active Decisions and Considerations

- The sdkman download URL is `https://get.sdkman.io/download` (not the bare
  `https://get.sdkman.io`); the bare URL works but redirects.
- `SDKMAN_DIR` environment variable is set on Task 2 to ensure sdkman installs
  into the correct user directory even if the installer uses the env var.
- No `no_log: true` anywhere in the role (per spec Assumptions).

## Patterns to Preserve

- `creates:` guard for JDK task MUST reference the version-specific path, not `current/`.
- No `become: true` at task level — play-level `become` is inherited.
- All YAML files start with `#SPDX-License-Identifier: MIT-0`.
