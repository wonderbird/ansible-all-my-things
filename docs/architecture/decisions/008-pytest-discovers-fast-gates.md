# ADR-008: pytest Discovery Is the Fast-Gate List

Date: 2026-11-24
Status: Accepted
Deciders: Stefan (Product Owner)

## Decision

A plain `pytest` run from the repository root is the list of fast gates, the
checks every commit must pass. No file lists a gate by hand.

- `pytest.ini` makes a plain run collect every `test_*.py` module under
  `scripts/`. Acceptance tests (`acceptance_*.py`) stay out of it and run by
  name.
- The version-update harness playbooks become test cases: a test globs
  `playbooks/update-versions/tests/test-*.yml` and runs each harness with
  `ansible-playbook` as its own `subTest`; another test runs the syntax check
  of the version-update playbook. Each checker under `scripts/` is covered by
  a test that runs it on the real tree.
- `scripts/ci-local.sh` checks the tools it needs and runs `python3 -m pytest`.
- CI runs `scripts/ci-local.sh` in the job that already provisions the
  init_dev prerequisites, and names no test of its own. The separate
  version-update workflow is removed.

Because discovery replaces the hand-kept list, a gate is lost when discovery
misses it. Four guards make each such miss fail, locally and in CI:

| Guard | Fails when |
| --- | --- |
| Empty harness glob | `test-*.yml` matches no file; a loop over zero harnesses would pass. |
| Nothing collected | pytest collects no test; `ci-local.sh` does not mask exit code 5. |
| Orphan harness-directory file | A YAML file in the harness directory is neither a harness nor included by one, or a play sits in a subdirectory, where it never runs. |
| Uncollected test file | A Python file under `scripts/` defines a test but is not in the set a plain `pytest` run collects, and is not an acceptance test. |

The guards live in `scripts/gate-discovery/`, and each was seen failing on a
planted input before it was relied on (Principle XV).

## Context and Problem Statement

`scripts/ci-local.sh` is the pre-push convenience that runs the fast gates of
the pull-request workflows in one command, per commit (`git rebase --exec`)
and without waiting for a runner. Until this decision each gate was defined
twice: once in a workflow, which decided, and once by hand in the script.
When a gate was added to only one of them, the two drifted apart, and a commit
that passed the script could fail CI. At the time of the decision:

- the version-update workflow and `ci-local.sh` each kept their own list of
  harnesses and checkers;
- the init_dev unit tests ran in CI but not in `ci-local.sh`, and the tests in
  `scripts/backup/` ran nowhere;
- the Python tests were started in two ways, as `python3 test_x.py` and under
  pytest, although pytest already collected all of them.

The need: a commit that passes `ci-local.sh` passes the fast pull-request
workflows, for every gate, including gates added later, without anyone
remembering to edit two places. A gate that should run but does not must fail
something.

## Decision Drivers

1. **One gate list that nobody keeps.** Adding a gate must not require
   editing a second place (Principle XI).
2. **A lost gate fails loudly.** Every way a gate can drop out of the list is
   caught by a guard proven by failure (Principles XII and XV).
3. **CI can run what pytest collects.** Once pytest collects the init_dev
   unit tests, the CI job that runs `ci-local.sh` needs direnv, git and the
   other init_dev prerequisites.

## Considered Options

### Where the gate list lives

1. **Do nothing**: keep the two hand-kept lists and review both on every
   change.
2. **Manual workaround**: a checklist in the contributing guide that tells
   contributors to add each gate to both places.
3. **A hand-kept list in `ci-local.sh` that CI reads** (`ci-local.sh --list`
   feeds a workflow matrix, with gate groups for several workflows).
4. **pre-commit as the only list**: pytest and the harnesses as hooks at a
   manual stage; CI runs `pre-commit run --hook-stage manual`.
5. **A short Bash `ci-local.sh` without a list**: pytest, the syntax check, a
   glob loop over harnesses, pre-commit.
6. **pytest discovery is the list** (chosen).

No product solves this: the gates are repository-specific tests, and a CI
runner emulator such as `act` runs the workflow, not a list shared with it.

#### Pros and Cons

| Option | Pros | Cons |
| --- | --- | --- |
| 1 Do nothing | No work. | The drift that caused the problem continues; nothing fails when a list misses a gate. |
| 2 Checklist | Cheap. | Relies on memory, which already failed; nothing fails when a step is skipped. |
| 3 List in `ci-local.sh` | Meets the need; per-gate check names in CI. | Needs a guard for each way the list can go wrong and a failing case for each guard; a dispatch branch without a list entry stays unguarded. |
| 4 pre-commit only | One tool for linters and tests. | Stage semantics are subtle; listing harnesses as hooks rebuilds the list; running pytest from a hook collapses into option 6. |
| 5 Bash without a list | Smallest diff. | The Bash grows with every new kind of gate; harnesses are not test cases, so no guard covers them. |
| 6 pytest discovery | No list to keep; harnesses become test cases; pytest's own collection answers what runs. | Per-harness check names in CI are gone; discovery can miss a gate, so it needs guards. |

**Mitigation for option 6.** The four guards in the Decision make every known
way of missing a gate fail. The pytest log names each failing harness by its
`subTest`, which replaces the per-harness check names.

### Which CI job runs `ci-local.sh`

