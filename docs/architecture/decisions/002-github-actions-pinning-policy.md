# ADR-002: GitHub Actions Pinning Policy (SHA vs Version Tags)

Date: 2026-05-16
Status: Proposed
Deciders: Stefan (Product Owner)

## Context and Problem Statement

The CI/CD workflows under `.github/workflows/` build, test, sign, and
publish the `ansible-toolchain` container image to GHCR, and run
Molecule role tests. These workflows reference third-party GitHub
Actions using two different pinning shapes:

- **Commit-SHA pins with version comments** are used for some
  credential-bearing, signing, building, or publishing actions.
- **Floating major-version tags** are used for some utility actions
  that do not request elevated permissions.

See `.github/workflows/*.yml` for the live pin snapshot — that file
set is the source of truth for which actions are currently in which
shape.

The split exists but is undocumented. Dependabot
(`.github/dependabot.yml`) already updates both shapes monthly and
groups all `github-actions` updates into a single PR.

Constitution Principle IX (CI/CD Pipeline Security) requires "auditable
artefact provenance" but does not currently specify a pinning policy.
Without an explicit rule, future workflow changes risk inconsistent
review: a reviewer cannot tell whether a new `uses: foo/bar@v1` line is
acceptable or must be SHA-pinned.

This ADR records a recommended policy so the decision-maker can accept,
amend, or reject it, and so future contributors (human and AI) apply a
consistent rule.

### Project Blast Radius

This is a single-maintainer Ansible repository for personal virtual
machine setup. The Docker artefact (`ansible-toolchain`) is consumed
mainly by the maintainer's own workflows and by anyone who voluntarily
forks the repo. The publish step already runs only on non-PR events
(`docker-publish.yml:128`) and the image is cosign-signed
(`docker-publish.yml:205`). Consumers can detect tampering with
`cosign verify` against the OIDC certificate.

Sizing the worst case: a compromised publish produces an image used by
the maintainer and possibly a handful of voluntary forks; cosign
signature verification will fail or implicate the run; recovery is a
rebuild and a key rotation. This is materially smaller than a
multi-tenant production registry. The policy below is deliberately
proportional: it formalises what is already working rather than adding
new machinery.

### Scope

In scope: every `uses:` reference in every workflow under
`.github/workflows/`, regardless of form. This explicitly includes:

- direct action references (`uses: owner/action@ref`);
- reusable workflows (`uses: owner/repo/.github/workflows/x.yml@ref`);
- composite actions (which themselves transitively use other actions);
- container actions (`uses: docker://image:tag` or actions whose
  `runs.using: docker` pulls an external image).

Out of scope:

- non-`uses:` third-party code execution in CI. In particular, the
  `curl -LO .../container-structure-test-linux-${arch}` followed by
  `sudo mv` in `docker-publish.yml:107-110` is a distinct supply-chain
  finding (tracked separately as a curl|sudo binary-download issue).
  That finding exists precisely because pinning policy alone cannot
  address floating binary downloads inside `run:` steps. Adopting
  this ADR does not close that finding, and rejecting this ADR does
  not nullify it.
- runner-host integrity (GitHub-hosted runner internals);
- secret rotation, repository ruleset configuration, branch protection
  (separate concerns).

## Threat Model

The threats below are enumerated so each Considered Option can be
cross-referenced to the threats it materially addresses. Severities
are calibrated against the "Project Blast Radius" section above:
a single-maintainer, single-VM consumer surface bounds the absolute
impact of every threat below.

- **T1 — Pipeline credential leak.** GHCR push token plus OIDC
  `id-token: write` exposed to malicious action code running inside
  the publish job. This is the highest-blast-radius threat in the
  enumeration: a leaked push token can publish an arbitrary image
  under our identity until the token is rotated.
  - Scope: in scope.
  - Severity for this repo: high — the publish job holds exactly
    these credentials and is the one place an action can pivot from
    "executes in CI" to "publishes as us".
  - Owning option(s): A (SHA-pin credential-bearing actions), B
    (SHA-pin all); partial coverage from G (allow-list) by
    preventing introduction of disallowed actions.
