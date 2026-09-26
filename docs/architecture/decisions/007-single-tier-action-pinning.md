# ADR-007: Single-Tier GitHub Actions Pinning

Date: 2026-09-26
Status: Accepted — supersedes [ADR-002](002-github-actions-pinning-policy.md)
Deciders: Stefan (Product Owner)

## Decision

Every `uses:` reference in every workflow under `.github/workflows/` MUST be
pinned to a 40-character commit SHA carrying a full semantic-version comment:

```yaml
uses: owner/action@<40-char-sha> # vX.Y.Z
```

There is one tier. The identity of the publisher does not matter; the
permissions of the surrounding job do not matter. `actions/checkout` in a
read-only lint job is pinned exactly like `sigstore/cosign-installer` in the
publish job.

The comment MUST state the full `vX.Y.Z` version, not a major-only `vN`. The
comment is what a reader uses to judge how old a pin is, so a major-only
comment tells them almost nothing.

ADR-002's Tier B — a floating major tag (`@vN`) permitted for actions published
under the `actions/` or `github/` organisations — is withdrawn.

Two conditions are part of this decision, not follow-up work:

1. **Dependabot pull requests MUST NOT be auto-merged.** See "Condition A" below.
2. **The Dependabot interval for the `github-actions` ecosystem MUST be
   shortened** from monthly to weekly or daily. See "Condition B" below.

## Context and Problem Statement

ADR-002 established a two-tier policy: SHA pins for actions that are
credential-bearing, signing, building, publishing, or in a transitive publish
chain (Tier A), and floating major tags for permission-free actions published by
GitHub's own organisations (Tier B). The reasoning was proportionality — pay the
SHA-pin cost where the blast radius is real, and keep zero-touch patch delivery
where it is not.

Four months of operation falsified the cost model that made Tier B worth having.

### The two permitted forms are exhaustive, and drift produces a third

ADR-002 permits exactly two shapes: a SHA with a `# vX.Y.Z` comment, or a
floating `@vN`. A bare `@vN.Y.Z` — an exact version tag with no SHA — satisfies
neither. It has none of Tier A's immutability, because a tag can be retargeted
by whoever controls the upstream repository. It gives up Tier B's automatic
patch delivery, because the tag no longer floats. It is legal nowhere in the
policy, and it is strictly worse than either form it resembles.

### Dependabot produces exactly that third form

Commit `8427621` rewrote `actions/checkout@v7` to `actions/checkout@v7.0.1` at
four call sites. The mechanism is structural, not a misconfiguration: a floating
`@v7` already resolves to v7.0.1, so Dependabot cannot express a patch-level
update at all except by widening the reference until it names the patch.

The same commit shows the contrast. `actions/setup-python@v6` became `@v7` and
kept its major-only form, because that update crossed a major boundary and the
floating tag could therefore carry it.

That pattern holds across every Dependabot commit in the repository's history.
Major bumps preserve the form the reference already had (`actions/checkout@v4`
to `@v6`, then `@v6` to `@v7`, then `setup-python@v6` to `@v7`). The one
observed patch bump widened the reference instead.

So Tier B does not hold still. Every floating tag in the repository is queued to
drift into an illegal form on its publisher's next patch release. ADR-002
recognised this case and prescribed SHA-pinning the affected action as the
remedy — which, applied to every Tier B action in turn as each one drifts, is
this ADR arriving one action at a time.

### Two-tier enforcement is not achievable with the current tooling

`.github/zizmor.yml` sets `"actions/*": ref-pin` and `"github/*": ref-pin`, and
relies on zizmor's implicit `"*": hash-pin` default for everything else. That
expresses the *identity* half of ADR-002's Tier B test and nothing else.

ADR-002 makes an action Tier A if it satisfies identity **or** capability. So
`actions/checkout` inside a job holding `packages: write` is Tier A by
capability while still matching `"actions/*"` by identity. zizmor cannot see
that: it matches a `uses:` clause against the publisher patterns it is given and
models no job permissions at all, so the capability half of the rule is simply
absent from the check.

This is observable, not theoretical. `docker-publish.yml:156` sits in the `push`
job, which holds `packages: write` and `id-token: write`. It is pinned
`@v7.0.1`. It is Tier A by capability and satisfies no tier by form. The
`Pinning Lint` job passes it on every run.

