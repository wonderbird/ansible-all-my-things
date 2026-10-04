<!-- SPDX-License-Identifier: MIT-0 -->

# ADR-006: Version Update Mechanism for Role Version Pins

Date: 2026-10-04
Status: Proposed
Deciders: Stefan (Product Owner)

## Context and Problem Statement

Roles in this repository install tools by downloading a specific versioned
artefact from upstream. Each such role pins that choice in its
`defaults/main.yml` as literal values: a version string, and — for most
tools — one SHA-256 checksum per supported CPU architecture. A role never
resolves its own version at converge time; where it pins a digest, it
verifies the download against that digest before placing the artefact. The
consumption side of that contract, and the role that verifies against a live
checksums file instead, are described in the
[checksum-verification pattern][pattern].

Keeping those pins current is the job of a separate mechanism,
`playbooks/update-versions/`, documented in
[`version-update-playbooks.md`](../version-update-playbooks.md). It is one
Ansible playbook on localhost, `perform-updates.yml`, which resolves upstream
versions and rewrites the defaults files in place. A registry of tracked
tools, `vars/tools.yml`, drives it: each entry names the role, the task file
that queries the upstream, the values the tool consumes, the digests it needs
and the pins it writes. The playbook shares a directory of task files: one
fetch task file per kind of upstream, plus shared files for pre-flight
validation, checksum resolution, pin writing and failure reporting. Each tool
runs in isolation, so one upstream failure does not hide the others, and
every failure is classified as either an upstream problem or this
repository's own.

### Why the mechanism is larger than it looks

The tracked tools do not share one upstream shape. The registry is the
authoritative enumeration; it covers nineteen tools resolved through eight
distinct upstream kinds: GitHub releases, a GitHub commit SHA, a vendor
release manifest in JSON, a language-SDK REST API restricted to same-major
patches, a distribution index, a vendor desktop-release feed, a GitHub
release paired with a per-version digest manifest in object storage, and an
HTML page scraped with a regular expression, although the vendor also
serves a machine-readable XML repository manifest that the mechanism does
not read.

Checksums add a second axis. Some upstreams publish the digest in the same
manifest as the version. Others publish an aggregate checksums file per
release. Others publish nothing, and the digest must be computed from the
downloaded archive. Most tools need two digests, one per architecture, and
a version pin written without the digests that belong with it is worse
than no update at all.

The mechanism holds that pairing in three ways. Pre-flight validates the
whole registry before anything is queried. The order of writes is structural:
a tool's pins are written by one task file, and only after every digest they
reference has resolved. Two further rules are policed by static checks in CI:
no task edits a defaults file except through that task file, and every fact a
fetch task file sets carries the identity of the call that produced it.

The result is roughly 1,800 lines of YAML across the playbook, its registry
and its task files, an Ansible test harness of about 1,500 lines, and about
500 lines of Python in the two static checkers and their unit tests. A CI
workflow of its own runs the harness and the checkers and syntax-checks the
playbook. None of this provisions a machine; all of it exists to keep the
version and checksum pins of nineteen tools current.

Registering a newly pinned tool is one registry entry, plus a fetch task file
when no existing one serves its kind of upstream. The mechanism is young: its
design is still being reworked, and further redesign should be expected.

**Decision: which mechanism should keep this repository's role version
pins current, and how much of it should this project own?**

## Overriding Constraint: Literal Checksum Pins

**The repository must state the exact bytes it expects, as reviewable
literals in `defaults/main.yml`. No decision driver below may be traded
against this.**

This is the reason the pinning exists at all. Without it the sound choice
would be to install each tool's latest release unverified and accept
whatever upstream serves; the entire apparatus of versions, digests and
the update mechanism is the price of not doing that. An option that reduces
that apparatus by weakening the guarantee has not solved the problem, it
has abandoned it.

