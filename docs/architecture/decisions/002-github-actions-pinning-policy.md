# ADR-002: GitHub Actions Pinning Policy

Date: 2026-05-21
Status: Accepted
Deciders: Stefan (Product Owner)

## Context and Problem Statement

GitHub Actions workflows that push to registries, sign artefacts, or hold
elevated permissions (`packages:write`, `id-token:write`, `contents:write`,
`security-events:write`) are at risk of supply-chain compromise when the
`uses:` clause references a mutable tag or branch. A malicious commit
force-pushed to a tag can hijack a privileged workflow step.

At the same time, requiring SHA pins on every action — including well-known
first-party utilities from the `actions/` org — adds maintenance overhead
with minimal security benefit for low-privilege steps.

The problem: how to balance supply-chain security with maintainability?

## Decision Drivers

1. **Supply-chain security**: actions with access to secrets or registries
   must be immutably pinned.
2. **Maintainability**: low-privilege first-party actions should not require
   SHA rotation on every update.
3. **Automated enforcement**: the policy must be machine-checkable in CI.
4. **Simplicity** (Principle IV): minimum rules that cover the real risk.

## Decision Outcome

Adopt a **two-tier pinning policy** enforced by
[zizmor](https://github.com/woodruffw/zizmor) in CI.

### Tier A — SHA pin required

`uses: owner/action@<40-char-sha> # vX.Y.Z`

Applies to any action that:

- runs in a job holding `packages:write`, `id-token:write`, `contents:write`,
  or `security-events:write` permissions;
- signs, builds, pushes, or releases an artefact;
- is a container action (`docker://`);
- is from a third-party owner (any org other than `actions/` or `github/`);
- is in a transitive publish chain (e.g. `upload-artifact` feeding a push
  job).

### Tier B — floating major tag permitted

`uses: actions/something@vN` or `uses: github/something@vN`

Applies **only** to actions from the `actions/` or `github/` GitHub orgs that
do **not** hold elevated permissions.

### Allow-list mechanism

Exceptions to the default policy are configured in `.github/zizmor.yml` using
zizmor's `rules.unpinned-uses.config.policies` map. Per-line inline suppression
is available with `# zizmor: ignore[unpinned-uses]` comments for documented
edge cases.

## Tool Selection

**Selected: zizmor v1.x** (`woodruffw/zizmor`)

Health check evidence (assessed 2026-05-21):

| Tool    | Stars | Latest release    | Last push    | Archived |
| ------- | ----- | ----------------- | ------------ | -------- |
| zizmor  | 5 182 | v1.25.2 (2026-05) | 2026-05-20   | no       |
| pinact  | 1 020 | v3.10.1 (2026-05) | 2026-05-21   | no       |
| ratchet |   935 | v0.11.4 (2025-06) | 2026-04-21   | no       |

**Rejection rationale:**

- **pinact** (`suzuki-shunsuke/pinact`): strong health metrics and `--check`
  mode available. Rejected because pinact's check mode flags all non-SHA pins
  uniformly — it has no built-in policy layer for Tier B (ref-pin allowed for
  `actions/*`). Implementing the two-tier distinction would require a wrapper
  script, adding complexity.
- **ratchet** (`sethvargo/ratchet`): last release was June 2025 (~11 months
  before evaluation), indicating slower maintenance cadence. Also lacks native
  Tier B policy support.
- **zizmor**: purpose-built static analyser for GitHub Actions security;
  `unpinned-uses` audit is natively configurable with per-pattern `hash-pin`
  vs `ref-pin` policies, directly expressing the Tier A / Tier B distinction
  without wrappers. Most active project by commit cadence and star count.

## CI Enforcement

The pinning policy is checked on every push and pull request that touches
workflow files by `.github/workflows/pinning-lint.yml`.

## Consequences

### Positive

- Supply-chain risk is eliminated for all privileged workflow steps.
- Policy is version-controlled and machine-enforced — no manual audits needed.
- Tier B exemption keeps routine dependency-update PRs lightweight.

### Negative

- Tier A SHAs must be rotated when upstream actions release new versions
  (mitigated by Dependabot or pinact auto-update).
- zizmor flags additional GHA security issues beyond pinning; future findings
  may need allow-listing.

## References

- [zizmor documentation](https://woodruffw.github.io/zizmor/)
- [zizmor `unpinned-uses` audit](https://woodruffw.github.io/zizmor/audits/#unpinned-uses)
- Policy config: [`.github/zizmor.yml`](../../../.github/zizmor.yml)
- CI enforcement: [`.github/workflows/pinning-lint.yml`](../../../.github/workflows/pinning-lint.yml)
- Constitution Principle IX (GitHub Actions pinning)