- **T2 — Malicious artefact published.** An image carrying a backdoor
  is published under our signed identity; the cosign signature is
  still valid because we sign whatever we built; downstream trust
  chain is weaponised against consumers who only check the signature.
  - Scope: in scope.
  - Severity for this repo: high — trust chain compromise survives
    token rotation and is detectable only by out-of-band review of
    image contents.
  - Owning option(s): A, B; F (runtime egress monitoring) provides
    defence-in-depth.
- **T3 — CI secret exfiltration.** Ansible Vault password, SSH keys,
  or cloud credentials reachable via `secrets.*` exfiltrated by
  malicious action code in any job that mounts them.
  - Scope: in scope.
  - Severity for this repo: low — the CI secret surface today is
    small (publish credentials and signing OIDC, both covered by
    T1/T2); no broader cloud credential is mounted in CI.
  - Owning option(s): A and B reduce; the primary control is
    least-privilege job permissions per Principle IX rather than
    the pinning policy itself.
- **T4 — Supply chain to maintainer dev box.** A compromised action
  writes malicious content into `.devcontainer/` or other files that
  get pulled to local laptops by the maintainer or contributors —
  an indirect attack path that bypasses the CI sandbox.
  - Scope: in scope.
  - Severity for this repo: medium — indirect, requires the
    compromised content to be merged and then pulled locally, but
    bypasses runner isolation entirely if it lands.
  - Owning option(s): A, B reduce the action-code surface; the
    primary control is out-of-band code review on `.devcontainer/`
    changes.
- **T5 — Phishing or social-engineered PRs.** An adversary opens a
  PR adding `uses: evil/foo@v1`, betting on reviewer fatigue or
  unfamiliarity to land the action.
  - Scope: in scope.
  - Severity for this repo: medium — solo-maintainer review is the
    only gate; an inattentive merge of a malicious `uses:` line
    moves an attacker straight to T1/T2.
  - Owning option(s): A or B + G (allow-list) reduce; a future
    deferred SHA-enforcement CI lint reduces further by blocking
    non-conforming pins before review.
- **T6 — Bot-net abuse of forks.** A fork's CI compute is repurposed
  as a crypto miner, proxy, or other unrelated abuse target.
  - Scope: out of scope — a fork is the forker's compute, not ours.
  - Severity for this repo: n/a.
  - Owning option(s): none; named and dismissed.

Each Considered Option below cross-references the threat IDs it
materially addresses; the Recommendation cites them explicitly.

## Decision Drivers

The drivers below are priority-ranked. Higher-priority drivers should
dominate the trade-off when options conflict.

1. **D1 — Supply-chain integrity for credential-bearing steps.** The
   publish job holds `packages: write` and `id-token: write`. Code
   reached from those steps must be referenced by something an attacker
   cannot mutate without our consent.
2. **D2 — Auditability (Principle IX alignment).** A reviewer (human or
   future agent) should be able to determine which action code will run
   by reading the workflow file alone.
3. **D3 — Security-patch velocity.** Once a CVE in an action is fixed
   upstream, the path from "fix released" to "fix running in our
   pipeline" should be as short as is consistent with D1.
4. **D4 — Maintenance and cognitive load.** Dependabot PR churn,
   contributor effort to add a new action, reviewer time per PR.
   "Reviewer cognitive load" and "maintenance burden" are merged into
   this driver because the repository has a single maintainer who is
   also the sole reviewer.
5. **D5 — No recurring out-of-pocket cost.** This repository is a
   single-maintainer open-source personal project. Mechanisms that
   require a paid subscription or per-event metered cost are
   unacceptable as a permanent pin-policy dependency; free / OSS /
   free-tier-sufficient tooling only. Adopting a mechanism is
   permitted only while it stays free at the scale this repository
   operates at. D5 sits between D2 (auditability) and D3 (patch
   velocity) in priority: a mechanism that fails D5 is rejected
   outright, but among D5-compatible mechanisms the higher-priority
   drivers still dominate.

## Considered Options

- **Option A — Two-tier policy (recommended)**: SHA-pin actions that
  satisfy a capability-and-role test (credential-bearing, signing,
  building, or publishing); floating major-version tag for
  GitHub-published utility actions that do not request elevated
  permissions.
- **Option B — SHA-pin everything**: every `uses:` line in every
  workflow uses a 40-character commit SHA with a `# vX.Y.Z` comment.
- **Option C — Tag-pin everything**: every `uses:` line uses a floating
  major-version tag.
