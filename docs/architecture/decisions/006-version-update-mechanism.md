<!-- SPDX-License-Identifier: MIT-0 -->

# ADR-006: Version Update Mechanism for Role Version Pins

Date: 2026-09-19
Status: Proposed
Deciders: Stefan (Product Owner)

## Context and Problem Statement

Roles in this repository install tools by downloading a specific versioned
artefact from upstream. Each such role pins that choice in its
`defaults/main.yml` as literal values: a version string, and — for most
tools — one SHA-256 checksum per supported CPU architecture. A role never
resolves its own version at converge time; it reads the pin and verifies
the download against the pinned digest before placing the artefact. The
consumption side of that contract is described in the
[checksum-verification pattern][pattern].

Keeping those pins current is the job of a separate mechanism,
`playbooks/update-versions/`, documented in
[`version-update-playbooks.md`](../version-update-playbooks.md). It is a
pair of Ansible playbooks on localhost — one that reports stale pins and
exits non-zero, one that resolves upstream versions and rewrites the
defaults files in place — sharing a directory of per-strategy fetch task
files.

### Why the mechanism is larger than it looks

The tracked tools do not share one upstream shape. The authoritative
enumeration is the stale-check list in `query-versions.yml`; at the time of
this decision it covers eighteen tools resolved through eight distinct
upstream kinds: GitHub releases, a GitHub commit SHA, a vendor release
manifest in JSON, a language-SDK REST API restricted to same-major
patches, a distribution index, a vendor desktop-release feed, an
object-storage release manifest, and an HTML page scraped with a regular
expression because the vendor publishes no machine-readable manifest.

Checksums add a second axis. Some upstreams publish the digest in the same
manifest as the version. Others publish an aggregate checksums file per
release. Others publish nothing, and the digest must be computed from the
downloaded archive. Most tools need two digests, one per architecture, and
a version pin written without the digests that belong with it is worse
than no update at all.

The result, at the time of this decision, is roughly 2,550 lines of YAML
across the two playbooks and their shared task files, plus about 720 lines
of Python implementing an apply-order checker and its unit tests, plus a
separate Ansible test harness with its own CI job. None of this provisions
a machine; all of it exists to keep eighteen literals current.

### What triggered the reassessment

Recent work hardened the mechanism rather than extending it: per-tool
failure isolation, so one upstream outage no longer hides every tool after
it, and a failure classifier that decides whether a failure belongs to a
third party or to this repository. That hardening is sound, but it is also
evidence — the mechanism has reached the size at which it needs its own
reliability features, its own contract tests, and its own CI gates.

Two further facts sharpen the question. The per-tool marginal cost is now
high: Constitution Principle II requires every role that pins a version to
register a fetch task file, a read-current-pin task, an upstream-query
task, an update task and a fetch include — five edit sites across two
playbooks, enforced by a checker that will reject the change if the
apply-order contract is violated. And the mechanism is young; its design
has changed materially several times and can be expected to change again.

**Decision: which mechanism should keep this repository's role version
pins current, and how much of it should this project own?**

## Overriding Constraint: Literal Checksum Pins

**The repository must state the exact bytes it expects, as reviewable
literals in `defaults/main.yml`. No decision driver below may be traded
against this.**

This is the reason the pinning exists at all. Without it the sound choice
would be to install each tool's latest release unverified and accept
whatever upstream serves; the entire apparatus of versions, digests and
update playbooks is the price of not doing that. An option that reduces
that apparatus by weakening the guarantee has not solved the problem, it
has abandoned it.

It is the same reasoning that already makes Principle IX SHA-pin
third-party GitHub Actions. A literal digest defends against an upstream
artefact being replaced *after* it was pinned — a retagged release, a
force-pushed tag, a compromised account backfilling an old release. Under
literal pins that fails loudly on every converge. Under install-time
verification against an upstream checksums file it does not, because
whoever replaces the artefact replaces the checksums file in the same
motion; that shape is integrity in transit only, and it is why the
live-checksum-URL consumption form was retired.

Consequence for this decision: **any candidate must be able to write
checksums, not only version strings.** This eliminates Dependabot and the
Mend-hosted Renovate app before the drivers are applied.

