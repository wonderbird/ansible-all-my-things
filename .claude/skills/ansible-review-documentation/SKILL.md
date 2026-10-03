---
name: ansible-review-documentation
description: >
  The documentation strategy for this repository: tier structure, co-located
  role documentation, the working-context specs tier, and the migration
  policy between them. Use when creating or reviewing documentation here.
---
# Documentation Strategy

This skill is self-contained and authoritative for this repository: review
documentation against the tiers below and nothing else.

The writing rules every durable artefact must satisfy — intent over
implementation details, current state over history, and the variable contract a
task file header states — are defined in `.specify/memory/constitution.md`,
Documentation Standards. Review against them there; they bind every agent, so
they are not restated here (Principle XI).

## Documentation Tiers

These are the tiers that carry placement rules. They are not an inventory of
`docs/`; anything else there is reference material bound by the same writing
rules.

- `README.md` — developer onboarding. Minimal and action-oriented: quick
  start, prerequisites, basic usage. It links to the detailed tiers rather
  than duplicating them, and changes when setup or usage changes. It is the
  first file a newcomer reads.
- `docs/architecture/` — long-term architecture and interface documentation,
  following the [arc42](https://docs.arc42.org/) template. Solution strategy,
  Architecture Decision Records and technical debt live here. Written once a
  decision is stable; revised when the architecture itself changes.
- `specs/<feature>/` — working context for one feature: spec, plan, research
  and tasks, managed by spec-kit.
- `roles/<role_name>/` — documentation of a single role, co-located with it.

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
Cross-cutting architecture documentation belongs to the `docs/architecture/`
tier instead, because it outlives any single role.

## Migration Policy

Content moves from `specs/` to `docs/` when it becomes stable, reusable
across features, and no longer tied to a single increment.