| Option | Pros | Cons |
| --- | --- | --- |
| **Run it in the init-dev job; remove the version-update workflow** (chosen) | The job already provisions direnv, git and the init_dev prerequisites; it has no `paths` filter, so the gates run on every change; one Python version, the system Python of the VMs. | Harnesses move to that Python version; every pull request runs the harnesses; a provisioning failure also hides the gate results. |
| Merge the workflows first, then switch to discovery | Ends in the same shape. | The merged workflow would run the hand-kept list for a while; the merge builds on the new `ci-local.sh`. |
| Run it in the version-update workflow and provision direnv there too | Keeps a newer Python for the harnesses. | Provisions the runner twice (Principle XI); its `paths` filter would skip the unit tests on other changes. |

**Mitigation.** If provisioning failures start hiding gate results, split
setup from the gates inside the same workflow.

### How the orphan guard knows that a harness uses a file

| Option | Pros | Cons |
| --- | --- | --- |
| **Static include graph** (chosen): follow `include_tasks` and `import_tasks` from every harness to a fixpoint; a templated target such as `tool-isolation-trigger-{{ _case.trigger }}.yml` matches only files whose filled-in part is a value of that same key in a harness; plays in subdirectories are reported | Detects "neither a harness nor used by one" as defined; finds a renamed harness, an unused helper and a trigger file that no case names; pure file reading, testable on temporary trees. | More code than the alternatives; an include form it does not follow reports its target until the guard learns the form. |
| Play shape only: any file under the harness directory that holds a play and is not a top-level `test-*.yml` fails | Very small; catches the loss that matters most, a harness that no longer runs. | Does not detect unused helpers or trigger files without a case. |
| Runtime include log from `ansible-playbook` output | Exact for whatever ran. | Depends on the text of Ansible's default callback; every harness must run before the guard can decide. |
| Naming convention (helpers start with a harness name) | Very small. | A proxy: an unused helper passes. |

**Mitigation.** The guard's docstring lists the include forms it does not
follow (`vars_files`, `include_vars`, `import_playbook`, roles, lookups and
plain path values). A file used only through one of them is reported, which is
the fail-loud direction: the guard learns the form, or the file moves.

### How the uncollected-test guard knows what pytest collects

| Option | Pros | Cons |
| --- | --- | --- |
| **Ask pytest** (chosen): run `pytest --collect-only` without a path argument and compare its files with an `ast` scan for test definitions | One source of truth for what pytest collects; catches a narrowed `testpaths`, an `--ignore` or a `norecursedirs` change. | A nested pytest run (well under a second); a base class imported from another module is not followed by the scan. |
| Re-implement pytest's rules from `pytest.ini` | No subprocess. | A second copy of pytest's rules that drifts when options change; misses ignores and `norecursedirs`. |

### Shape of the harness test

| Option | Pros | Cons |
| --- | --- | --- |
| **One `unittest.TestCase` with a `subTest` per harness** (chosen) | Follows the repository's Python conventions; pytest 9 reports each failing harness by name. | Needs pytest 9 for per-harness reports; pytest 8 stops reporting at the first failing harness, though it still fails. |
| `pytest.mark.parametrize` functions | One test ID per harness. | Departs from the conventions' `unittest.TestCase` rule. |
| Name the module `acceptance_*.py` | Follows the conventions' acceptance-test rule. | A plain run skips it, so the harnesses would leave every gate run. |

## Exception to the Python Conventions

The python-conventions skill puts a test that needs the real tools or minutes
of run time into `acceptance_*.py`, run by name. The harness test runs the
real `ansible-playbook` for about two minutes, yet a plain `pytest` collects
it. This exception is deliberate: the harnesses are per-commit gates that
plain `pytest` must discover, and they need no network, touch only temporary
directories and are deterministic, which is what the acceptance rule protects
against. The fast path for development is `pytest scripts/init_dev`, or
`pytest -k 'not VersionUpdateHarness'` to skip the harness test.

## Consequences

### Positive

- Adding a test or a harness adds a gate, locally and in CI, with no second
  edit.
- The init_dev and backup unit tests run before every push and in CI.
- A gate that discovery misses fails a test instead of disappearing.

### Negative

- A plain `pytest` takes minutes instead of seconds; the fast path above
  skips the harnesses.
- Every pull request runs the harnesses, and a provisioning failure in the
  shared job hides the gate results.
- `ci-local.sh` needs the repository's `.venv/bin` on `PATH`, direnv and git.
  A caller that only names an `ansible-playbook` through `ANSIBLE_PLAYBOOK` no
  longer suffices; the script fails with a fix hint.
- CI no longer shows one check per harness.

### Neutral

- The harnesses run on the system Python version of the VMs instead of a
  newer one.
- The `ANSIBLE_CONFIG` setting for each `ansible-playbook` child is proven by
  failure. Dropping `ANSIBLE_VAULT_PASSWORD` from the child environment is
  least privilege only: the harness configuration reads no vault, so dropping
  it changes no test result.

## Follow-ups

- Run the pre-commit hooks from `ci-local.sh`, give the CI workflow a name
  that matches its job, and add a test that fails when a workflow runs a test
  or lint tool other than through `ci-local.sh` (tracked in
  `ansible-all-my-things-6cgl.2`).
- Run zizmor, the workflow pinning scan, as a pinned pre-commit hook, so that
  `ci-local.sh` runs it too (tracked in `ansible-all-my-things-6cgl.3`).
- Measure the init_dev acceptance test's run time, network use and side
  effects, then make it a gate or record it as CI-only in the `ci-local.sh`
  header (tracked in `ansible-all-my-things-6cgl.4`).