Note that this constraint is a gate, not a discriminator. Every option
surviving it can satisfy it. Where integrity still separates options — a
guarantee enforced structurally versus one policed by a checker — that
difference is carried by driver 3 below.

## Further Constraints

- **C2 — Batched, scheduled pull request.** The end state is one
  scheduled job that sweeps all tools and opens a single pull request
  containing every stale pin, reviewed and merged by the maintainer. Not
  one pull request per tool, and no automatic commits to the default
  branch.
- **C3 — Constitution compliance.** Fail loud on any value that cannot be
  resolved (Principle XII); no untracked duplication of the pin
  definitions (Principle XI); Python scripts ship with a `test_`-prefixed
  sibling (Technology Stack).

## Decision Drivers

These rank the options that survive the overriding constraint. They are
listed in the priority established with the Product Owner, and they
discriminate — each one separates at least two surviving options.

1. **Maturity must sit in the resolve layer.** The layer that has actually
   broken in this repository is upstream resolution: a vendor publishing
   two release lines from one tag namespace, a renamed checksums file
   carrying hashes that did not match the archives, a release missing the
   asset this project installs. A candidate that leaves upstream querying
   as bespoke local code does not address the concern that motivated this
   review, however mature its scheduling and pull-request machinery.
2. **Cost of ownership.** One driver covering both the standing surface
   and the per-tool friction, because they are the same complaint: every
   line of the update mechanism is infrastructure for the infrastructure,
   and registering a newly pinned tool should be a small, declarative,
   single-site change rather than five edit sites across two playbooks
   plus a checker that must be kept satisfied.
3. **Integrity guaranteed structurally, not policed.** The overriding
   constraint sets the bar; this driver ranks how it is held. A mechanism
   in which a version cannot be written without its digests — because one
   function produces both and writes them in one transaction — is better
   than one in which a separate checker forbids the ordering that would
   break the pairing. A guarantee that depends on a rule being enforced
   can be lost by removing the enforcement; one that depends on a shape
   cannot.
4. **Fit with the existing Ansible and CI architecture.** The control node
   already carries a Python virtual environment and a `requirements.txt`;
   CI already runs scheduled jobs and already receives bot pull requests.

## Considered Options

- **A — Do nothing.** Keep `playbooks/update-versions/` as it stands.
- **B — Manual operator workaround.** Retire the automation; check
  upstreams by hand on a cadence.
- **C — Restructure the existing mechanism in place.** Replace the
  per-tool copy-paste sections with a declarative tool registry and one
  resolver per upstream kind, in tested Python, with no new dependency.
- **D — Dependabot.** Already present in this repository for GitHub
  Actions, devcontainers and Docker.
- **E — Renovate, Mend-hosted app.**
- **F — Renovate, self-hosted as a GitHub Action.** Custom managers and
  custom datasources for resolution; `postUpgradeTasks` invoking a local
  script for checksums.
- **G — updatecli.**
- **H — nvchecker for resolution, plus a tested Python tool for checksums
  and pin writing.**
- **I — Buy a commercial dependency-management product.**

### Pros and Cons

#### A — Do nothing

- Good, because it is already working, already tested, already isolated
  per tool, and already understood by its author.
- Good, because it owes nothing to any third party's roadmap or
  availability, and runs offline on a laptop.
- Bad, because the marginal cost per tool stays at five edit sites across
  two playbooks plus a checker that must be kept satisfied (driver 2).
- Bad, because it puts no maturity anywhere (driver 1); every future
  upstream change is this project's design problem.
- Bad, because the HTML scrape of the Android download page remains an
  accepted, unmitigated fragility, recorded as technical debt TD-009 in
  `docs/architecture/technical-debt/technical-debt.md`.
- Neutral: the code volume is stable, not growing, as long as the tool
  count is stable — but the tool count is what has been growing.

#### B — Manual operator workaround

- Good, because it removes the entire mechanism, its tests and its CI
  jobs at a stroke — the largest possible reduction against driver 2.
- Good, because a human reading a release page catches things no matcher
  catches: a deprecation notice, a changed artefact naming scheme, an
  advisory.