Closing that gap under two tiers requires a checker that parses each workflow,
resolves the permissions in scope for each job — including the repository
default when a job declares no `permissions:` block — and applies the form rule
per job. No off-the-shelf tool does this, so it means writing and maintaining
one.

Under one tier the same gap closes by deleting configuration. zizmor documents
an implicit `"*": hash-pin` rule for any `uses:` clause matching no rule, so
removing the publisher policies leaves every action hash-pinned by default,
the tool is already wired into CI, and no capability analysis is needed because
the rule no longer depends on capability.

### The maintenance argument for Tier B is largely illusory

`.github/dependabot.yml` groups the `github-actions` ecosystem as
`patterns: ["*"]`. There is already exactly one grouped pull request per
interval covering every action in the repository. Tier B does not reduce the
number of pull requests to review; the grouping does. Tier B reduces only the
number of changed lines inside that single pull request.

### Current pin inventory

Twenty-one `uses:` references across four workflow files:

- 12 SHA pins with version comments — already conformant in form.
- 5 floating `@vN` tags — `actions/checkout` twice in
  `version-update-lint.yml`, and `actions/setup-python` three times across
  `molecule.yml` and `version-update-lint.yml`.
- 4 bare `@vN.Y.Z` references — all `actions/checkout`: `molecule.yml:19`, and
  `docker-publish.yml` at lines 55, 108 and 156.

`.github/workflows/*.yml` remains the source of truth for the live snapshot;
the numbers above size the migration, they do not replace reading the files.

Every bare reference is already tracked as an open defect. The three in
`docker-publish.yml` are one defect, and one of them — line 156, the checkout
step of the credentialed publish job — is the single highest-value reference in
the repository to get right (tracked in `ansible-all-my-things-ftfd`).
`molecule.yml:19` is a separate defect with a fix already on an open pull
request (tracked in `ansible-all-my-things-fwuw`), so whoever executes the
migration should confirm whether that pull request has landed before touching
that line.

The artifact actions carry major-only comments at three call sites:
`actions/upload-artifact@<sha> # v7` once, and
`actions/download-artifact@<sha> # v8` twice. All three satisfy the SHA
requirement but not the full-semver comment requirement, so their comments need
completing.

## Decision Drivers

The drivers are ADR-002's, unchanged in wording and priority order. Two of them
score differently against the evidence above, and that re-scoring is the
substance of why the decision changed.

1. **D1 — Supply-chain integrity for credential-bearing steps.** Code reached
   from a job holding `packages: write` or `id-token: write` must be referenced
   by something an attacker cannot mutate without our consent.
2. **D2 — Auditability.** A reviewer should be able to determine which action
   code will run by reading the workflow file alone.
3. **D3 — Security-patch velocity.** The path from "fix released" upstream to
   "fix running in our pipeline" should be as short as is consistent with D1.
4. **D4 — Maintenance and cognitive load.** Dependabot churn, contributor
   effort to add an action, reviewer time per pull request.
5. **D5 — No recurring out-of-pocket cost.** Free, OSS, or free-tier-sufficient
   tooling only.

### D3 re-scored

ADR-002 credited Tier B with preserving patch velocity: a floating tag picks up
a patch on the next workflow run with no human in the loop. That remains true
of a tag that stays floating.

What ADR-002 did not account for is that Dependabot ends the floating as soon as
it notices the patch. After `@v7` becomes `@v7.0.1`, the reference is pinned to
one exact version and delivers nothing automatically thereafter. The zero-touch
property Tier B was credited with survives exactly one patch release per action.

Tier B's real D3 advantage is therefore one patch cycle's head start, not
standing immunity to the Dependabot delay. Under one tier, D3 is served by the
interval instead — which is why Condition B below is part of this decision.

### D4 re-scored

ADR-002 treated Tier B as a net reduction in maintenance load. Against the
evidence, the ledger reverses:

- The pull-request count is set by Dependabot's grouping, not by the tiers.
- Tier B tags drift into a form that is illegal in both tiers, so each drift
  event creates remediation work that would not exist under a single tier.
- Catching that drift needs a job-capability-aware checker that does not exist
  and would have to be built and maintained.
- Two tiers require every contributor and every reviewer to classify each action
  before they can judge its pin, and the classification depends on job
  permissions that may be several lines away from the `uses:` line.

Tier B's D4 benefit is smaller than ADR-002 assumed and its D4 cost is larger.
It saves changed lines inside one grouped pull request, and charges a
classification rule, a drift-remediation stream, and a custom lint.