It is the same reasoning that already makes Principle IX SHA-pin
every GitHub Action. A literal digest defends against an upstream
artefact being replaced *after* it was pinned — a retagged release, a
force-pushed tag, a compromised account backfilling an old release. Under
literal pins that fails loudly on every converge. Under install-time
verification against an upstream checksums file it does not, because
whoever replaces the artefact replaces the checksums file in the same
motion; that shape is integrity in transit only.

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
   as bespoke local code does not address the concern that motivates this
   decision, however mature its scheduling and pull-request machinery.
2. **Cost of ownership.** One driver covering both the standing surface
   and the per-tool friction, because they are the same complaint: every
   line of the update mechanism is infrastructure for the infrastructure,
   and registering a newly pinned tool should be a small, declarative,
   single-site change.
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

- **A — Do nothing.** Keep `playbooks/update-versions/` as it stands: the
  registry-driven Ansible playbook described above.
- **B — Manual operator workaround.** Retire the automation; check
  upstreams by hand on a cadence.
- **C — Restructure the existing mechanism in place.** The tool registry,
  one resolver per upstream kind and the pin writer, in tested Python, with
  no new dependency. The registry and the per-kind task files already exist
  in Ansible; C is their Python form.
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
- Bad, because a tool whose upstream is of a new kind still needs a bespoke
  fetch task file written and tested here (driver 2).
- Bad, because it puts no maturity anywhere (driver 1); every future
  upstream change is this project's design problem.
- Bad, because the HTML scrape of the Android download page remains an
  accepted, unmitigated fragility, recorded as an open point in
  `docs/architecture/version-update-playbooks.md`.
- Neutral: adding a tool adds a registry entry, not code, so the code
  volume grows only with new kinds of upstream.

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

- Good, because the eight upstream kinds become eight tested Python
  resolver functions instead of eight Ansible task files, while the
  per-tool cost stays one registry entry (driver 2).
- Good, because Python unit tests replace the Ansible contract harness. The
  order of writes is structural in today's mechanism as well; how a Python
  writer would hold the two rules policed in CI is for the implementing
  branch to show.
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
  hyperlinks and would retire the Android HTML scraping recorded as an open
  point in `version-update-playbooks.md`; `format: json` with JSONata
  `transformTemplates`, which covers the vendor manifest, distribution
  index and desktop-feed shapes (the SDK API answers in comma-separated
  plain text, not JSON); and a release object may carry a
  `digest` field beside its `version`.
- Good, because for a tool whose upstream publishes the checksum in the
  same manifest as the version, that `digest` support makes the checksum
  update fully declarative — no script at all.
- Bad, and central: it does not satisfy driver 1. Renovate's maturity
  covers the plumbing, which is not where this repository breaks. Under
  this option the resolve layer remains bespoke local configuration —
  roughly one custom-manager regular expression per tracked tool plus one
  custom datasource per non-GitHub upstream kind — and the checksum layer
  remains a bespoke local script. The vendor-with-two-release-lines problem,
  the renamed-checksums-file problem and the missing-asset problem all stay
  exactly where they are, restated in a second configuration language.
- Bad, because the per-architecture checksum shape fights the tool's
  model. Renovate carries one digest per dependency, so a tool needing an
  amd64 and an arm64 digest must be declared as two dependencies, or be
  handled by a post-upgrade script. For the tools whose digests live in a
  per-release aggregate checksums file, or must be computed from the
  downloaded artefact, a datasource cannot supply them in one call, so the
  script is unavoidable for them.
- Bad, because `postUpgradeTasks` is gated by `allowedCommands`, a
  self-hosted global option supplied as a regular-expression allow-list
  via environment variable — a security-relevant configuration surface
  this project would own and must get right.
- Bad, because the batched-single-pull-request end state (C2) uses little
  of what makes Renovate worth adopting; grouping everything into one pull
  request discards the per-dependency lifecycle that is its main asset.
- Bad, because of two concrete integration costs: `renovatebot/github-action`
  must, like every action under ADR-007, be pinned to a commit SHA and added
  to the allow-list in `CONTRIBUTING.md`; and
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
  pin; `jq` against a JSON endpoint for the vendor manifest, distribution
  index and desktop feed; `regex` against the SDK
  API's comma-separated plain-text list; and `android_sdk`, which reads
  Google's own `repository2-1.xml` package index and therefore **retires
  the Android HTML scraping** rather than containing it. TD-009, the
  SHA-1-only digest, is unaffected: the package index publishes SHA-1 as
  well.