- Bad, because it does not scale past a handful of tools and this project
  is past that point; the problem statement of the existing mechanism
  already records that manual checking is "error-prone and often skipped".
- Bad, because stale pins are a security exposure, and the failure mode of
  a skipped manual check is silence.
- Bad, because computing a per-architecture digest by hand for every tool
  is exactly the work most likely to be shortcut under time pressure,
  which puts the overriding constraint at risk in practice even while
  honouring it on paper.

#### C — Restructure in place

- Good, because the marginal cost per tool collapses to one registry entry
  (driver 2), and the eight upstream kinds become eight tested resolver
  functions rather than eighteen playbook sections.
- Good, because Python unit tests replace an Ansible contract harness and
  a bespoke apply-order checker; the ordering invariant that checker
  enforces becomes unexpressible rather than merely policed, since a
  single writer function writes version and digests together.
- Good, because it introduces no new dependency and keeps the mechanism
  runnable offline.
- Bad, because it buys no maturity at all (driver 1). This is the driver
  the Product Owner ranked first, and this option scores zero on it.
- Bad, because the upstream-querying code — the part that actually breaks
  — remains entirely this project's to design, debug and redesign.
- Neutral: it is the fallback shape underneath every other option, since
  even the chosen option needs a pin writer.

#### D — Dependabot

- Good, because it is already configured here, needs no credentials, and
  its pull requests are already an accepted part of the workflow.
- Bad, and disqualifying: Dependabot supports a fixed set of package
  ecosystems. An arbitrary version literal in an Ansible role's
  `defaults/main.yml` is not one of them, and there is no custom-manager
  or custom-datasource extension point. It cannot see these pins at all.
- Bad, because it cannot write checksums under any configuration,
  violating the overriding constraint.
- Neutral: it stays in place for the ecosystems it does cover. This
  decision does not displace it.

#### E — Renovate, Mend-hosted app

- Good, because it requires no runner, no token management and no
  operational ownership.
- Bad, and disqualifying: the hosted app does not execute
  `postUpgradeTasks`, and `allowedCommands` is a self-hosted-only option.
  Without a post-upgrade command there is no way to derive a checksum for
  a version Renovate has just bumped, so the overriding constraint
  cannot be met.
- Bad, because the small set of post-upgrade commands the hosted app does
  permit is deliberately undocumented and subject to change, which is not
  a foundation for a supply-chain control.

#### F — Renovate, self-hosted as a GitHub Action

- Good, because Renovate is by far the most mature and widely deployed
  option, with a large ecosystem, and because its configuration is a
  format many engineers can already read.
- Good, because its plumbing is genuinely excellent: scheduling, caching,
  host rate limiting, retries, grouping, pull-request lifecycle,
  changelog rendering and a dependency dashboard.
- Good, because `customDatasource` is more capable than it first appears.
  It supports `format: html`, which extracts versions from a page's
  hyperlinks and would retire the Android HTML-scraping debt (TD-009);
  `format: json` with JSONata `transformTemplates`, which covers the
  vendor manifest, SDK API, distribution index and desktop-feed shapes;
  and a release object may carry a `digest` field beside its `version`.
- Good, because for the two tools whose upstream publishes the checksum in
  the same manifest as the version, that `digest` support makes the
  checksum update fully declarative — no script at all.
- Bad, and central: it does not satisfy driver 1. Renovate's maturity
  covers the plumbing, which is not where this repository breaks. Under
  this option the resolve layer remains bespoke local configuration —
  roughly eighteen custom-manager regular expressions plus five custom
  datasources with JSONata expressions — and the checksum layer remains a
  bespoke local script. The vendor-with-two-release-lines problem, the
  renamed-checksums-file problem and the missing-asset problem all stay
  exactly where they are, restated in a second configuration language.
- Bad, because the per-architecture checksum shape fights the tool's
  model. Renovate carries one digest per dependency, so a tool needing an
  amd64 and an arm64 digest must be declared as two dependencies, or be
  handled by a post-upgrade script. For the majority of tools here, whose
  digests live in a per-release aggregate checksums file that a datasource
  cannot enumerate in one call, the script is unavoidable.
