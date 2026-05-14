# ru3 Molecule CI Pipeline — Verification Fix

## Context

The `ru3-molecule-ci-pipeline` task was closed prematurely. Verification surfaced
two blockers:

1. `.github/workflows/molecule.yml` pins `actions/checkout@v6`, a version that
   does not exist. Current stable major is `v4`. The job will fail at the
   checkout step before any Molecule scenario runs.
2. No pull request exists for the branch targeting `main`, so the workflow has
   never been triggered. The implementation is fundamentally unverified — the
   "all roles tested in CI" success criterion has no evidence behind it.

Branch: `ru3-molecule-ci-pipeline` (1 commit ahead of `main`:
`156e323 ci: run Molecule tests for all roles on PR and push`).

## Work Objectives

- Restore the workflow to a runnable state with a maintained `actions/checkout`
  version.
- Trigger the workflow against `main` via a pull request so CI proves the
  pipeline works end-to-end against every role.
- Capture the green run as the verification artifact that should have closed
  the original task.

## Guardrails

**Must Have**
- Workflow uses a published, maintained `actions/checkout` version.
- Workflow file remains otherwise unchanged in scope — no refactor of triggers,
  runner, or steps as part of this fix.
- A PR exists against `main` and its `Molecule Tests` check completes
  successfully before the task is re-closed.

**Must NOT Have**
- No changes to `scripts/test-molecule-all.sh`, role code, or scenario configs
  in this plan.
- No version bumps for `setup-python`, Ansible, Molecule, or Python deps as
  part of this fix.
- No squash/rebase of the existing `156e323` commit unless required to resolve
  conflicts with `main`.

## Task Flow

```
fix checkout@v4 -> commit -> push -> open PR -> wait for CI -> verify green -> close task
```

## Detailed TODOs

### 1. Patch `actions/checkout` version

- Edit `.github/workflows/molecule.yml` line 19: `actions/checkout@v6` ->
  `actions/checkout@v4`.
- Acceptance: `grep -n "actions/checkout" .github/workflows/molecule.yml`
  returns exactly one match pinned to `@v4`.

### 2. Commit and push the fix

- Stage only `.github/workflows/molecule.yml`.
- Commit with a focused message, e.g.
  `ci: pin actions/checkout to v4 in molecule workflow`.
- Push `ru3-molecule-ci-pipeline` to `origin`.
- Acceptance: `git log origin/ru3-molecule-ci-pipeline -1` shows the new commit
  and `git status` is clean.

### 3. Open the pull request against `main`

- Use `gh pr create` with title `ci: run Molecule tests for all roles on PR
  and push` and a body that links the original task and explains the v6 -> v4
  correction.
- Base: `main`. Head: `ru3-molecule-ci-pipeline`.
- Acceptance: `gh pr list --head ru3-molecule-ci-pipeline` returns one open PR
  targeting `main`.

### 4. Verify CI run is green

- Watch the PR check with `gh pr checks <pr-number> --watch` (or poll
  `gh run list --branch ru3-molecule-ci-pipeline`).
- If `Run Molecule tests` fails, treat it as a separate investigation:
  capture the failing role/scenario, open follow-up issues, and do not merge.
- Acceptance: `Molecule Tests / Run Molecule tests` check is `success` on the
  PR head commit.

### 5. Re-close the original ru3 task with evidence

- Update the beads/task tracker entry for `ru3` to reference the green CI run
  URL and the PR.
- Acceptance: Task entry contains the PR URL and the successful workflow run
  URL as the verification artifact.

## Success Criteria

- `.github/workflows/molecule.yml` references `actions/checkout@v4`.
- An open PR for `ru3-molecule-ci-pipeline` -> `main` exists.
- The `Molecule Tests` workflow has at least one `success` run on the PR.
- `ru3` task is closed with links to the PR and the green workflow run.

## RALPLAN-DR Summary

### Principles

1. **Verify before claiming completion.** A task that never ran its own CI is
   not done.
2. **Smallest correct change.** Fix the single broken pin; do not bundle
   unrelated workflow changes.
3. **Use maintained, published versions of third-party actions.** Pin to a
   real major.
4. **Make verification artifacts durable.** A PR + workflow run URL is the
   evidence the next reader needs.
5. **One concern per PR.** Keep the CI fix isolated from role logic changes.

### Decision Drivers

1. **Correctness of the action reference** — must resolve to a real, supported
   release.
2. **Speed of unblocking the ru3 task** — minutes, not days; CI just needs to
   run.
3. **Stability of pin choice** — should not require another bump in the very
   near term.

### Viable Options

**Option A — Pin to `actions/checkout@v4` (floating major)**
- Pros: Current stable major, broadly used, receives non-breaking updates
  automatically, matches the convention already used by `setup-python@v5` in
  the same file.
- Cons: Floating tag means future minor/patch releases land without an explicit
  bump (mitigated by GitHub's tag stability policy for major refs).

**Option B — Pin to a specific `actions/checkout@v4.x.y` SHA**
- Pros: Maximum reproducibility; immune to silent updates within the major;
  aligns with supply-chain hardening guidance.
- Cons: Diverges from the rest of the workflow's tagging style; adds
  maintenance burden (Dependabot or manual bumps) for a project that is not
  currently doing SHA pinning anywhere else; out of scope for a "fix the
  broken pin" task.

**Option C — Drop the checkout step / use a different action**
- Pros: None meaningful here.
- Cons: Molecule tests need the repo on disk; replacing `actions/checkout` is
  a bigger change than the bug warrants. Invalidated.

### Recommendation

**Option A: pin to `actions/checkout@v4`.** It is the minimal, conventional
fix, matches the existing pinning style in the same file (`setup-python@v5`),
and unblocks verification immediately. Supply-chain hardening via SHA pinning
(Option B) is a worthwhile follow-up but should be a project-wide decision,
not a side effect of this task.

### ADR

- **Decision:** Pin `actions/checkout` to `@v4` in `molecule.yml`; open a PR
  to trigger and verify the workflow.
- **Drivers:** Workflow currently broken at startup; ru3 success criterion
  requires green CI evidence; smallest-change preference.
- **Alternatives considered:** SHA pinning (deferred — project-wide concern);
  removing the action (not viable).
- **Why chosen:** Matches existing tagging convention, resolves to a
  maintained release, fastest path to verifiable green CI.
- **Consequences:** Floating major means future v4.x updates land silently.
  Acceptable given no other actions in the repo are SHA-pinned.
- **Follow-ups:** Consider a separate task for repo-wide SHA pinning of all
  third-party actions if supply-chain hardening becomes a priority.