- Good, because the resolve layer becomes roughly one four-line TOML
  stanza per tool (driver 2), replacing the version-query part of the
  fetch task files; the manifest digests and the asset check those files
  also perform move to the pin writer.
- Good, because the failure classes that have bitten this repository have
  declarative answers in the idiom the tool exists for: the
  two-release-lines problem is an `include_regex`, the same-major SDK
  restriction is `include_regex` plus a `from_pattern`/`to_pattern`
  rewrite.
- Good, because what remains to own is small and sharply scoped: a Python
  tool taking a tool name and a resolved version, producing the
  per-architecture digests and rewriting the defaults file atomically.
  That tool is unit-testable without network access and carries the
  exactly-once pin-write guard and the
  write-nothing-unless-every-pin-of-a-file-validates rule that
  `write-pins.yml` implements today, and the asset-existence guard that
  `fetch-github-release.yml` implements today as `required_asset_regexes`
  (drivers 2 and 3).
- Good, because the overriding constraint is held structurally rather than
  policed (driver 3): version and digests are produced by one function and
  written in one transaction. Today's mechanism holds the order of writes
  structurally as well; what H changes is the two rules it polices in CI,
  whose replacement under H is for the implementing branch to show.
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
  action must be SHA-pinned and allow-listed under ADR-007.
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
structurally; today's mechanism holds the order of writes structurally as
well and polices two further rules in CI. The choice is therefore made on the
drivers, and driver 1 is where the options genuinely part.

The decision turns on driver 1. Renovate (F) is the more mature product by
a wide margin, and if the pain were scheduling, deduplication, rate
limiting or pull-request lifecycle, it would be the obvious answer. But
the failures this repository has actually absorbed are all in upstream
resolution, and Renovate does not own that layer for dependencies it has
no native datasource for — it would remain this project's code, merely
rewritten as custom managers and JSONata. Adopting Renovate would add a
configuration language without removing the class of problem that
motivates this decision, and C2 discards most of what would have justified the
cost anyway.

nvchecker is the only candidate that is mature *in the layer that breaks*.
The trade is deliberate and narrow: this project gives up owning upstream
querying, and keeps owning the checksum-and-write step, which is where its
genuinely project-specific rules live — the exactly-once pin match, the
asset guard, the all-or-nothing file write, the refusal to write a version
without its digests. Those rules were earned by real incidents and should
not be delegated.

