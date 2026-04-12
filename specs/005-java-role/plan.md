<!-- SPDX-License-Identifier: MIT-0 -->

# Implementation Plan: Java Role (sdkman + Temurin JDK)

**Branch**: `005-java-role` | **Date**: 2026-04-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-java-role/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

Install sdkman and the Temurin JDK (pinned LTS version) into the home directory
of every user listed in `desktop_user_names`, using a four-task per-user
sequence: install prerequisites (`zip`, `unzip`, `curl`) via apt, download the
sdkman installer, run the installer, then install the JDK via `sdk install java`.
All tasks are guarded for idempotency with `creates:`.
The role follows the conventions of the `android_studio` and `flutter` reference
roles (SPDX header, FQCN, `become_user`, no task-level `become`).
A Molecule test scenario (driver: `podman`, platform: `ubuntu:24.04`) provides
automated acceptance verification.

## Technical Context

**Language/Version**: YAML (Ansible 2.19+)
**Primary Dependencies**: `ansible.builtin.*`; sdkman installer from
`https://get.sdkman.io`; Eclipse Temurin JDK published on sdkman as `tem` vendor
**Storage**: Per-user `~/.sdkman/` directory tree on the remote host; no
controller-side storage
**Testing**: `molecule test` inside `roles/java/` using `molecule-plugins[podman]`
and `ubuntu:24.04`; SC-005
**Target Platform**: AMD64 + ARM64 Ubuntu Linux (both supported by sdkman and
Temurin)
**Project Type**: Ansible role
**Performance Goals**: N/A — provisioning tool, not a latency-sensitive service
**Constraints**: Idempotent (zero `changed` on second run); no task-level
`become`; FQCN throughout; SPDX header on every YAML file; no system-wide Java
installation
**Scale/Scope**: One role; four tasks per user (apt prerequisites + three
sdkman/JDK steps); one variable; one DESIGN.md; one Molecule scenario

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
| --------- | ------ | ----- |
| I. Idempotency | PASS | All `shell`/`command` tasks use `creates:` guards referencing version-specific paths. |
| II. Role-First | PASS | Implemented as `roles/java/`; no implementation logic in playbooks. |
| III. Test Locally Before Cloud | PASS | Molecule + Podman (`molecule test`) is the acceptance criterion (SC-005); this satisfies local-VM validation without cloud access. |
| IV. Simplicity (YAGNI) | PASS | Three tasks per user, one variable, no speculative abstraction. |
| V. Conventional Commits | PASS | No commits in this plan phase; will follow `feat:` prefix on first implementation commit. |
| VI. Markdown Quality | PASS | All `.md` files produced here follow ATX headings and blank-line list rules. |
| VII. Structured Problem Solving | PASS | No obstacles at plan time. Protocol applied if any arise during implementation. |

**Gate result**: All principles satisfied. No violations to justify in Complexity
Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/005-java-role/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

No `contracts/` directory: the role exposes no external API surface.
It consumes the `desktop_user_names` list and the `java_sdkman_identifier`
variable defined by the calling playbook/inventory; those are documented in
`data-model.md`.

### Source Code (repository root)

```text
roles/java/
├── defaults/
│   └── main.yml               # java_sdkman_identifier default value
├── meta/
│   └── main.yml               # galaxy_info
├── molecule/
│   └── default/
│       ├── molecule.yml       # podman driver, ubuntu:24.04 platform
│       ├── prepare.yml        # install python3+sudo, create testuser
│       ├── converge.yml       # apply java role with testuser
│       └── verify.yml         # assert java -version contains Temurin
├── tasks/
│   └── main.yml               # All provisioning tasks
└── DESIGN.md                  # Non-obvious design decisions
```

**Structure Decision**: Single-role layout matching every other role in the
repository. No `handlers/`, `templates/`, `files/`, or `vars/` directories
are needed; the role is pure-task with one default variable.

## Complexity Tracking

No constitution violations. This table is intentionally empty.