D1, D2 and D5 are unaffected. A single tier satisfies D1 and D2 at least as well
as two tiers did — it extends immutability and readability to the references
that previously had neither — and it needs no tooling beyond the zizmor job
already running.

## Considered Options

- **Option 1 — Keep the two-tier policy unchanged.** ADR-002 stands as written;
  each drift event is remediated individually as it appears.
- **Option 2 — Keep two tiers and build a custom lint.** Write a checker that
  encodes both halves of the rule: the permitted pin forms, and the job-scope
  capability test that decides which form applies.
- **Option 3 — Collapse to one tier (chosen).** Every reference is SHA-pinned
  with a full `# vX.Y.Z` comment; enforcement is zizmor's implicit `hash-pin`
  default.

Two options from ADR-002 are deliberately not re-opened. "Tag-pin everything"
fails D1 and D2 outright and was rejected on those grounds, which this evidence
does not disturb. "Buy a hardening product" is not an option here: no product
enforces a pin-form policy, so adopting one would leave this question
unanswered and add cost against D5. ADR-002's "do nothing" option is Option 1
in this list — with ADR-002 accepted, keeping the status quo *is* doing nothing.

### Pros and Cons of the Options

#### Option 1 — Keep the two-tier policy unchanged

- Good, because it costs nothing today: no workflow edits, no config change, no
  reader has to learn a new rule.
- Good, because Tier B actions retain one patch cycle of zero-touch delivery
  after each Dependabot pin (D3, bounded as re-scored above).
- Bad, because it is not enforceable with the tooling in place. The two-tier
  rule turns on job permissions and zizmor is configured on publisher identity,
  so a Tier A action wearing a Tier B publisher's name passes CI while
  violating the policy. This is not a gap to be closed later; it is the current
  state of `main`.
- Bad, because every remaining floating tag is queued to drift into a form that
  is legal in neither tier, so the violation count grows on upstream's
  schedule rather than ours.
- Bad, because the classification burden is permanent: each `uses:` line must be
  read together with its job's `permissions:` block before its pin form can be
  judged.

##### Mitigations

- The enforcement gap cannot be mitigated within this option. Any mitigation is
  either a custom lint (Option 2) or the removal of the capability half of the
  rule (Option 3). Honest framing: choosing Option 1 is choosing a policy that
  CI does not enforce and a reviewer must apply by hand on every pull request.
- Drift remediation can be made routine rather than eliminated, by SHA-pinning
  each action as it drifts — which converges on Option 3 one action at a time,
  without ever writing down that it has.

#### Option 2 — Keep two tiers and build a custom lint

- Good, because it is the only option that makes ADR-002 as written actually
  enforceable, closing the gap that Option 1 leaves open.
- Good, because it keeps Tier B's D3 head start for permission-free actions.
- Bad, because it requires new code to write, test, and maintain: a workflow
  parser, a per-job permission resolver that models the repository default token
  scope for jobs with no `permissions:` block, and the form rules. That is a
  standing D4 cost charged against a D4 benefit the re-scoring above already
  found to be small.
- Bad, because the lint must track GitHub's own semantics. Permission defaults,
  reusable-workflow permission inheritance, and matrix-expanded jobs all change
  what "the permissions in scope here" means, and each change is a maintenance
  event.
- Bad, because it does not stop Tier B drift; it only reports it. The bare
  `@vN.Y.Z` form still arrives on every patch release and still has to be fixed
  by hand.
- Bad, because it contradicts Principle IV (Simplicity / YAGNI): custom
  infrastructure to enforce a distinction whose benefit the evidence has already
  shrunk.

##### Mitigations

- The maintenance cost could be reduced by keeping the lint narrow — form rules
  only, no capability analysis. But that is precisely zizmor's current
  behaviour, so the result enforces Option 3's rule while the documented policy
  still claims two tiers. Not a mitigation; a divergence.
- The D4 cost cannot be mitigated away. Writing and owning a checker is the
  option.

#### Option 3 — Collapse to one tier (chosen)

- Good, because the rule is checkable by looking at one line. No publisher
  allow-list, no job-permission lookup, no tier to argue about.
- Good, because it is enforceable today with the tool already in CI: remove the
  publisher policies from `.github/zizmor.yml` and zizmor's documented blanket
  `hash-pin` default covers every action. No new code (D4, D5).
- Good, because it closes the drift class entirely. A SHA pin has no looser form
  for Dependabot to widen into, so the illegal third shape can no longer appear.
