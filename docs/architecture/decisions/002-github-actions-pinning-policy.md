# ADR-002: GitHub Actions Pinning Policy (SHA vs Version Tags)

Date: 2026-05-16
Status: Proposed
Deciders: Stefan (Product Owner)

## Context and Problem Statement

The CI/CD workflow `.github/workflows/docker-publish.yml` builds, tests,
signs, and publishes the `ansible-toolchain` container image to GHCR. It
currently references third-party GitHub Actions using two different
pinning styles:

- **Commit-SHA pins with version comments** are used for
  `docker/setup-buildx-action`, `docker/metadata-action`,
  `docker/build-push-action`, `docker/login-action`, and
  `sigstore/cosign-installer` — the actions that touch registry
  credentials, sign artefacts, or build the image.
- **Floating major-version tags** are used for `actions/checkout@v6`,
  `actions/upload-artifact@v7`, and `actions/download-artifact@v8` in
  `docker-publish.yml`, and for `actions/checkout@v6` and
  `actions/setup-python@v6` in `molecule.yml`.

The split exists but is undocumented. Dependabot (`.github/dependabot.yml`)
already updates both styles monthly and groups all `github-actions`
updates into a single PR.

Constitution Principle IX (CI/CD Pipeline Security) requires "auditable
artefact provenance" but does not currently specify a pinning policy.
Without an explicit rule, future workflow changes risk inconsistent
review: a reviewer cannot tell whether a new `uses: foo/bar@v1` line is
acceptable or must be SHA-pinned.

This ADR records the proposed policy so the team can decide and so
future contributors (human and AI) apply a consistent rule.

## Decision Drivers

Initial driver set (to be reduced or expanded to 3–5 in a follow-up
interview with the decision-maker):

1. **Supply-chain integrity** — resistance to tag-retargeting attacks
   where a third-party maintainer (or attacker with maintainer
   credentials) moves an existing tag to a malicious commit.
2. **Security-patch velocity** — how quickly a CVE fix in an action
   reaches our pipeline without manual intervention.
3. **Auditability** — alignment with Principle IX; ability to reconstruct
   exactly which action code ran for a given workflow run.
4. **Maintenance burden** — Dependabot PR churn, reviewer time,
   merge-conflict risk in workflow files.
5. **Reviewer cognitive load** — readability of `uses:` lines and ease
   of spotting policy violations during code review.

## Considered Options

- **Option A — Two-tier policy (proposed)**: SHA-pin third-party actions
  that handle credentials, sign, or push artefacts; floating
  major-version tag for first-party `actions/*` utility actions.
- **Option B — SHA-pin everything**: every `uses:` line in every workflow
  uses a 40-character commit SHA with a `# vX.Y.Z` comment.
- **Option C — Tag-pin everything**: every `uses:` line uses a floating
  major-version tag.

## Decision Outcome

**Chosen option: A — Two-tier policy.** Document the rule in this ADR and
add a one-sentence cross-reference from constitution Principle IX. No
workflow changes required — both current workflows already conform to
the proposed tiers.

### The Two Tiers

**Tier A — SHA pin with `# vX.Y.Z` comment.** Required for any
third-party action that satisfies any of the following:

- runs with `packages: write`, `id-token: write`, or any cloud
  push/login credential;
- signs artefacts (cosign, sigstore, slsa-framework);
- builds or pushes a container image, package, or release;
- otherwise participates in the artefact-provenance chain.

Examples: `docker/*`, `sigstore/*`, `slsa-framework/*`,
`goreleaser/goreleaser-action`.

**Tier B — floating major-version tag (`@vN`)** is permitted for
first-party utility actions published under the GitHub-owned `actions/`
and `github/` organisations.

Examples: `actions/checkout`, `actions/setup-python`,
`actions/upload-artifact`, `actions/download-artifact`,
`actions/setup-node`, `github/codeql-action`.

### Dependabot Interaction

The existing `.github/dependabot.yml` configuration (monthly,
ecosystem `github-actions`, grouped) handles both tiers without change.
For Tier A entries, Dependabot rewrites the SHA and updates the
trailing `# vX.Y.Z` comment in the same edit. For Tier B entries, it
bumps the major version when a new major is released.

### Enforcement

This ADR is policy only. Automated enforcement (a CI lint job that
fails when a Tier A action is tag-pinned) is tracked separately as
issue `ansible-all-my-things-v2u` and blocks the parent finding epic.

## Consequences

**Positive**

- Reviewers gain an unambiguous rule for evaluating new `uses:` lines.
- Supply-chain risk for credential-bearing actions is bounded by SHA
  immutability; reading the workflow file is enough to know exactly
  which action code will run.
- First-party utility actions continue to receive security patches
  with minimal PR churn.
- No workflow rewrite is required today — current code already conforms.

**Negative**

- The policy is human-enforced until the lint job (`v2u`) lands; a
  drift between policy and workflow file is possible.
- The Tier B allow-list is identity-based (`actions/`, `github/`) and
  rests on trust in GitHub's account-security posture; a compromise of
  the `actions` org would bypass the policy entirely.
- Adding a new third-party action requires finding the right SHA at
  PR-creation time, a small friction compared with copying a tag.

**Neutral**

- The Dependabot grouping continues to land all action updates in a
  single monthly PR; reviewer effort stays the same.

## Confirmation

After approval:

1. Update constitution Principle IX with a one-sentence cross-reference
   to this ADR (PATCH version bump: 1.7.0 → 1.7.1).
2. Audit `docker-publish.yml` and `molecule.yml` against the tier table
   above; document any deviation as a finding.
3. Close `ansible-all-my-things-urf`.
4. The follow-up CI lint (`ansible-all-my-things-v2u`) provides the
   long-term enforcement mechanism.

## More Information

- Constitution Principle IX, `.specify/memory/constitution.md`.
- Current Dependabot configuration, `.github/dependabot.yml`.
- Feature concept doc that originally noted SHA pinning was out of
  scope, `docs/features/fork-safe-docker-ci/concept.md`.
- Issue tracker references: source finding
  `ansible-all-my-things-urf`; enforcement follow-up
  `ansible-all-my-things-v2u`; parent epic
  `ansible-all-my-things-86r`.
