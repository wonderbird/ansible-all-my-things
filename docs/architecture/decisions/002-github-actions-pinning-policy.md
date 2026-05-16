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
- **Option D — Do nothing**: keep the current mixed pinning state
  undocumented and resolve each new `uses:` line case-by-case.
- **Option E — Manual reviewer workaround**: no written policy; each
  pull-request reviewer applies their own judgement when a new action
  is introduced or an existing one changes pin style.
- **Option F — Buy a hardening product**: adopt a third-party
  supply-chain security product (for example StepSecurity
  Harden-Runner, Snyk for GitHub Actions, Socket) that monitors action
  behaviour at runtime instead of, or in addition to, writing a
  pinning policy.

### Pros and Cons of the Options

#### Option A — Two-tier policy

- Good, because it bounds supply-chain risk where it is highest
  (credential- and signing-bearing actions) without paying SHA-pin
  overhead everywhere.
- Good, because both current workflows already conform — adoption cost
  is documentation only.
- Good, because Dependabot already handles both tiers; no new tooling
  is required.
- Bad, because the policy is human-enforced until a CI lint (`v2u`)
  lands; drift between policy and workflow files is possible.
- Bad, because the Tier B allow-list rests on trust in GitHub's own
  account-security posture for the `actions/` and `github/` orgs.
- Neutral, because adding a new third-party action requires looking up
  a SHA at PR time — minor friction compared with copying a tag.

**Mitigations**

- Human-enforcement drift is closed by the follow-up CI lint job
  tracked as `ansible-all-my-things-v2u`, which blocks the parent
  finding epic and so cannot silently slip.
- Trust in the `actions/` org can be tightened on demand: an
  individual Tier B action MAY be SHA-pinned with an inline comment
  (`# tightened to SHA, see <issue>`) without changing the overall
  policy. If GitHub itself were compromised, the policy can be
  amended in a single PATCH revision to collapse to Option B.
- SHA-lookup friction can be removed for the contributor by running
  `pinact run` or `ratchet pin` locally before committing; both tools
  resolve `owner/action@vX` to `owner/action@<sha> # vX` automatically.

#### Option B — SHA-pin everything

- Good, because the rule is the simplest possible: every `uses:` line
  carries an immutable SHA — no allow-list, no per-action judgement.
- Good, because supply-chain risk is uniformly bounded; even a
  hypothetical compromise of the `actions/` GitHub org cannot move a
  pinned SHA under us.
- Bad, because security patches for first-party utility actions (CVEs
  in `actions/checkout`, etc.) require a Dependabot PR + merge before
  they reach our pipeline, slowing patch velocity.
- Bad, because workflow diffs become noisier — every minor utility
  bump generates a SHA change PR.
- Bad, because contributors must look up a SHA for every action,
  including trivial utility actions.

**Mitigations**

- Patch-velocity loss can be reduced by switching Dependabot to
  weekly cadence for `github-actions` and enabling auto-merge for
  passing CI on Dependabot PRs touching only first-party utility
  actions.
- Diff noise is already mitigated by the existing Dependabot grouping
  (`groups: all-actions`); all SHA bumps land in one PR per cycle.
- Contributor lookup burden is removed by `pinact run` / `ratchet pin`
  as described under Option A.

#### Option C — Tag-pin everything

- Good, because workflow files stay readable and writeable without
  external lookup.
- Good, because security patches roll in automatically when a
  maintainer cuts a new minor/patch under the same major tag.
- Bad, because credential- and signing-bearing actions become
  vulnerable to tag-retargeting attacks — a single compromised
  maintainer credential can replace the code that holds our GHCR push
  token at the next workflow run.
- Bad, because Principle IX's "auditable artefact provenance" claim
  becomes false: the workflow file no longer tells us which code ran.
- Neutral, because Dependabot churn drops slightly compared with
  SHA-everywhere (only major bumps generate PRs).

**Mitigations**

- The tag-retargeting risk cannot be mitigated at the policy layer —
  any meaningful mitigation (re-introducing SHA pinning for
  credential-bearing actions) is equivalent to adopting Option A and
  is therefore not a mitigation but a different choice.
- The audit-trail loss is partially recoverable post-hoc: GitHub
  workflow-run logs record the resolved `repo@SHA` for each action
  invocation, but only until the log retention window expires.
  Stakeholders relying on Option C MUST therefore extend the
  workflow-log retention to match their audit horizon.
- Layering Option F (Harden-Runner or equivalent) on top of Option C
  is the only meaningful compensating control.

#### Option D — Do nothing

- Good, because it requires zero effort and no policy maintenance.
- Bad, because every future workflow change re-opens the same debate
  with no precedent to anchor the decision.
- Bad, because Principle IX's "auditable artefact provenance" goal
  cannot be confirmed without an explicit rule against which to audit.
- Bad, because a contributor (including an AI agent) introducing a new
  third-party action has no signal that SHA pinning is expected.

**Mitigations**

- None of the negatives can be addressed without writing some form
  of policy, which is no longer "do nothing". A partial mitigation
  is to add a brief contributor hint in `AGENTS.md` pointing at the
  open decision; that, however, is itself a policy fragment and is
  excluded here to keep this option pure.

#### Option E — Manual reviewer workaround

- Good, because it preserves full per-case flexibility.
- Good, because it imposes no upfront documentation cost.
- Bad, because decisions drift over time as reviewers change or
  forget prior reasoning.
- Bad, because consistency cannot be enforced by any automated check,
  ruling out the later CI lint (`v2u`).
- Bad, because it places the burden of supply-chain reasoning on every
  reviewer for every PR rather than encoding the answer once.

**Mitigations**

- Drift and consistency loss can be reduced by maintaining a written
  reviewer checklist — but a checklist that captures the rule is
  effectively a thin Option A, so this is not a separable mitigation.
- The per-PR reasoning burden cannot be removed without a written
  policy.

#### Option F — Buy a hardening product (e.g. Harden-Runner)

- Good, because runtime egress monitoring catches a compromised action
  even when its pin (SHA or tag) was valid at review time —
  defence-in-depth beyond what any pinning policy can achieve.
- Good, because audit trails of network/file activity per workflow run
  strengthen the Principle IX provenance story.
- Bad, because it does not replace a pinning policy — Harden-Runner's
  own documentation recommends SHA pinning as a complement, so the
  policy question still has to be answered.
- Bad, because it adds an external runtime dependency and an extra
  workflow step on every job, increasing CI minutes and surface area.
- Bad, because full feature sets (custom egress allow-lists, longer
  audit retention, SSO) are paid-tier on most products evaluated.
- Neutral, because the product can be adopted later on top of any of
  Options A–C without re-opening this decision.

**Mitigations**

- The "does not replace policy" negative is mitigated by treating
  Option F as additive: adopt it on top of Option A, not instead of
  it. Harden-Runner's documentation explicitly recommends SHA
  pinning alongside its agent.
- CI-minute overhead can be capped by enabling Harden-Runner only on
  the `push` job (where credentials live) and not on `build` or
  `test` jobs.
- Paid-tier dependency is avoided by using only the free-tier
  egress-monitoring features at first; an upgrade decision can be
  deferred until the audit findings demand it.

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
