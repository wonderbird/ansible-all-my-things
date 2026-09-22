# Session hand-over: ADR-006, version update mechanism

You are picking up an unfinished architecture decision. This file is the
whole context; the session that produced it is gone. Read it start to
finish before doing anything.

Paste this to start:

> Read `PROMPT.md` in the repository root and follow it.

## Before any action

Read these two files first, in this order. The repository requires it of
every agent, for every task, including clarifying questions:

1. `AGENTS.md`
2. `.specify/memory/constitution.md`

Relevant beyond the usual: Principle II (roles that pin a version must
register in the version-update mechanism), Principle IV (YAGNI),
Principle IX (supply-chain rules for CI), Principle X (durable artefacts
must survive deletion of tracker IDs), Principle XI (no duplication),
Principle XII (fail loud), and the Documentation Standards rule "Write
Against Intent, Not Against Implementation Details".

Collaboration rules that shape this session: **English throughout**, ask
**one question at a time**, and use `bd` (beads) for task tracking, never
markdown to-do lists.

## The hard gate — read this before you verify anything

**Do not fact-check the ADR against the working tree until this branch has
been rebased onto `main`.** The tree you are standing in is stale, and it
is stale in a way that will actively mislead you: it looks plausible.

This branch, `025-adr-version-update-mechanism`, was cut from `85024a2`
(the merge of PR #121). It therefore does **not** contain the registry
refactor that landed on `024-clf3-per-tool-failure-isolation` and is being
merged as PR #122. Three different states of the same mechanism exist:

| File | This worktree | When the ADR was drafted | On `024` after the refactor |
| --- | --- | --- | --- |
| `playbooks/update-versions/perform-updates.yml` | 575 lines | 1388 lines | 109 lines |
| `playbooks/update-versions/query-versions.yml` | 475 lines | 475 lines | 88 lines |
| `playbooks/update-versions/vars/tools.yml` | absent | absent | 373 lines |
| `scripts/version-update-order/` | old apply-order checker, 724 lines with tests | same | `check-write-pins-bypass.py`, 180 lines with tests |

An agent that "verifies the ADR against the repo" from here will find the
old checker and the old playbooks, conclude the ADR is accurate, and be
wrong. That exact mistake already happened once in the previous session —
it is what stopped the work — so it is worth one deliberate gate.

**Step one is therefore: rebase, then re-derive.** Nothing else first.

## Why the work stopped

The ADR was drafted against `024` as it stood at the start of that
session. While it was being written, the maintainer and another agent were
implementing — in parallel, on `024` — the data-driven tool registry.
That work is **Option C of this very ADR**. It landed as commits
`7425f61`, `5f45aeb`, `e99cabb`, `31f501d`, `32263c9`, `fd42b5d` and
became PR #122.

So the ADR argues for its recommendation partly on premises that the
refactor has already satisfied. It is not wrong so much as **out of
date and mis-scoped**: it frames a decision about replacing the whole
mechanism, when what is actually left to decide is much narrower.

The maintainer's own account: both tracks were pursued deliberately,
because the alternatives — Renovate, and especially nvchecker — were not
known when the implementation started, and a working solution was wanted
regardless of how the ADR came out. The refactor also deleted more than
expected, `query-versions.yml` among it.

## Current state

- The ADR: `docs/architecture/decisions/006-version-update-mechanism.md`,
  528 lines, `Status: Proposed`, markdownlint clean, committed on this
  branch as `1134b16`.
- It is an **unreviewed draft**. An architect review was spawned,
  re-briefed once the stale facts were discovered, then stopped before it
  reported. Critic and deslop never ran.
- The review chain the maintainer asked for is still owed, and must run
  **after** the re-base, because reviewing stale facts wastes the review:
  **architect → fix to acceptance → critic → fix to acceptance → deslop**.
  Each reviewer iterates until it accepts.

## What the ADR currently says

Recommends **Option H**: adopt `nvchecker` for the resolve layer, plus a
small tested Python tool for checksum resolution and pin writing, driven
by a scheduled GitHub Actions workflow opening one batched pull request.

Structure: Context → Overriding Constraint → Further Constraints →
Decision Drivers → nine Considered Options with pros and cons → Decision
Outcome → Consequences → Mitigations → Confirmation → More Information.

The nine options: A do nothing, B manual, C restructure in place (**now
implemented — this is the new baseline, not an alternative**), D
Dependabot, E Renovate hosted, F Renovate self-hosted, G updatecli,
H nvchecker plus a Python pin writer, I buy a commercial product.

## Settled with the maintainer — do not re-ask

Nine questions were answered in the previous session. Treat these as
decided. Re-open one only if the merged PR #122 makes it factually
untenable, and say so explicitly when you do.

1. **Driver behind the review**: maintenance cost per new tool, total code
   volume, and — the maintainer's own addition, which became the top
   driver — *maturity*: the hand-rolled solution is alpha-stage and will
   need repeated redesign, whereas a mature tool may already have a design
   that handles current and future requirements.
2. **Literal checksum pins**: non-negotiable. This became the Overriding
   Constraint. The maintainer's argument for it, in their words: it is the
   reason for the whole effort, since otherwise one could just install
   each tool's `latest` without verifying.
3. **Owning fetch logic as a script**: acceptable, provided it shrinks a
   lot and is Python with tests.
4. **Workflow shape**: one batched, scheduled pull request containing all
   stale pins. Not one PR per tool.
5. **Where maturity is needed**: the *resolve* layer. Explicitly: if
   Renovate does not own that layer, adopting Renovate does not solve the
   problem. This is what selects nvchecker over Renovate and is the
   load-bearing driver of the whole document.
6. **Dependency envelope**: a new control-node dependency is acceptable.
7. **Integrity as constraint or driver**: both. It is a hard gate *and* it
   discriminates in one narrow sense (a guarantee held structurally beats
   one policed by a checker).
8. **Marginal cost vs total volume**: merged into a single driver, "cost
   of ownership" — the maintainer judged them one concern, not two.
9. **Reversibility as a driver**: rejected. It is an argument belonging in
   the options' pros and cons, not a driver.

### How the drivers were derived

Kept here because the ADR records the drivers but not their derivation,
and this file is the only place that trail exists.

The maintainer initially proposed ranking supply-chain integrity **first**,
reasoning that it is why the effort exists at all. That was pushed back
on, at their invitation, on two grounds:

- The update mechanism does not exist *for* integrity. Pinning exists for
  integrity and reproducibility; pinning causes staleness; the update
  mechanism pays that cost back. The `latest` counterfactual argues for
  pinning, which is settled and not on the table.
- A driver must discriminate between surviving options, and integrity does
  not: once the constraint eliminates Dependabot and hosted Renovate,
  every remaining option satisfies it, and C and H score identically
  because they share a pin writer. Ranking a gate above the factor that
  actually decided the case would misrepresent the reasoning.

The maintainer accepted this and chose the proposed resolution: promote
the constraint to an **Overriding Constraint** with its own section
carrying the `latest` argument as rationale, and keep the driver list as a
ranking of what genuinely discriminates.

**Final drivers, in priority order:**

1. Maturity must sit in the resolve layer.
2. Cost of ownership (standing surface and per-tool friction, as one).
3. Integrity guaranteed structurally, not policed.
4. Fit with the existing Ansible and CI architecture.

## What survives the merge, and what dies

Re-verify only the second list. Re-researching the first is waste.

### External findings — unaffected by PR #122, already verified

- **Literal digests vs install-time verification.** A literal digest
  detects an upstream artefact replaced *after* pinning (retagged release,
  force-pushed tag, compromised account backfilling a release). Verifying
  at install time against an upstream checksums file does not, because
  whoever replaces the artefact replaces the checksums file in the same
  motion. That is integrity in transit only.
- **Dependabot** cannot see arbitrary version literals in an Ansible
  role's `defaults/main.yml` — no custom-manager or custom-datasource
  extension point — and cannot write checksums under any configuration.
- **Renovate, Mend-hosted app**: does not execute `postUpgradeTasks` at
  all; `allowedCommands` is a self-hosted-only option. The few
  post-upgrade commands the hosted app does permit are deliberately
  undocumented and subject to change.
- **Renovate, self-hosted** (runnable as a GitHub Action, no server
  needed): `customDatasource` supports `format: html` (extracts versions
  from a page's hyperlinks), `format: json` with JSONata
  `transformTemplates`, and a release object may carry a `digest` field
  beside `version`. But it carries **one digest per dependency**, which
  fights per-architecture pins, and a per-release aggregate `checksums.txt`
  cannot be enumerated by a datasource in one call — so a
  `postUpgradeTasks` script is unavoidable for most tools here.
  `postUpgradeTasks` is gated by `allowedCommands`, a regex allow-list
  supplied by environment variable.
- **nvchecker**: mature (Arch-packaged, v2.21, second major version,
  decade old), TOML config, one stanza per tool. Covers every upstream
  kind in this repository with stock source plugins — `github` with
  `use_latest_release`; `git` with `use_commit`; `jq` against a JSON
  endpoint for the vendor manifest, SDK API, distribution index, desktop
  feed and object-storage manifest; and **`android_sdk`, which reads
  Google's own `repository2-1.xml`** and therefore retires the TD-009
  HTML-scraping debt rather than containing it. Handles versions **only**:
  no checksums, no file writing, no pull requests. Declarative answers
  exist for the known edge cases: `include_regex` for a repository
  publishing two release lines from one tag namespace, and `include_regex`
  plus `from_pattern`/`to_pattern` for the same-major Java constraint.
- **updatecli**: source/condition/target manifests, a `shell` target that
  handles checksums natively, opens its own pull requests — but a smaller,
  less widely deployed project, so it fails the maturity driver on its own
  terms.
- **Integration costs of any CI-side option**: an action holding
  `contents: write` is Tier A under ADR-002, so it needs a SHA pin and an
  entry in the allow-list in `CONTRIBUTING.md`; and pull requests opened
  with the default `GITHUB_TOKEN` do **not** trigger other workflows, so
  Molecule and the lint jobs would not run on update PRs without a GitHub
  App or a personal access token.

### Codebase claims — all invalidated by PR #122

Every one of these appears in the ADR and must be re-derived:

- All line counts: "roughly 2,550 lines of YAML", "about 720 lines of
  Python", `perform-updates.yml` at 1388 lines, `query-versions.yml` at
  475 lines.
- "Five edit sites across two playbooks" as the marginal cost of adding a
  tool. The registry's own header now reads "Adding a tool is one entry."
- Everything about the apply-order checker: that it exists, what it
  enforces, that roughly 720 lines of it would be deleted, and the
  argument that its ban "MUST survive any simplification" is satisfied
  structurally by the new design. It has already been replaced by
  `check-write-pins-bypass.py`.
- The description of the mechanism as "a pair of Ansible playbooks", and
  everything that follows from `query-versions.yml` existing — including
  FR-002's stale-check exit code, which the ADR discusses in the
  Mitigations section.
- The characterisation of checksum handling as per-tool. The registry
  already abstracts it into two declared kinds, `checksum_file` and
  `download`.
- The whole subsection "What triggered the reassessment", which is an
  argument from a code shape that no longer exists.
- Option C's status. It is no longer an alternative; it is the baseline.
  "Do nothing" (Option A) now means something entirely different, and must
  be rewritten accordingly.

Last known state of `024` before the merge, for orientation only —
re-derive rather than trusting these: 18 tools in the registry, 8 upstream
kinds, 11 tools routed through `fetch-github-release.yml`, checksum kinds
`checksum_file` (10 tools) and `download` (7), 1793 lines of YAML
excluding the test harness, 1164 lines of Ansible test harness, 180 lines
of Python.

## The likely new shape of the decision

Stated as a hypothesis for you to test, not a conclusion to adopt.

With the registry implemented, drivers 2 and 3 are largely paid out
already. **Driver 1 is untouched**: the resolve layer is still eight
bespoke `fetch-*.yml` files, the Android HTML scrape among them. If
maturity in the resolve layer is genuinely the top driver, nvchecker is
still the only candidate that answers it.

So the recommendation probably survives, but the decision is far narrower
than the document frames it: not "replace the mechanism", but **"replace
the eight fetch task files with nvchecker stanzas, keeping the registry,
the pin writer, the per-tool isolation and the failure reporting that now
exist"**. That is both cheaper and more attractive than the ADR describes.

Test that hypothesis against the merged code. Do not assume it.

## Your first steps

1. Read `AGENTS.md` and `.specify/memory/constitution.md`.
2. Rebase this branch onto `main` (or onto whatever now carries the merged
   PR #122). Resolve conflicts in favour of the merged code; the only file
   this branch owns is the ADR.
3. Re-derive the ground truth yourself from the merged tree — counts,
   file list, what replaced `query-versions.yml`, what the registry entry
   shape is, what `check-write-pins-bypass.py` enforces. **Read the PR
   #122 diff and log directly** (`git log`, `git diff`); do not ask the
   maintainer to summarise what the diff already shows.
4. Produce a short written list: every ADR claim that is now false, with
   its location and what it should say instead.
5. Then start asking the maintainer questions, **one at a time**, using
   `AskUserQuestion` rather than prose questions.

### Questions worth asking first

Ask what the diff cannot tell you. Suggested order:

1. Re-scope or rewrite? The previous session recommended re-scoping to the
   resolve layer only, keeping the registry as the baseline. The
   maintainer had not yet answered when work stopped.
2. `query-versions.yml` was deleted — what now carries FR-002, the
   stale-check that exits non-zero? Is that capability still wanted at all?
3. Does the registry change the maturity judgement? A registry the
   maintainer now owns and understands may feel less alpha than it did.
4. Are the eight upstream kinds unchanged, or did the refactor alter the
   fetch contract in ways that change how an nvchecker stanza would slot
   in?

## Follow-ups the previous session recommended but did not do

Deliberately left undone to keep the hand-over to a single file. Offer
them; do not do them unasked.

- **Move this file to `specs/025-adr-version-update-mechanism/`.** The
  repository's documentation strategy designates `specs/<feature>/` as the
  working-context tier, and a root-level `PROMPT.md` is off-strategy.
- **File a beads issue** as the durable anchor, since a worktree can be
  deleted and an issue cannot. Note the repository rule: run
  `bd export --all -o .beads/issues.jsonl` after bd mutations, bundled
  once per response, and never plain `bd export`. Also never run
  `bd list --all`.
- **Fold the driver derivation above into the ADR** (More Information), so
  that deleting this file loses nothing. Until that is done, this file is
  load-bearing.
- **Delete this file** once the ADR is accepted and the above are folded
  in. It is transient working context, not a durable artefact.