- Good, because it extends D1 and D2 to every reference, including the
  credentialed publish job's checkout step that satisfies no tier today.
- Good, because the Dependabot behaviour it depends on is the confirmed one:
  every SHA-pinned entry in commit `8427621` had its SHA and its trailing
  version comment rewritten together, never one without the other.
- Bad, because a patch fix for any action now waits for a Dependabot pull
  request and a human merge. Nothing arrives by itself any more (D3).
- Bad, because adding a new action requires looking up a SHA rather than copying
  a tag (D4, small and one-off per action).
- Bad, because the grouped Dependabot pull request gets larger: more references
  change per cycle, and each one is an opaque 40-character hash rather than a
  readable tag bump.

##### Mitigations

- Patch-delivery delay is mitigated by shortening the Dependabot interval —
  Condition B below, part of this decision rather than a follow-up. It is
  mitigated, not eliminated: a human merge is now on the critical path by
  design, because that approval is the control D1 is buying.
- SHA lookup friction is mitigated by a free OSS resolver such as `pinact` or
  `ratchet`, which rewrites `owner/action@vX.Y.Z` to
  `owner/action@<sha> # vX.Y.Z` in place. Adopting one is optional and
  D5-compatible; until then the lookup is a manual visit to the upstream
  release.
- Review burden on a larger diff is mitigated by the version comments: the
  reviewer reads the `# vX.Y.Z` change to see what moved and consults the
  upstream release notes, rather than diffing hashes. This is why the comment is
  mandatory and why major-only comments are not acceptable — `# v8` to `# v8`
  tells a reviewer nothing about what changed.
- The known limit of a SHA pin is not mitigable and is accepted: it guarantees
  that the referenced commit does not change, not that the code at that commit
  is trustworthy. An action that was malicious when its SHA was chosen, or that
  fetches code at runtime, remains a risk. SHA pinning is necessary, not
  sufficient.

## Condition A — Dependabot pull requests are not auto-merged

Auto-merging Dependabot pull requests is ruled out for the `github-actions`
ecosystem. This is the decision's central fragility and the reason it is
recorded here rather than left to operational preference.

The threat SHA pinning defends against is a compromised publisher pushing a
malicious release. The SHA pin defeats the tag-retarget path: the attacker
cannot move code under an existing reference. But Dependabot will still notice
the new release and still offer its hash in a pull request. If that pull request
merges without a human reading it, the malicious release lands in the pipeline
unattended — through the front door, on the next scheduled run.

SHA pinning plus auto-merge is therefore strictly worse than floating tags: the
same exposure, plus the ceremony of hashes and comments that buys nothing. The
entire value of a SHA pin is that a person approves each hash change.

A future reader looking for efficiency will find auto-merge an obvious
candidate. It is not available as an efficiency. Adopting it re-opens this
decision, because it removes the control the decision exists to create.

## Condition B — The Dependabot interval must be shortened

The `github-actions` ecosystem in `.github/dependabot.yml` is currently set to
`interval: monthly`. Under a single tier that interval becomes the repository's
patch-delivery latency for every action, with a worst case near 30 days of
running a version whose fix is already published upstream. Under the two-tier
policy a floating tag absorbed part of that delay; nothing absorbs it now.

The interval MUST be shortened to `weekly` or `daily` for the `github-actions`
ecosystem. This is part of the decision: the single tier is accepted on the
understanding that D3 is served by cadence, since it is no longer served by
floating tags.

The grouping (`patterns: ["*"]`) stays. It is what keeps the review burden to
one pull request per interval, and it is the reason a shorter interval is
affordable at all: weekly grouped updates are one pull request a week, not one
per action.

## Consequences

### Positive

- One rule, checkable on one line, with no classification step. A reviewer or
  agent judges any `uses:` line without reading the surrounding job.
- Enforcement becomes real rather than aspirational, using a tool already in
  CI. The policy itself is expressed by removing configuration from
  `.github/zizmor.yml`; making the check fail on a violation additionally
  needs the workflow change recorded under Negative below.
- Immutability and auditability extend to every reference, including the
  checkout step of the credentialed publish job, which satisfies no tier today.
- The drift class is closed. A SHA pin has no looser form to widen into, so the
  bare `@vN.Y.Z` shape cannot recur.
- The version comment becomes a reliable review aid, because it always carries
  the full version.

### Negative

- No action receives a patch without a human merge. Patch latency is bounded by
  the Dependabot interval (Condition B), and a run between a release and that
  merge uses the older code.