Option C is the honest fallback. If the new dependency proves unwelcome,
C delivers drivers 2 and 3 as far as a Python form can, and only forfeits
driver 1 — and because H's pin writer is C's pin writer (C as defined here,
in Python; today's Ansible pin writer is not that writer), choosing H first
costs nothing if the resolve layer is later brought back in-house.

The resulting shape:

| Layer | Owner | Form |
| --- | --- | --- |
| Which version is current upstream | nvchecker | TOML stanza per tool |
| Which digests belong to that version | this project | tested Python |
| Writing version and digests together | this project | tested Python |
| Scheduling and opening the pull request | GitHub Actions | workflow |
| Reviewing and merging | maintainer | unchanged |

### Consequences

- `playbooks/update-versions/` is retired: the playbook, its registry and
  task files, the Ansible test harness and its CI workflow, and the two
  static checkers with their unit tests.
- The order of writes stays structural. The ban on file edits outside the
  pin writer and the call identity of fetch outputs are each policed by a
  CI check today, and the architecture document requires each contract to
  survive any simplification or removal of its script, at minimum as a CI
  step. The implementing branch must show how H holds both, structurally
  or by a replacement step.
- Constitution Principle II must be amended. Its current wiring
  requirement names a registry entry in
  `playbooks/update-versions/vars/tools.yml`, plus a fetch task file when
  no existing one serves the upstream. Under this
  decision, registering a tool is one nvchecker stanza and one registry
  entry for the pin writer. The registration rule, and the escape from
  version tracking it guards against, are unchanged; only the mechanism it
  names moves.
- `version-update-playbooks.md` is replaced. The checksum-verification
  pattern stands unchanged: the consumption contract it describes is
  untouched, and only the sentences naming `perform-updates.yml` as the
  resolver need retargeting.
- The Android HTML-scraping open point is closed rather than carried.
  TD-009, the SHA-1-only digest, stays open.
- `requirements.txt` gains nvchecker with its `jq` extra
  (`nvchecker[jq]`); CI gains a scheduled workflow whose
  actions, including a create-pull-request action, are SHA-pinned under
  ADR-007 and need allow-list entries in `CONTRIBUTING.md`.
- The failure-classification model — whether a failure is `upstream` or
  `configuration` — is preserved in the Python tool rather than ported
  literally. It does not become simpler for free: nvchecker reports a
  per-entry error without saying whether the stanza or the upstream is
  wrong — a mistyped repository fails like a deleted one, the blind spot
  today's classifier also has. Everything the pin writer raises is this
  repository's own.
- Offline behaviour is retained: both nvchecker and the pin writer run on
  the control node from the project virtual environment, so the maintainer
  can still run a sweep locally and read `git diff` before anything
  reaches CI.

### Mitigations for the negative consequences

- **New dependency, small maintainer team.** nvchecker is pinned to an
  exact version in `requirements.txt`, so an upstream regression cannot
  arrive unannounced; this is stricter than the file's other entries, which
  carry a version floor or no constraint at all. Its output
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
- **No stale-check gate.** Neither today's mechanism nor this one exits
  non-zero merely because pins are stale. If a hard gate is wanted, the pin
  writer's dry-run mode provides it as its own CI step; the scheduled
  workflow fails when the pin writer reports pins it could not resolve.

## Confirmation

The decision is confirmed in the implementing branch by:

- Unit tests for the pin writer covering: a renamed pin, a duplicated pin,
  a missing pin, a value containing a quote, backslash or newline, and the
  all-or-nothing guarantee that a file with one bad pin is left untouched.
- A test proving a version is never written without its digests.
- An end-to-end run against the real upstreams producing a diff
  equivalent to what `perform-updates.yml` produces for the same day.
- A second run immediately afterwards producing no changes (Principle I).
- The amended Principle II and the rewritten documents landing in the same
  branch as the code, so no document describes the replaced mechanism.

## More Information

- [`version-update-playbooks.md`](../version-update-playbooks.md) —
  the mechanism being replaced, including its failure-classification rules
  and the order of its writes.
- [checksum-verification pattern][pattern] — the consumption contract,
  unchanged by this decision.
- [ADR-007](007-single-tier-action-pinning.md) — the action-pinning
  policy that governs any workflow added here.
- nvchecker documentation: <https://nvchecker.readthedocs.io/>
- Renovate custom datasources:
  <https://docs.renovatebot.com/modules/datasource/custom/>
- Renovate `postUpgradeTasks` and the self-hosted-only `allowedCommands`:
  <https://docs.renovatebot.com/self-hosted-configuration/>
- updatecli: <https://www.updatecli.io/docs/core/configuration/>

### Why integrity is a constraint, not a driver

Supply-chain integrity is not ranked among the drivers, for two reasons. The
update mechanism does not exist for integrity: pinning exists for integrity
and reproducibility, pinning causes staleness, and the update mechanism pays
that cost back; the argument against installing `latest` argues for pinning,
which is settled. And a driver must discriminate between the options that
survive, which integrity does not: once the constraint eliminates Dependabot
and the Mend-hosted Renovate app, every remaining option satisfies it, and C
and H score identically on it because they share a pin writer. Integrity is
therefore the Overriding Constraint, and the driver list ranks only what
discriminates.

Two further choices follow. The standing surface and the per-tool
friction form one driver, cost of ownership, because they are one concern.
Reversibility is not a driver, because it belongs in the options' pros and
cons.

[pattern]: ../concepts/checksum-verification-pattern.md