- Bad, because `postUpgradeTasks` is gated by `allowedCommands`, a
  self-hosted global option supplied as a regular-expression allow-list
  via environment variable — a security-relevant configuration surface
  this project would own and must get right.
- Bad, because the batched-single-pull-request end state (C2) uses little
  of what makes Renovate worth adopting; grouping everything into one pull
  request discards the per-dependency lifecycle that is its main asset.
- Bad, because of two concrete integration costs: `renovatebot/github-action`
  holds `contents: write` and is therefore Tier A under ADR-002, requiring
  a SHA pin and an addition to the allow-list in `CONTRIBUTING.md`; and
  pull requests opened with the default `GITHUB_TOKEN` do not trigger other
  workflows, so Molecule and the lint jobs would not run on update pull
  requests unless a GitHub App or personal access token is introduced.

#### G — updatecli

- Good, because its source/condition/target manifest model fits this
  problem shape directly, and its `shell` target handles checksum
  computation natively rather than through a bolted-on hook.
- Good, because it opens pull requests itself and can express "update
  these files together" as a first-class concept.
- Bad, because it fails driver 1 on its own terms: it is a smaller, less
  widely deployed project than the mechanism it would replace is likely to
  become, with a thinner ecosystem and fewer people exercising its edge
  cases. Adopting it trades code this project understands for a dependency
  whose maturity advantage is not clearly established.
- Bad, because its resource plugins for the shapes here (vendor JSON
  manifests, SDK APIs, HTML pages) reduce to generic HTTP-plus-matcher
  resources, which is the same bespoke matching the current mechanism
  already contains, expressed in another manifest language.

#### H — nvchecker plus a Python pin writer

nvchecker is a version-tracking tool used routinely by distribution
packagers, packaged in Arch Linux, in its second major version and a
decade old. Its configuration is TOML: one stanza per tracked tool naming
a source plugin and its parameters. It resolves versions only; it does not
compute checksums, does not write files and does not open pull requests.

- Good, because it owns precisely the resolve layer (driver 1). Every
  upstream kind tracked here maps onto a stock source plugin: `github`
  with `use_latest_release`; `git` with `use_commit` for the commit-SHA
  pin; `jq` against a JSON endpoint for the vendor manifest, SDK API,
  distribution index, desktop feed and object-storage manifest; and
  `android_sdk`, which reads Google's own `repository2-1.xml` package
  index and therefore **retires the TD-009 HTML-scraping debt** rather
  than containing it.
- Good, because the resolve layer becomes roughly one four-line TOML
  stanza per tool (driver 2), replacing the query playbook and the whole
  directory of fetch task files.
- Good, because the failure classes that have bitten this repository have
  declarative answers in the idiom the tool exists for: the
  two-release-lines problem is an `include_regex`, the same-major SDK
  restriction is `include_regex` plus a `from_pattern`/`to_pattern`
  rewrite.
- Good, because what remains to own is small and sharply scoped: a Python
  tool taking a tool name and a resolved version, producing the
  per-architecture digests and rewriting the defaults file atomically.
  That tool is unit-testable without network access and carries the
  exactly-once pin-write guard, the asset-existence guard and the
  write-nothing-unless-every-pin-of-a-file-validates rule the current
  `write-pins.yml` already implements (drivers 2 and 3).
- Good, because the overriding constraint is held structurally rather than
  policed (driver 3): version and digests are produced by one function and
  written in one transaction, so the apply-order contract the Python
  checker currently polices becomes impossible to express, and roughly 720
  lines of checker and checker tests are deleted rather than ported.
- Good, because it fits the existing architecture (driver 4): a Python
  package added to `requirements.txt` beside Molecule, run from the same
  virtual environment, on the control node, offline-capable apart from the
  upstream queries themselves.
- Bad, because it is a new runtime dependency on the control node and in
  CI, on a project maintained by a small team.
- Bad, because nvchecker supplies a mature *engine*, not mature *per-tool
  judgement*. Deciding that a given repository needs `include_regex` is
  still this project's call; nvchecker only makes expressing that decision
  a single declarative line.