- **Option D — Do nothing**: keep the current mixed pinning state
  undocumented and resolve each new `uses:` line case-by-case.
- **Option E — Manual reviewer workaround**: no written policy; each
  pull-request reviewer applies their own judgement when a new action
  is introduced or an existing one changes pin style.
- **Option F — Buy a hardening product**: adopt a third-party
  supply-chain product (for example StepSecurity Harden-Runner) that
  monitors action behaviour at runtime in addition to (or instead of)
  a pinning policy.
- **Option G — GitHub repository allow-list (Settings → Actions)**:
  enable "Allow specific actions and reusable workflows" in repository
  settings and require SHA references. Mechanically prevents
  introduction of disallowed actions without writing a CI lint.
- **Option H — Fork-pin / internal mirror**: maintain a fork of each
  third-party action under a maintainer-owned namespace and reference
  the fork's SHA. Eliminates upstream-account-compromise exposure for
  the actions in the mirror.
- **Option I — Trusted-publisher allow-list + tag-pin**: maintain an
  explicit list of trusted publishers (a file or a repository ruleset)
  and permit tag pins for any action in that list, SHA otherwise.

### Pros and Cons of the Options

#### Option A — Two-tier policy

- Good, because it bounds supply-chain risk where it is highest
  (credential- and signing-bearing actions) without paying SHA-pin
  overhead everywhere (addresses T1, T2).
- Good, because both current workflows already conform — adoption cost
  is documentation only.
- Good, because Dependabot already handles both tiers; no new tooling
  is required.
- Good, because Tier B actions still receive zero-touch security
  patches via floating major tag, preserving patch velocity (D3) where
  credential risk is lowest.
- Good, because the candidate SHA-resolving helpers (`pinact`,
  `ratchet`) are free OSS tools — tool selection in the deferred
  SHA-enforcement CI lint must remain D5-compatible (free / OSS).
- Bad, because the policy is human-enforced unless and until the
  deferred SHA-enforcement CI lint lands — partial coverage of T5
  until that lint exists. See "Enforcement reality" below for an
  honest framing of this constraint.
