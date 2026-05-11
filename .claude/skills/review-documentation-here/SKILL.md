---
name: review-documentation-here
description: >
  Extends review-documentation by project-specific documentation structure,
  including co-located role documentation. Use when reviewing the project
  documentation.
---
# Project-Specific Documentation Strategy

Review the project documentation according to the rules here and to the
rules in the "review-documentation" skill.

## Role Documentation Co-Location

Each Ansible role MUST keep its documentation inside its own directory
under `roles/`:

```text
roles/<role_name>/
├── README.md    ← operator-facing: requirements, variables, usage
└── DESIGN.md   ← technical design: non-obvious decisions and constraints
```

`README.md` is the entry point for anyone using or maintaining the role.
`DESIGN.md` captures non-obvious implementation decisions, constraints,
and their rationale. Both files travel with the role if it is ever
extracted to a standalone Ansible Galaxy repository.

Role-specific documentation MUST NOT be placed under `docs/roles/`.
Cross-cutting architecture documentation (solution strategy, ADRs,
technical debt) continues to live in `docs/architecture/` as described
in the "review-documentation" skill.

## Working-Context Tier: `specs/<feature>/`

This project adds one documentation tier on top of the base strategy:

- `specs/<feature>/` — Working context per feature: spec, plan, research,
  and tasks (managed by spec-kit).

## Migration Policy

Content moves from `specs/` to `docs/` when it becomes stable, reusable
across features, and no longer tied to a single increment.