- Bad, because the batched pull request is not provided: a scheduled
  workflow plus a create-pull-request action must be wired, and that
  action is Tier A under ADR-002.
- Neutral: nvchecker's own `nvtake`/version-record model is not needed
  here, because the defaults files are already the version record. Only
  the `newver` output is consumed.

#### I — Buy a commercial dependency-management product

- Good, because a vendor absorbs maintenance and provides support,
  advisories and a policy interface.
- Bad, and disqualifying on fit: the commercial offerings in this space —
  Mend's Renovate Enterprise tier, Snyk, and comparable software
  composition analysis products — are built to parse recognised package
  manifests for known ecosystems and to correlate them with vulnerability
  databases. A hand-written version literal in an Ansible role's defaults
  file is invisible to all of them without the same custom-matcher work
  this decision is trying to avoid, and none of them will compute and
  write a per-architecture archive digest.
- Bad, because the costs are disproportionate: a per-seat or per-project
  subscription and, for the hosted tiers, granting a third party write
  access to the repository, in exchange for capability this project
  already has.
- Neutral: the vulnerability-advisory half of what these products sell is
  a genuinely different concern from keeping pins current, and could be
  revisited on its own merits later without reopening this decision.

## Decision Outcome

**Recommended: Option H — nvchecker for the resolve layer, plus a tested
Python tool for checksum resolution and pin writing, driven by a scheduled
GitHub Actions workflow that opens one batched pull request.**

Every option reaching this point clears the overriding constraint, so
integrity did not decide between them; H and C hold it equally, and
structurally. The choice is therefore made on the drivers, and driver 1 is
where the options genuinely part.

The decision turns on driver 1. Renovate (F) is the more mature product by
a wide margin, and if the pain were scheduling, deduplication, rate
limiting or pull-request lifecycle, it would be the obvious answer. But
the failures this repository has actually absorbed are all in upstream
resolution, and Renovate does not own that layer for dependencies it has
no native datasource for — it would remain this project's code, merely
rewritten as custom managers and JSONata. Adopting Renovate would add a
configuration language without removing the class of problem that
prompted the review, and C2 discards most of what would have justified the
cost anyway.

nvchecker is the only candidate that is mature *in the layer that breaks*.
The trade is deliberate and narrow: this project gives up owning upstream
querying, and keeps owning the checksum-and-write step, which is where its
genuinely project-specific rules live — the exactly-once pin match, the
asset guard, the all-or-nothing file write, the refusal to write a version
without its digests. Those rules were earned by real incidents and should
not be delegated.

Option C is the honest fallback. If the new dependency proves unwelcome,
C delivers drivers 2 and 3 in full and only forfeits driver 1 — and
because H's pin writer is C's pin writer, choosing H first costs nothing
if the resolve layer is later brought back in-house.

The resulting shape:

| Layer | Owner | Form |
| --- | --- | --- |
| Which version is current upstream | nvchecker | TOML stanza per tool |
| Which digests belong to that version | this project | tested Python |
| Writing version and digests together | this project | tested Python |
| Scheduling and opening the pull request | GitHub Actions | workflow |
| Reviewing and merging | maintainer | unchanged |

### Consequences

- `playbooks/update-versions/` is retired: both playbooks, the fetch task
  files, the Ansible test harness and its CI job, and the apply-order
  checker with its unit tests.
- The apply-order contract and the ban on direct file edits during the
  apply phase are no longer enforced by a checker. They do not need to be:
  a single writer that takes a version and its digests together cannot
  express the ordering violation the checker existed to catch. The
  existing requirement that this ban "MUST survive any simplification or
  removal of that checker" is therefore satisfied structurally rather than
  by a replacement CI step.
- Constitution Principle II must be amended. Its current wiring
  requirement names a fetch task file, a read-current-pin task, an
  upstream-query task, an update task and a fetch include. Under this
  decision, registering a tool is one nvchecker stanza and one registry
  entry for the pin writer. The requirement that an unregistered tool
  silently escapes version tracking is unchanged; only the mechanism it
  names moves.