- Adding an action costs a SHA lookup.
- The grouped Dependabot pull request carries more hash changes per cycle, and
  a hash is unreadable without its version comment.
- A SHA-pinned action can still execute code the SHA does not cover: composite
  action chains, `curl | bash` inside a `run:` step, or a container image pulled
  at runtime. This policy narrows the surface; it does not close it. Non-`uses:`
  third-party code execution in `run:` steps remains outside the scope of any
  pinning policy, exactly as ADR-002 recorded.
- Nine non-conformant references need migration before the repository satisfies
  its own policy; until that lands, tightening
  `.github/zizmor.yml` would fail CI.
- `Pinning Lint` must invoke zizmor twice, so the audit runs twice per job. A
  single invocation cannot both report and enforce: `advanced-security: true`
  selects zizmor's SARIF format, which exits 0 even on a finding, and the
  action propagates that exit code. Observed by experiment — one floating
  `@vN` reference produced a SARIF finding at `error` level and a green check.
  The reporting run keeps the code-scanning alerts; a second run with
  `annotations: true` selects `--format=github`, exits 14 on a finding, and is
  what turns the check red.

### Neutral

- The GitHub repository allow-list (Settings → Actions) is unaffected. It
  controls which action repositories may be used at all, not how they are
  pinned, and it remains the guard against a new action being introduced at all.
  Its entry list stays in `CONTRIBUTING.md § Fork setup (one-time)`.
- Upstream renames still do not follow a SHA pin. A renamed action breaks the
  pin and is fixed by hand. This was already true for every Tier A pin and now
  applies to all of them.

## Migration Scope

The policy above describes the target state. Reaching it means:

- Replacing 5 floating `@vN` references with SHA pins and full version
  comments.
- Replacing 4 bare `@vN.Y.Z` references with SHA pins and full version
  comments — `docker-publish.yml:156`, the publish job's checkout step, first,
  and `molecule.yml:19` unless the open pull request named above has already
  landed it.
- Completing the artifact actions' major-only comments to full semantic
  versions at all three call sites.
- Deleting the whole `unpinned-uses` block from `.github/zizmor.yml` so the
  documented blanket `hash-pin` default applies — after the references above
  conform, since the tightened check fails on any that do not. Delete the
  block rather than only its two `ref-pin` lines: that would leave `policies:`
  empty, and the blanket default is documented for a `uses:` clause matching no
  rule, not for an empty policy map.
- Shortening the `github-actions` interval in `.github/dependabot.yml`
  (Condition B).
- Replacing Principle IX.4's two-tier text in the constitution with the
  single-tier rule, and removing the tier vocabulary from `.github/zizmor.yml`
  comments and `CONTRIBUTING.md` wherever it appears.

This ADR records the decision only. No workflow, configuration, or constitution
file is changed by it.

## Revisit Triggers

- Any Dependabot pull request that rewrites a SHA without co-updating its
  version comment, or the reverse. The co-update behaviour is confirmed and this
  decision leans on it; a regression invalidates the review story.
- A patch-delivery delay that causes real exposure in practice — a known
  vulnerability running in the pipeline because a grouped pull request sat
  unreviewed. The answer is a shorter interval or a narrower group, never
  auto-merge (Condition A).
- Growth beyond single-maintainer scale, where the review-per-hash assumption
  behind Condition A may no longer hold and a different control is needed.
- Annual review (next: 2027-09-26).

## More Information

- [ADR-002](002-github-actions-pinning-policy.md) — the superseded two-tier
  policy. Its threat model (T1–T6), project blast radius, and full options
  analysis remain the reasoning this decision is built on and are not restated
  here.
- Constitution
  [Principle IX (CI/CD Pipeline Security)](../../../.specify/memory/constitution.md),
  whose clause 4 states the two-tier rule this ADR supersedes, and
  [Principle IV (Simplicity / YAGNI)](../../../.specify/memory/constitution.md).
- [Dependabot configuration](../../../.github/dependabot.yml) and
  [zizmor configuration](../../../.github/zizmor.yml) — the two files whose
  current contents this decision is measured against.
- [CONTRIBUTING.md § Fork setup](../../../CONTRIBUTING.md#fork-setup-one-time) —
  the canonical allow-list entry list.
- Methodology: MADR pros and cons, matching ADR-002, because the options remain
  categorically different risk models rather than commensurable criteria.