- Bad, because Tier B's identity-and-capability constraint accepts a
  trust assumption about GitHub's own account-security posture for the
  `actions/` and `github/` organisations (residual T1/T2 exposure
  bounded by Tier B's capability test). See "Residual risk" below.
- Bad, because adding a new third-party action requires looking up a
  SHA at PR time — small friction compared with copying a tag.

##### Mitigations and residual-risk acceptance

- Lookup friction: a SHA-resolving helper such as `pinact` or
  `ratchet` can rewrite `owner/action@vX` to
  `owner/action@<sha> # vX` automatically. Tool selection and any
  installation/documentation is deferred to the deferred CI lint;
  this ADR does not pre-commit either tool. Until then the lookup
  is manual.
- Per-action tightening: an individual Tier B action MAY be SHA-pinned
  ad hoc with a comment above the `uses:` line documenting the
  reason, for example:

  ```yaml
  # SHA-pinned: downloads artefacts into the publish job (transitive Tier A)
  uses: actions/download-artifact@<sha> # v8
  ```

  The comment makes the deviation visible without requiring a tracker
  reference in the workflow file. This is policy-conformant, not a
  deviation. The maintainer approves these by reviewing the PR that
  introduces them; no separate governance is required.
- Residual risk — `actions/` org compromise: this is not mitigated by
  the policy. It is accepted as the cost of D3 patch velocity for
  utility actions. The accepted residual is bounded by the fact that
  Tier B actions cannot request `packages: write`, `id-token: write`,
  `contents: write`, `security-events: write`, or any cloud
  push/login credential (see Tier B definition below). Public
  precedents (for example the 2025 `tj-actions/changed-files`
  incident, which was a third-party publisher and would have fallen
  under Tier A, not Tier B) inform but do not change this
  acceptance: no published `actions/*` or `github/*` incident to
  date has resulted in arbitrary code execution under an attacker's
  control in our credential context. Re-evaluate on first disclosed
  `actions/`-org incident.

#### Option B — SHA-pin everything

- Good, because the rule is the simplest possible: every `uses:` line
  carries an immutable SHA — no allow-list, no per-action judgement
  (addresses T1, T2 uniformly across all actions, not only
  credential-bearing ones).
- Good, because trust scope shrinks uniformly; an `actions/`-org
  compromise cannot move a pinned SHA under us (closes Option A's
  residual T1/T2 exposure on Tier B).
- Bad, because security patches for utility actions (CVEs in
  `actions/checkout`, etc.) require a Dependabot PR + merge before
  they reach the pipeline, slowing D3.
- Bad, because workflow diffs become noisier — every minor utility
  bump generates a SHA change PR.
- Bad, because contributors must look up a SHA for every action,
  including trivial utility actions (D4 cost).

##### Mitigations

- Patch-velocity loss can be reduced by switching Dependabot to
  weekly cadence for `github-actions` and enabling auto-merge for
  passing CI on Dependabot PRs that touch only utility actions.
  This narrows the A↔B gap on D3 significantly; the residual delta is
  largely whether you trust auto-merge on `actions/*` bumps.
- Diff noise is already mitigated by the existing Dependabot grouping
  (`groups: all-actions`); all SHA bumps land in one PR per cycle.
- Contributor lookup burden is removed by `pinact run` / `ratchet pin`
  as discussed for Option A (same caveat: tool choice deferred to
  the deferred CI lint).

**Rejected even with mitigations**: Option B+auto-merge+pinact closes
the D3 gap but requires trusting GitHub's CI auto-merge for
security-touching bumps; A+G achieves equivalent T5 coverage at zero
adoption cost without that trust dependency.

#### Option C — Tag-pin everything

- Good, because workflow files stay readable and writeable without
  external lookup.
- Good, because security patches roll in automatically when a
  maintainer cuts a new minor/patch under the same major tag (D3).
- Bad, because credential-bearing actions become vulnerable to
  tag-retargeting attacks (D1 fails) — a single compromised
  maintainer credential can replace the code that holds our GHCR push
  token at the next workflow run (fails T1; enables T2 through the
  same path).
- Bad, because Principle IX's "auditable artefact provenance" claim
  becomes false: the workflow file no longer tells us which code ran
  (D2 fails).
- Bad, because Dependabot churn for tag pins is lower (only major
  bumps generate PRs) — this is a positive on D4 but the price is
  the D1/D2 regression above.

##### Mitigations

- The tag-retargeting risk on credential-bearing actions cannot be
  mitigated at the policy layer without re-introducing SHA pinning
  for those actions, which is Option A.
- The audit-trail loss is partially recoverable post-hoc: GitHub
  workflow-run logs record the resolved `repo@SHA` for each action
  invocation, but only until the log retention window expires.
  Stakeholders relying on Option C MUST therefore extend
  workflow-log retention to match their audit horizon.
- Layering Option F (Harden-Runner or equivalent) provides
  defence-in-depth without changing the pin layer.

**Rejected even with mitigations**: Layering F (Harden-Runner) on C
detects post-hoc but cannot prevent T1/T2 exploitation before it
completes; D1 and D2 fail at the policy layer regardless of runtime
egress monitoring.

#### Option D — Do nothing

- Good, because it requires zero effort and no policy maintenance.
- Bad, because every future workflow change re-opens the same debate
  with no precedent to anchor the decision.
- Bad, because Principle IX's "auditable artefact provenance" goal
  cannot be confirmed without an explicit rule to audit against.
- Bad, because a contributor (including an AI agent) introducing a
  new third-party action has no signal that SHA pinning is expected
  (no control over T5; T1/T2 exposure depends on whichever pin shape
  is chosen ad hoc).

##### Mitigations

- None at the policy layer. A partial mitigation is to add a brief
  contributor hint in `AGENTS.md` pointing at the open decision; that
  is itself a policy fragment and is excluded here to keep the option
  pure.

**Rejected even with mitigations**: An AGENTS.md policy hint is
functionally an unenforceable fragment of Option A; T1, T2, and T5
exposures remain fully open.

#### Option E — Manual reviewer workaround

- Good, because it preserves full per-case flexibility.
- Good, because it imposes no upfront documentation cost.
- Bad, because decisions drift over time as reviewers change or
  forget prior reasoning.
- Bad, because consistency cannot be enforced by any automated check,
  ruling out the deferred SHA-enforcement CI lint.
- Bad, because it places the burden of supply-chain reasoning on
  every reviewer for every PR rather than encoding the answer once
  (T5 exposure scales with reviewer fatigue rather than being
  bounded by a written rule).

##### Mitigations

- A written reviewer checklist would reduce drift, but a checklist
  that captures the rule is functionally a thin Option A.
- The per-PR reasoning burden is unavoidable at this option.

**Rejected even with mitigations**: A reviewer checklist that captures
the pinning rule is functionally Option A with additional per-PR
burden; adopting A directly is strictly better and enables the deferred
SHA-enforcement CI lint.

#### Option F — Buy a hardening product (e.g. Harden-Runner)

- Good, because runtime egress monitoring catches a compromised
  action even when its pin was valid at review time —
  defence-in-depth beyond what any pinning policy can achieve
  (defence-in-depth against T1 and T2 even after pin shape is
  compromised).
- Good, because audit trails of network/file activity per workflow
  run strengthen the Principle IX provenance story.
- Good, because it can be adopted later on top of any of Options A–C
  without re-opening this decision. (Treat this as a positive of
  flexibility, not as a "neutral".)
- Bad, because it does not replace a pinning policy — Harden-Runner's
  own documentation recommends SHA pinning as a complement, so the
  policy question still has to be answered.
- Bad, because it adds an external runtime dependency and an extra
  workflow step on every job, increasing CI minutes and surface area.
- Bad, because full feature sets (custom egress allow-lists, longer
  audit retention, SSO) are paid-tier on most products evaluated
  (**D5-violating, defer adoption** — paid-tier features fail D5);
  free-tier coverage is assumed sufficient at the time of writing
  (2026-05-16) and would need re-verification at adoption time.
  Free-tier-only adoption remains permissible under D5.

##### Mitigations

- Treat F as additive: adopt it on top of Option A if defence-in-depth
  is wanted later. Harden-Runner documentation explicitly recommends
  SHA pinning alongside its agent.
- Scope Harden-Runner to the `push` job (the only job holding write
  credentials) to bound the per-job overhead.

#### Option G — GitHub repository allow-list (Settings → Actions)

- Good, because GitHub's native "Allow specific actions and reusable
  workflows" toggle mechanically blocks introduction of disallowed
  actions, without requiring CI or a lint job (mechanically addresses
  T5 at the introduction point).
- Good, because it can be combined with Option A: A defines what
  belongs in which tier; G prevents accidental addition of anything
  outside the allow-list.
- Good, because it is a native GitHub repository setting with no
  per-event or subscription cost (D5-positive).
- Bad, because the allow-list lives in repository settings, not in
  git — drift between settings and policy is invisible to
  reviewers reading the repo.
- Bad, because the allow-list does not distinguish SHA pin from tag
  pin per entry; enforcement of "SHA for Tier A" still requires the
  deferred SHA-enforcement CI lint or human review.
- Neutral, because for a solo-maintainer repo the settings-vs-git
  drift risk is small (one person owns both).

#### Option H — Fork-pin / internal mirror

- Good, because pinning to a fork in a maintainer-owned namespace
  eliminates upstream-account-compromise exposure for the mirrored
  actions (addresses T1, T2 specifically against upstream publisher
  compromise).
- Bad, because mirror maintenance is a recurring task: every
  upstream release must be re-mirrored and the pin advanced manually
  or via custom Dependabot configuration (D5-neutral: no recurring
  cash cost, but a recurring time cost charged to D4).
- Bad, because patch velocity (D3) drops to manual cadence for any
  mirrored action.
- Bad, because the trust relocation is partial: the upstream
  publisher is still trusted at the moment of each fork-sync.

**Rejected even with mitigations**: Fork-sync automation reduces but
does not eliminate D3/D4 overhead; trust relocation is partial
(upstream publisher trusted at sync time), and the maintenance
complexity is disproportionate to this repo's single-maintainer blast
radius.

#### Option I — Trusted-publisher allow-list + tag-pin

- Good, because it decouples the trust decision (per publisher) from
  the pinning decision (uniform tag pins inside the trusted set).
- Good, because the trust list is short and reviewable (handful of
  publishers).
- Bad, because tag-retargeting risk is restored for all
  credential-bearing actions whose publishers are on the list,
  including signing tools. D1 fails for the same reason as Option C
  (fails T1; enables T2 for any compromised publisher on the list).
- Bad, because publisher trust is binary in this option; a publisher
  is either fully trusted (any of their actions can be tag-pinned)
  or not at all, which is a coarser knob than Tier A's
  per-capability test.
- Neutral, because the trusted-publisher list is a plain repository
  artefact with no recurring cost (D5-neutral).

**Rejected even with mitigations**: The trusted-publisher list
restores tag-retargeting risk for every credential-bearing publisher
on it (T1 open); Option A's per-capability test is a strictly
finer-grained trust control with identical D5 posture.

## Recommendation

The recommended option is **A+G — Two-tier policy combined with the
GitHub repository allow-list**. G is elevated from "optional guard"
to primary co-recommendation because it is free (D5-positive), additive,
and mechanically addresses T5 (phishing/social-engineered PRs) at the
introduction point — the only gap G does not close is pin-style
enforcement (SHA vs tag per tier), which is reserved for the deferred
SHA-enforcement CI lint.

The table below summarises the option×threat×mitigation re-walk
performed after the Threat Model (T1–T6) and D5 driver landed;
see the per-option sections for full rationale and
"Rejected even with mitigations" notes.

| Option | D1 | D2 | D3 | D4 | D5 | T1 | T2 | T5 | Verdict |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| **A+G** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Recommended** |
| B + auto-merge | ✓ | ✓ | ~¹ | ~¹ | ✓ | ✓ | ✓ | ~² | Second-best |
| C + F | ✗ | ✗ | ✓ | ✓ | ~³ | ✗ | ✗ | ~³ | Rejected |
| D | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | Rejected |
| E | ~ | ~ | ✓ | ✗ | ✓ | ~ | ~ | ~ | Rejected |
| H | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ~ | Rejected |
| I | ✗ | ✗ | ✓ | ~ | ✓ | ✗ | ✗ | ~ | Rejected |
| F (additive) | — | — | — | — | ~³ | + | + | — | Add-on only |

Legend: ✓ satisfies · ✗ fails · ~ partial/conditional ·
— not applicable · + improvement

¹ D3/D4 close substantially with auto-merge and pinact; residual =
trust in auto-merge on security bumps.
² T5 coverage requires the deferred CI lint; G's introduction-point
guard is not part of B.
³ F free-tier assumed D5-compatible; paid-tier features are
D5-violating (see D5 driver).

The sections below document the policy as it would read if Option A
is accepted, so the decision-maker can review the rule before deciding.

### Tier A — SHA pin with `# vX.Y.Z` comment

Required for any action — direct, composite, container, or
reusable-workflow — that satisfies any of the following:

- the action runs in a job that holds `packages: write`,
  `id-token: write`, `contents: write`, `security-events: write`, or
  any cloud push/login credential; or
- the action signs artefacts (cosign, sigstore, slsa-framework); or
- the action builds, pushes, or releases a container image,
  package, binary, or other artefact; or
- the action is a container action (`uses: docker://...` or
  `runs.using: docker` with an external image) — regardless of
  publisher, because container actions can fetch arbitrary
  layers at runtime; or
- the action is a reusable workflow or composite action that itself
  uses any action satisfying the above (transitive Tier A); or
- the action uploads or stages artefacts (container layers, build
  products, test archives) that are subsequently downloaded in a job
  satisfying any of the above criteria, forming a transitive publish
  chain (`actions/upload-artifact` in a pipeline whose
  `download-artifact` step runs in the publish job is a canonical
  example).

Examples (illustrative, not exhaustive): `docker/*`, `sigstore/*`,
`slsa-framework/*`, `goreleaser/goreleaser-action`,
`actions/upload-artifact` and `actions/download-artifact` (when used
in a pipeline with a publish job — see Tier B note below). The
criteria above are normative; the examples are not.

### Tier B — floating major-version tag (`@vN`) permitted

Tier B requires **both** of the following:

- *Identity*: the action is published under the GitHub-owned
  `actions/` or `github/` organisation.
- *Capability*: the action does NOT request any of
  `packages: write`, `id-token: write`, `contents: write`,
  `security-events: write`, or any cloud push/login credential.

If both hold, a floating major-version tag (`@vN`) is permitted.
Examples (illustrative): `actions/checkout`, `actions/setup-python`,
`actions/setup-node`. Note: `github/codeql-action` uploads SARIF
with `security-events: write` and is therefore Tier A under the
capability test, even though its identity satisfies Tier B.
Similarly, `actions/download-artifact` runs inside the publish job
in this repository's pipeline (which holds `packages: write`) and is
therefore Tier A under the capability criterion;
`actions/upload-artifact`, which runs earlier in the non-credential
build job, is Tier A under the transitive-publish-chain criterion.

### Dependabot Interaction

The existing `.github/dependabot.yml` configuration (monthly,
ecosystem `github-actions`, grouped) is expected to handle both
tiers: rewriting the SHA and updating the trailing `# vX.Y.Z`
comment for Tier A entries, and bumping the major version for Tier B
when a new major is released. This behaviour is documented by
Dependabot but has not been verified in this repository; the first
Dependabot PR after merging this ADR serves as the verification (see
Confirmation, below).

### Enforcement Reality

This ADR is policy only. Two enforcement levels are possible:

1. **Mechanical guard (Option G, co-recommended)**: enabling GitHub's
   repository allow-list under Settings → Actions can prevent
   accidental introduction of unallowed actions at zero implementation
   cost. It does not enforce Tier A vs Tier B per pin style.
2. **Automated lint (open issue, deferred)**: a CI lint job that fails
   on a Tier A action with a tag pin. The lint issue is open with no
   committed timeline. With only ~12 `uses:` lines across two workflows
   today, human enforcement by the maintainer-reviewer is realistic
   indefinitely. If the lint job is never implemented, the policy
   remains in effect as a human convention; that is an honest part of
   this decision, not a postponed deficit.

### Cron and Scheduled Runs

`docker-publish.yml` runs on a Monday 04:00 cron. Tag-retargeting on
a Tier B action could execute on that schedule without a human in
the loop. Because Tier B forbids elevated permissions, the blast
radius of such an event is bounded to the build/test path (which
cannot publish or sign on its own). A retargeted Tier A action
would, by definition, reach the credential-bearing publish path.
Both cases reduce to "trust the publisher of any Tier A action"
during cron runs; the policy as a whole is the mitigation.

### Action Deprecation and Rename

SHA-pinned consumers do not follow upstream rename/redirect. If
`sigstore/cosign-installer` is renamed, our Tier A pin breaks and
must be updated manually or via Dependabot's deprecation detection.
Tag-pinned consumers may follow rename if the publisher pushes the
new tag to the old repo. The asymmetry is accepted as part of the
SHA pin choice.

### Tier B Tightening Governance

A Tier B action may be SHA-pinned ad hoc (see Mitigations above)
with a comment above the `uses:` line that documents the reason
for the tightening. The PR that introduces the tightening is the
approval; the comment makes the deviation visible in the workflow
file without requiring a tracker reference.

## Consequences

### Positive

- Reviewers gain an unambiguous rule for evaluating new `uses:`
  lines.
- Supply-chain risk for credential-bearing actions is bounded by SHA
  immutability. Note: a SHA pin guarantees that the *referenced
  commit* does not change; it does NOT guarantee that the code at
  that commit is trustworthy. A SHA-pinned action that was malicious
  when the SHA was chosen, or that runs `curl | bash` or downloads
  external code at runtime, remains a risk. SHA pinning is a
  necessary but not sufficient supply-chain control.
- First-party utility actions continue to receive security patches
  with minimal PR churn.
- Current `docker-publish.yml` and `molecule.yml` already conform to
  Tier A and Tier B rules for all actions except
  `actions/upload-artifact` and `actions/download-artifact`, which
  participate in the artifact-publish chain and require SHA pinning
  under the new transitive-publish-chain Tier A criterion. Pinning
  these two actions is a post-acceptance follow-up task (see below),
  not a prerequisite for adopting this ADR.
- The G co-recommendation (GitHub repository allow-list) adds a
  zero-cost mechanical guard: once enabled under Settings → Actions,
  it prevents introduction of any action outside the allow-list without
  requiring the deferred SHA-enforcement CI lint.

### Negative

- The policy is human-enforced indefinitely if the deferred
  SHA-enforcement CI lint never lands; see Enforcement Reality.
- A SHA-pinned third-party action can still execute arbitrary
  transitive code (composite-action chain, `run:` `curl | bash`,
  container image pull) that the SHA does not cover. Tier A reduces
  but does not eliminate this surface.
- Adding a new third-party action requires finding the right SHA at
  PR-creation time, a small friction compared with copying a tag.
- Residual risk for the `actions/` org compromise is accepted; see
  Option A mitigations.

### Neutral / known-unverified

- The Dependabot SHA-plus-comment co-update behaviour is documented
  by Dependabot but has not been observed in this repository. The
  Confirmation step below verifies it on the first post-merge bump.
- The G allow-list guards against introduction of disallowed actions
  but does not enforce pin style (SHA vs tag) per entry; the
  Tier A vs Tier B distinction still relies on human review or the
  deferred CI lint.

## Confirmation and Follow-up Tasks

**Confirmation (evidence the decision worked):**

- The first Dependabot PR after this ADR is merged that touches a
  Tier A action MUST update the SHA and the trailing `# vX.Y.Z`
  comment together. If it does not, the Dependabot assumption above
  fails and the ADR must be revisited.
- No new `uses:` line MAY be introduced after merge without the
  reviewer (maintainer) noting the tier classification in the PR
  description. This is the human-enforcement contract.
- The repository Settings → Actions allow-list is enabled within 30
  days of this ADR being accepted. If not enabled within that window,
  the G co-recommendation is not yet operative; re-evaluate whether
  human-only T5 enforcement is acceptable.

**Follow-up tasks (after approval):**

1. Update constitution Principle IX with a single informational
   cross-reference to this ADR. This is a clarification, not a new
   MUST, so a PATCH bump applies (1.8.0 → 1.8.1). If the
   decision-maker prefers a normative reference (introducing a MUST
   for ADR-002 conformance), a MINOR bump (1.8.0 → 1.9.0) applies
   instead per the Governance section of the constitution.
2. Close the source-finding issue for this ADR in the issue tracker
   once the ADR is accepted.
3. Leave the deferred CI lint issue open for the eventual SHA-enforcement automation;
   accept that it may not land soon and that human enforcement is
   the operative regime in the meantime.
4. Enable the GitHub repository allow-list under Settings → Actions to
   activate the G mechanical guard (see Confirmation above). This is a
   one-time settings change with no implementation cost.
5. SHA-pin `actions/upload-artifact` and `actions/download-artifact`
   in `.github/workflows/docker-publish.yml`. Both actions participate
   in the artifact-publish chain and are now classified as Tier A
   under the transitive-publish-chain criterion. Update the pins using
   the SHA-resolving helper selected in the CI lint follow-up.
6. Evaluate and implement pinning policy enforcement: either add a
   constitution principle referencing the Tier A/B rules for future
   workflow changes, or create a dedicated project review skill that
   checks workflow files for pin-style compliance. The review skill
   approach also serves as a fallback until the deferred CI lint lands.

## Revisit Triggers

This policy is not permanent by default. Revisit it on any of:

- a publicly disclosed compromise of the `actions/` or `github/`
  organisations, or of any Tier A publisher in active use;
- the first Dependabot Tier A PR that does not co-update SHA and
  version comment (invalidates the assumption above);
- annual review (next: 2027-05-16) — confirm the trade-off still
  reflects project scope, especially if the repo grows beyond
  single-maintainer scale;
- adoption of Option F or H, which changes the trust topology (G is
  the co-recommended baseline and does not re-open the decision when
  enabled).

## More Information

- Constitution [Principle IX (CI/CD Pipeline Security)](../../../.specify/memory/constitution.md)
  and [Principle IV (Simplicity / YAGNI)](../../../.specify/memory/constitution.md).
- [Dependabot configuration](../../../.github/dependabot.yml) — monthly
  grouped updates, ecosystem `github-actions`.
- [Feature concept doc](../../features/fork-safe-docker-ci/concept.md) —
  originally noted SHA pinning was out of scope for the fork-safe CI work.
- This ADR originated from a review of the mixed-pinning state in
  the CI workflows. The enforcement CI lint, curl|sudo binary-download
  supply-chain finding, and the parent code-review epic are all
  tracked separately in the project issue tracker.
- Methodology: [ADR-001](001-command-restrictions.md) uses a weighted
  decision matrix; ADR-002 uses MADR pros/cons because the options
  here represent categorically different risk models, not commensurable
  criteria.