- `version-update-playbooks.md` and the checker's own README are replaced.
  The checksum-verification pattern stands unchanged: the consumption
  contract it describes is untouched, and only the sentence naming
  `perform-updates.yml` as the resolver needs retargeting.
- TD-009 (Android HTML-scraping fragility) is closed rather than carried.
- `requirements.txt` gains nvchecker; CI gains a scheduled workflow and a
  create-pull-request step, both Tier A under ADR-002 and both requiring
  allow-list entries in `CONTRIBUTING.md`.
- The failure-classification model — whether a failure is `upstream` or
  `configuration` — is preserved in the Python tool rather than ported
  literally. It becomes cheaper to express: nvchecker's non-zero exits and
  per-entry errors are upstream by construction, and everything the pin
  writer raises is this repository's own.
- Offline behaviour is retained: both nvchecker and the pin writer run on
  the control node from the project virtual environment, so the maintainer
  can still run a sweep locally and read `git diff` before anything
  reaches CI.

### Mitigations for the negative consequences

- **New dependency, small maintainer team.** nvchecker is pinned by
  version in `requirements.txt` like every other control-node dependency,
  so an upstream regression cannot arrive unannounced. Its output
  contract is one JSON-ish name-to-version mapping; should the project
  become unmaintained, replacing it means writing the eight resolvers of
  option C behind the same interface, with the registry and the pin writer
  untouched. The blast radius is one layer, and option C is the
  pre-costed exit.
- **Mature engine, not mature judgement.** Each tool's stanza is a
  reviewable claim about how its upstream publishes. The pin writer's
  asset guard keeps that claim checked: a resolved version whose expected
  artefact does not exist fails the run naming the tool, the version and
  the missing artefact, which is the same protection
  `required_asset_regexes` provides today.
- **Batched pull request must be wired by hand.** This is a one-time cost
  of about one workflow file, and it is a cost option F shares in
  practice, since Renovate's grouping would need configuring to produce
  the same single pull request.
- **Pull requests opened by a bot may not trigger the existing CI jobs.**
  Resolve this once, explicitly, when the workflow is written: either a
  GitHub App token, or accept that the maintainer re-runs checks on the
  update branch. It must be decided rather than discovered, since silent
  non-execution of Molecule on an update pull request would be a
  regression against Principle III.
- **Loss of the stale-check exit code (FR-002).** The scheduled workflow
  fails when the pin writer reports stale pins that it could not resolve,
  and the pull request itself is the visible signal for pins it could.
  If a hard gate is wanted in addition, the pin writer's dry-run mode
  provides it as its own CI step.

## Confirmation

The decision is confirmed in the implementing branch by:

- Unit tests for the pin writer covering: a renamed pin, a duplicated pin,
  a missing pin, a value containing a quote, backslash or newline, and the
  all-or-nothing guarantee that a file with one bad pin is left untouched.
- A test proving a version is never written without its digests.
- An end-to-end run against the real upstreams producing a diff
  equivalent to what the retired playbook produces for the same day.
- A second run immediately afterwards producing no changes (Principle I).
- The amended Principle II and the rewritten documents landing in the same
  branch as the code, so no document describes a retired mechanism.

## More Information

- [`version-update-playbooks.md`](../version-update-playbooks.md) —
  the mechanism being replaced, including its failure-classification rules
  and apply-order contract.
- [checksum-verification pattern][pattern] — the consumption contract,
  unchanged by this decision.
- [ADR-002](002-github-actions-pinning-policy.md) — the action-pinning
  tiers that govern any workflow added here.
- The data-driven tool-registry refactor that option C describes was
  previously evaluated and deferred as not worth the indirection at a
  smaller tool count (tracked in `ansible-all-my-things-3ikt`). This
  decision revisits that judgement at the current count.
- nvchecker documentation: <https://nvchecker.readthedocs.io/>
- Renovate custom datasources:
  <https://docs.renovatebot.com/modules/datasource/custom/>
- Renovate `postUpgradeTasks` and the self-hosted-only `allowedCommands`:
  <https://docs.renovatebot.com/self-hosted-configuration/>
- updatecli: <https://www.updatecli.io/docs/core/configuration/>

[pattern]: ../concepts/checksum-verification-pattern.md
