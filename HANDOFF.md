# Handoff: y7f3.1 selective Molecule CI

Status as of 2026-11-26, end of day.

## Where things stand

- **Epic:** `ansible-all-my-things-y7f3` (Molecule testing infra improvements).
- **Child in work:** `ansible-all-my-things-y7f3.1` (Molecule CI runs only when
  code its scenarios test has changed). Status `in_progress`. The user closes
  it, not an agent. Blocked by findings gate `ansible-all-my-things-lnvd` (human
  review of PR 177). The pin update `ansible-all-my-things-y7f3.4` is closed.
- **Branch:** `y7f3-selective-molecule-ci`, pushed to `origin`, clean apart
  from the untracked `.claude/skills/caveman` (created by the skill manager;
  keep it out of commits) and this file.
- **Pull request:** <https://github.com/wonderbird/ansible-all-my-things/pull/177>

Commits on top of `main`:

| Commit | Content |
| --- | --- |
| `ce9f3d5` | Selector, runner modes, workflow, docs, changelog |
| `0a9b5ad` | Review round 1 fixes: `ansible.cfg`, push to `main`, imports, `edited`, gate job |
| `0f3bfcf` | Review round 2 fixes: reachable-graph walk, playbook-local roles, `vars_files`, empty `--roles` guard |
| `400cbd9` | Review round 3 fixes: scenario-only edits narrowed, merge keys rejected, parser tests |
| `74d1d30` | Beads export: revised acceptance criterion, follow-ups y7f3.2 and y7f3.3 |
| `c85c81d` | Pin update (y7f3.4): beads_viewer, claude_code, dolt_sql_server, github_cli 2.105.0 to 2.106.0, specify_cli, uv |
| `616c7ba` | Beads export: y7f3.4 blocking y7f3.1, follow-up y7f3.5 |

## What the change does

- `scripts/select_molecule_roles.py` and `scripts/molecule_references.py`
  pick the scenarios a diff affects. A role runtime change selects the role
  and every scenario that uses it, transitively. A change under `molecule/`
  selects the owning scenario plus scenarios that reach the changed file. A
  shared input (workflow, runner, requirements, `ansible.cfg`) selects all 28.
- Unresolvable reachable references and YAML merge keys fail selection loudly.
  Over-selection is preferred to a false skip.
- `scripts/test-molecule-all.sh` gains list and `--roles` modes and stays the
  only discovery mechanism.
- `.github/workflows/molecule.yml`: job `Select Molecule roles`, then
  `Run Molecule tests` on the selection, then the always-evaluated
  `Molecule CI gate`. PR runs cancel superseded ones. Pushes to `main` select
  on `before..after`. `workflow_dispatch` and a weekly schedule run everything.

## Review

Architect review: 4 rounds, final verdict **APPROVED**. Round 4 left one
MINOR, filed as y7f3.3.

User decision during round 2: post-merge duplicate runs are accepted.
Requirement 3 and its acceptance criterion in y7f3.1 were rewritten.

## CI status of PR #177 (VERIFIED, run 45863754713 on `616c7ba`)

All checks are green. Molecule: 28 passed, 0 failed; `Molecule CI gate` pass.
The selection picked all 28 roles, as expected, because the PR changes the
workflow itself.

The previous run (45813604006) failed only `github_cli`, because the pinned
`gh=2.105.0` had left the GitHub CLI apt repository. The pin update in
`c85c81d` fixed it. The user chose to update pins on this branch; had CI stayed
red, the plan was to revert `c85c81d` and move the update to a separate branch.

## Open items

1. **Fix finding `ansible-all-my-things-lnvd.1`** (Molecule CI runs the
   full suite or nothing, decided by a skip list, not per-role selection), P1.
   This reworks the PR: rewrite y7f3.1's Goal, requirement 2 and acceptance
   criteria, replace the per-role selector with a skip-list check, remove
   `scripts/molecule_references.py`, the role graph and the runner's `--roles`
   mode, close y7f3.3 as obsolete. Then re-review and re-run CI.
2. **Recorded skip run** (acceptance criterion of y7f3.1, Principle XV). This
   PR's own run cannot skip. After merge, open a docs-only PR and record its
   run URL in y7f3.1. A role-only PR gives the recorded selection run.
3. **Human review** `ansible-all-my-things-lnvd.2`: verify the fixes, then
   the user closes gate `lnvd`. Merge PR #177 afterwards.
4. **Required check.** If `main` gets branch protection, require
   `Molecule CI gate`, not `Run Molecule tests`: GitHub counts a skipped job
   as passing.
5. **Remove `HANDOFF.md`** from the branch before merging PR #177. It is a
   session handoff, not project documentation.
6. **Close y7f3.1** once the PR is merged and item 2 is done (user action).

## Follow-up issues (children of y7f3)

- `ansible-all-my-things-y7f3.2` (skip the post-merge Molecule run when the
  PR run already tested the same tree), P3.
- `ansible-all-my-things-y7f3.3` (track `copy.src` assets that a shared
  scenario playbook pulls from another role), P4. Obsolete once lnvd.1 is
  fixed.
- `ansible-all-my-things-y7f3.5` (`github_cli` pin breaks whenever gh drops
  the pinned version from its apt repository), P3.

## Notes for the next session

- On a fresh machine: clone, `git checkout y7f3-selective-molecule-ci`,
  then run `python3 -m scripts.init_dev` (initializes beads from the tracked
  `.beads/issues.jsonl`; see AGENTS.md). Check `bd show
  ansible-all-my-things-lnvd` to see the open findings.
- Skills under `.agents/skills/` are symlinks into `~/.skill-manager/skills`.
  The oh-my-openagent skill loader loads one only when it can also reach it
  from a user skill root (`~/.agents/skills`, `~/.claude/skills`,
  `~/.config/opencode/skills`) or `skills.sources` in
  `~/.config/opencode/oh-my-openagent.jsonc`. The `external_directory`
  permission does not affect it. This is fixed now.
- Subagent sessions can disappear between turns ("Task not found for
  session"). Brief any new subagent from the branch history and this file.
- Verification commands: `pytest -q scripts` (116 passed),
  `gh pr checks 177 --repo wonderbird/ansible-all-my-things`.
