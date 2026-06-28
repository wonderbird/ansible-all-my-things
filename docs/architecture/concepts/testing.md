# Testing Concepts

## Molecule Tests

Most roles in this project have a Molecule test scenario in `molecule/default/`
covering the full create → prepare → converge → idempotence → verify → destroy
lifecycle. Some legacy roles are not yet covered.

For roles that cannot be exercised in a container (e.g., desktop environment
configuration), follow the role-isolation procedure in
[role-development-workflow.md](./role-development-workflow.md).

## Host Architecture Map

For the architecture and provider of each test host, see the infrastructure
table in [README.md](../../../README.md#overview).

### Skip-Tag Mechanics

Two skip-tags gate role execution on hosts where a role cannot work:

- `not-supported-on-arm64` — applied to AMD64-only software; skipped on ARM64
  Tart VMs via `--skip-tags not-supported-on-arm64`.
- `not-supported-on-docker` — applied to roles that require a full desktop
  environment; skipped on Docker hosts via `--skip-tags not-supported-on-docker`
  (the Docker Ubuntu image has no XFCE desktop; Tart VMs do).

See [solution-strategy.md](../solution-strategy.md) for the authoritative
skip-tag definitions and rationale.
