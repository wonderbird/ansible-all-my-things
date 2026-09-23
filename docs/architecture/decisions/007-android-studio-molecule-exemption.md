# ADR-007: No Molecule Scenario for the android_studio Role

Date: 2026-09-23
Status: Accepted
Deciders: Stefan (Product Owner)

## Context and Problem Statement

Constitution Principle II binds every role that **can** be exercised in a
container to ship a Molecule scenario covering the full create → prepare →
converge → idempotence → verify → destroy lifecycle, and routes the rest to
VM validation as described in
[docs/architecture/concepts/testing.md](../concepts/testing.md).

The `android_studio` role installs Android Studio as a **classic snap**
(`community.general.snap`, `classic: true`). Snapd requires systemd as PID 1.
Every Molecule scenario in this repository uses the plain Podman driver with a
per-role `Dockerfile`; none runs an init system, and none is privileged. The
absence is uniform, and `grep -l -e systemd -e /sbin/init -e privileged
roles/*/molecule/default/molecule.yml` returns nothing.

The role is now applied by the desktop play of
`playbooks/configure-profile-roles.yml`, so the question is no longer
hypothetical: does Principle II oblige a scenario for this role?

## Decision Drivers

- **Principle II.** Its wording is "every role that **can** be exercised in a
  container". Whether this role can is the whole question.
- **Principle IV (YAGNI).** The cost of the scenario is measured against what
  it would actually verify.
- **A future harness change must reopen this.** A decision resting on a
  property of today's Molecule harness has to name that property, or a later
  change to the harness invalidates it silently.

## Considered Options

1. **Build a bespoke privileged, systemd-enabled Molecule scenario** for this
   one role.
2. **Declare the role not containerisable under this harness** and validate it
   on a local VM per `testing.md`.
3. **Track the missing scenario as technical debt**, to be paid later.

## Decision

Option 2. The `android_studio` role carries no Molecule scenario, and none is
planned. It is validated on a local VM.

This is a standing decision, not deferred work, so it is recorded here rather
than in the technical debt register: an entry in that register invites the
next Principle II audit to read a settled judgement as an open item and
re-litigate it.

The reasoning is deliberately narrow, because the general claim "snapd cannot
run under Podman" is false — Podman can run systemd as PID 1, and snapd in
containers is done elsewhere. The repo-local form is what holds:

- No Molecule scenario here runs an init system, so testing this role needs
  **new harness infrastructure**, not a new scenario in the existing shape.
- What that infrastructure would verify is a classic snap installing inside a
  container, which carries its own snapd-in-container caveats and therefore
  says little about the real desktop host the role targets.
- Under Principle IV that cost is disproportionate to the assurance.

## Consequences

- The `android_studio` role has no automated regression test. A defect in it
  is caught by a VM apply or by an operator, not by CI.
- Principle II is satisfied by its own wording, not waived.
- **Revisit trigger**: if any Molecule scenario in this repository gains an
  init system — that is, if the `grep` above ever returns a file — the first
  premise no longer holds and this decision must be re-taken.

## Follow-ups

The two roles wired into the desktop play alongside `android_studio` are
containerisable and their scenarios are deferred rather than exempted. That
deferral is recorded as TD-012 in
[docs/architecture/technical-debt/technical-debt.md](../technical-debt/technical-debt.md).
