# System Patterns: Java Role

**Primary source of truth**: [`specs/005-java-role/`](../../../../specs/005-java-role/)

## Role Structure

```text
roles/java/
├── defaults/main.yml    # java_sdkman_identifier: "21.0.7-tem"
├── meta/main.yml        # galaxy_info
├── tasks/main.yml       # Three-task per-user sequence
└── DESIGN.md            # Non-obvious design decisions
```

No `handlers/`, `templates/`, `files/`, or `vars/` directories.

## Task Sequence and Data Model

Full task sequence, variable definitions, file-system entities, and
idempotency state transitions are in
[`specs/005-java-role/data-model.md`](../../../../specs/005-java-role/data-model.md).

## Design Decisions

All key design decisions (version-specific idempotency guard path, inline
sdkman sourcing, no task-level `become`, no PATH modification, ARM64
compatibility) with rationale and rejected alternatives are in
[`specs/005-java-role/research.md`](../../../../specs/005-java-role/research.md).

Non-obvious decisions are also captured close to the code in
[`roles/java/DESIGN.md`](../../../../roles/java/DESIGN.md).

## Playbook Integration

The `java` role is registered in `configure-linux-roles.yml` after `flutter`
with no architecture tags (ARM64 is supported natively).

## Conventions

- All YAML files begin with `#SPDX-License-Identifier: MIT-0`.
- All module references use FQCN (`ansible.builtin.*`).
- No task-level `become: true` — play-level `become` is inherited.
