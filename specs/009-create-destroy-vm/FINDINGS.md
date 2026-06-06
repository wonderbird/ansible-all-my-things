# Findings: Create and Destroy VM Playbooks

**Source**: Specification review session — 2026-06-06
**Applies to**: `specs/009-create-destroy-vm/spec.md`

## Summary

Six findings emerged from the specification review. Five require spec updates;
one (non-breaking implementation) constrains the planning and task sequence.
Two candidate findings were raised and superseded during discussion (noted
below). Apply spec updates in the order listed — each builds on the previous.

---

## Finding 1 — `profile` parameter is optional (default: `basic`)

**Impact**: FR-002, User Story 1 acceptance scenario 1.

The `profile` parameter should be optional with a default value of `basic`,
symmetric with `provider` defaulting to `tart`. This makes the common case
frictionless: `ansible-playbook create-vm.yml` with no extra-vars spins up a
basic tart VM with no further input required.

**Spec change**: Update FR-002 to mark `profile` as optional with default
`basic`. Update User Story 1 acceptance scenario 1 to explicitly test the
no-args default path.

---

## Finding 2 — Single ordered hostname pool of 10 LOTR names

**Impact**: FR-004, FR-014, Key Entities (Hostname Pool), acceptance
scenarios referencing pool behaviour.

The hostname pool is a single ordered list of 10 LOTR place names shared
across all providers — not a per-provider pool. Existing hostnames
(`hobbiton`, `rivendell`, `lorien`, `dagorlad`, `moria`) are the first five
entries. Five additional LOTR names complete the list. Hostnames are assigned
sequentially from the list; the next available (unused) name is selected on
each `create-vm.yml` invocation.

The list is extensible: operators may append names to grow the pool beyond 10
at any time. When all names in the list are in use, `create-vm.yml` fails
immediately with an error naming the exhausted pool (no provider action is
taken).

**Spec change**: Replace per-provider pool language with a single ordered pool
definition. Retain LOTR examples and LOTR-region encoding as illustrative
defaults, not as a hardcoded requirement.

*Supersedes*:

- Per-provider pools with configurable themes (YAGNI: single pool is
  sufficient).
- Arbitrary pool size starting at 5 per provider (replaced by fixed list of
  10, extensible).
- Dropping grandfathered hostnames for geographic consistency (existing names
  are retained as first five entries; geographic precision is a lower priority
  than continuity).

---

## Finding 3 — `profile` places VM in group; `configure.yml` is a new deliverable

**Impact**: User Story 1 (acceptance scenario 4), FR-001, FR-005, scope
section (in scope), user documentation.

The `profile` parameter does not configure the VM within `create-vm.yml`.
Instead, it places the newly created VM into the corresponding inventory group
(`basic` or `desktop`). A separate `configure.yml` playbook reads group
membership and applies the appropriate roles (e.g., desktop environment roles
for the `desktop` group).

`configure.yml` targets all inventory hosts by default. The standard
`ansible-playbook --limit` flag restricts execution to a named group,
hostname, or pattern — no custom parameter is needed.

`configure.yml` does not currently exist in the required form and must be
created as part of this feature. It must be added to the spec scope, planned,
and tasked.

**Spec change**:

- Remove "VM is configured with a desktop environment" from User Story 1
  acceptance scenario 4; replace with "VM is placed in the `desktop` inventory
  group".
- Add `configure.yml` to the in-scope deliverables list.
- Add a new user story (or extend scope) describing `configure.yml` and
  `--limit` usage.
- Update FR-005 to separate VM registration (create-vm.yml) from role
  application (configure.yml).

---

## Finding 4 — Reorder user stories for earliest tangible outcome

**Impact**: User Scenarios section (priority labels only).

Swapping the priorities of User Story 3 and User Story 4 delivers the safety
guardrail (pool exhaustion) before the cosmetic improvement (provider-encoded
hostnames), allowing a working and safe system to be demonstrated earlier.

| Priority | Story |
| -------- | ----- |
| P1 | Create New VM |
| P2 | Destroy VM by Hostname |
| P3 | Pool Exhaustion Fails Loud *(was P4)* |
| P4 | Provider-Encoded Hostnames *(was P3)* |

**Spec change**: Update priority labels on User Story 3 and User Story 4.

---

## Finding 5 — Non-breaking implementation: coexist, then migrate, then delete

**Impact**: Scope section (in scope), FR-012.

Implementation must not break existing features. `provision.yml`, `destroy.yml`,
and the `provisioners/` directory coexist with the new playbooks throughout
implementation. Migration of existing hosts and workflows happens once the new
implementation demonstrably covers the required functionality. Deletion of
superseded artefacts is the final step, gated on migration completion.

**Spec change**: Update FR-012 and the scope section to make deletion
conditional on migration completion rather than an unconditional deliverable.

---

## Application sequence

Apply spec changes in this order to avoid conflicting edits:

1. Finding 4 — Reorder user stories (structural only, no content conflicts)
2. Finding 1 — Make `profile` optional
3. Finding 2 — Single ordered hostname pool
4. Finding 3 — `profile` → group; add `configure.yml`
5. Finding 5 — Non-breaking implementation constraint
