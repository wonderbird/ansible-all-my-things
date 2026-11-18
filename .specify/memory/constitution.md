<!--
Sync Impact Report — 2.4.0 → 2.5.0 (MINOR)
- Size: 5134 → 4900 words.
- Principle II (Role-First Organisation) keeps only its rules and their why.
  Host state lives in standalone roles; playbooks compose roles and MAY hold
  tasks, handlers or templates only for precondition assertions, procedures
  and user-environment transfer. The closed directory allowlist is replaced
  by these classes. A new procedure or user-environment playbook needs a plan
  whose architect review decides. New role rule: a configuration file in a
  user's home directory is created only if missing or gets only the role's
  keys merged in.
- Moved detail: the playbook classes and the fresh-host test to
  docs/architecture/concepts/playbook-classes.md (authoritative); role
  how-to (version-update wiring, meta dependencies, Molecule) stays in the
  ansible-role-creator and ansible-molecule-testing skills, which agents MUST
  invoke; docs/architecture/concepts/role-dependency-declaration.md stays
  authoritative for the dependency decision.
- Governance: new amendment step 5, a size review (rule plus why in the
  constitution, detail behind a pointer, word count before → after in this
  report); it also applies to AGENTS.md.
- MINOR: everything allowed before stays allowed; the VM-lifecycle
  playbooks, precondition assertions and bootstrap access, before covered
  only by per-plan exceptions, are now named; the home-directory rule and
  the size review are new guidance.
- Modified principles: II. Role-First Organisation. Modified sections:
  Governance.
- Added sections: none. Removed sections: none.
- Templates checked for propagation:
  ✅ .specify/templates/plan-template.md — no changes required
  ✅ .specify/templates/tasks-template.md — no changes required
  ✅ .specify/templates/spec-template.md — no changes required
  ✅ .specify/templates/checklist-template.md — no changes required
  ✅ .specify/templates/constitution-template.md — no changes required
  ✅ .specify/templates/agent-file-template.md — no changes required
- AGENTS.md and CLAUDE.md checked: no propagation required.
- Skills updated: ansible-role-creator (home-directory configuration rule),
  ansible-review-documentation (rule files stay lean).
- Runtime guidance updated: docs/architecture/solution-strategy.md,
  docs/architecture/concepts/playbook-classes.md (new).
- Technical debt: TD-002 updated (reboot-if-required.yml removed, shared
  setup task files added); TD-013 added for roles that overwrite a user's
  configuration files.
- Follow-up TODOs: none.
-->
# ansible-all-my-things Constitution

## Core Principles

### I. Idempotency (NON-NEGOTIABLE)

Every playbook, role and task MUST be idempotent: running the automation
more than once against the same target MUST produce the same system state
as running it once. Use Ansible built-in modules with idempotent semantics
(e.g., `copy`, `template`, `apt`, `user`) in preference to raw `command`
or `shell` tasks. When `command`/`shell` is unavoidable, add an explicit
`creates:` or `changed_when:` guard so the task is not re-executed
unnecessarily.

**`blockinfile` prohibition**: Never use `append_newline: true` or
`prepend_newline: true` on `ansible.builtin.blockinfile`. These parameters
cause the task to report `changed` on every run, silently breaking idempotency.
If blank lines around a block are required for readability, embed them
explicitly in the `block` content (e.g., `block: "\nexport FOO=bar\n"`).

**Rationale**: Infrastructure automation that is not idempotent causes
unpredictable drift and makes re-runs unsafe. Idempotency is the single
most important property of reliable Ansible code.

### II. Role-First Organisation

Everything a fresh managed host must get to be correct — packages, files,
services, accounts and settings, independent of which user works on it — MUST
be implemented as a standalone Ansible role in `roles/` with a single
responsibility. A role MUST:

- include a Molecule scenario covering the full create → prepare → converge →
  idempotence → verify → destroy lifecycle if it can run in a container, and
  otherwise be validated on a local Tart or Docker VM;
- register every tool version it pins in the version-update mechanism;
- declare a hard runtime dependency on another role in `meta/main.yml`, in
  addition to explicit ordering, and no other role relationship;
- create a configuration file in a user's home directory only if it is
  missing, or merge only the keys it requires.

Agents creating or changing a role MUST invoke the `ansible-role-creator`
skill, and the `ansible-molecule-testing` skill for its scenario; they hold the
details. `docs/architecture/concepts/role-dependency-declaration.md` is
authoritative for the dependency decision.

Playbooks compose roles. Besides roles, a playbook MAY contain tasks, handlers
or templates only for precondition assertions, procedures and
user-environment transfer, as defined in
`docs/architecture/concepts/playbook-classes.md`, which is authoritative. A new
procedure or user-environment playbook MUST be justified in a plan whose
architect review decides.

**Rationale**: Roles keep host configuration modular, idempotent and testable
in isolation. Procedures and user-environment transfer have no state a role
could converge, so a role wrapper would add scaffolding that tests nothing
(Principle IV).

### III. Test Locally Before Cloud

Changes to roles or playbooks MUST be validated locally before being applied
to cloud-hosted machines (AWS EC2 or Hetzner).

For roles with a Molecule scenario, run `molecule test` from the role directory
as the primary validation step. This covers the full create → prepare →
converge → idempotence → verify → destroy lifecycle.

For roles without a Molecule scenario (those requiring a full VM), follow the
procedure in `docs/architecture/concepts/testing.md`:
isolate the role under test as the only active role in the desktop play of
`configure-profile-roles.yml` and run `create-vm.yml` followed by
`configure-profile.yml` against the resulting local VM.

**Rationale**: Local validation is fast, free and reversible. Cloud
provisioning is slow and costs money; catching defects early avoids wasted
cycles.

### IV. Simplicity (YAGNI)

Automation MUST solve the current, confirmed need. Speculative abstraction,
parameterisation for hypothetical future targets, and premature generalisation
are prohibited. The minimum working solution is preferred over a flexible but
complex one. Complexity MUST be explicitly justified (see Governance).

**Rationale**: Over-engineered Ansible code is hard to reason about and
maintain for a single-person project. YAGNI keeps the repository actionable.

### V. Conventional Commits & Traceability

Every git commit MUST conform to the `commit` skill, which is the authoritative
source of truth for all commit formatting — including allowed prefixes, message
format, small-increment requirements, and co-authorship rules. All agents MUST
invoke it before creating any commit.

**Rationale**: Consistent commit messages make history machine-readable and
auditable; co-authorship credits are required by the collaboration agreement.

### VI. Markdown Quality Standards

All Markdown files in this repository (`.md`, `.mdc`) MUST be lint-clean
under the `format-markdown` skill's ruleset.

**The full linting ruleset, tool invocation, and installation instructions are
defined in the `format-markdown` skill, which is the authoritative source of
truth. All agents MUST invoke it once at the close of a task, after all
Markdown files are finalized — not after each individual edit.**

**Rationale**: Consistent formatting ensures readability across editors and
rendering tools, and makes diffs easier to review.

### VII. Structured Problem Solving

When an unexpected obstacle arises (test failure, tooling error, regression,
incorrect command output), agents MUST invoke the `fix-problem` skill, which
is the authoritative source of truth for the remediation protocol.

**Rationale**: Attempting to fix multiple interleaved issues simultaneously
introduces uncontrolled changes and makes root-cause analysis impossible.

### VIII. No Untracked Technical Debt

When implementing any task, all findings discovered during implementation —
code-review observations, follow-up improvements, and technical debt — MUST
be tracked as issues with the same priority as the source task. These issues
MUST block the source task's cover or parent issue before that issue is closed.

Policy or review follow-ups that impose compliance requirements on in-flight
work outside the originating epic tree MUST be wired as explicit blocking
dependencies on that in-flight work before it closes. Tracking a follow-up
only under its own parent epic — without connecting it to the constrained
feature — allows premature closure of work that is not yet compliant.

Technical debt MUST NOT be left untracked unless explicitly agreed with the
team. Such agreement MUST be recorded in the relevant issue before the source
task is closed.

**Rationale**: Untracked debt accumulates invisibly and degrades quality
without appearing in any backlog. Matching priority and blocking status ensures
findings are treated with the same urgency as the work that produced them,
preventing silent quality erosion. Cross-tree blocking makes compliance
requirements machine-readable in the issue tracker and prevents in-flight
features from being closed before a policy they must satisfy has been
enforced.

### IX. CI/CD Pipeline Security

CI/CD workflows that publish artefacts (container images, packages, signed
binaries) MUST follow four rules:

1. **Least-privilege job permissions.** Each job declares only the permissions
   it needs. Write-level credentials (`packages: write`, `id-token: write`,
   cloud push tokens) MUST be scoped to the job that performs the publish step
   — never to build, test, or lint jobs. Pull-request events from forks MUST
   NOT receive write-level permissions (gate publish steps with
   `if: github.event_name != 'pull_request'` or equivalent).

2. **Test-gated registry writes.** No artefact MUST reach a shared registry
   without first passing automated tests. The publish job MUST express a hard
   dependency on the test job (e.g. `needs: [build, test]` in GitHub Actions)
   so that a failing test blocks the push automatically.

3. **Artefact provenance.** Published container images MUST carry OCI
   provenance labels (`org.opencontainers.image.source`, `.revision`,
   `.created`) baked in at build time. Where the CI platform provides a
   keyless signing mechanism (e.g. cosign OIDC via Sigstore Fulcio), images
   MUST be signed after the push step.

4. **GitHub Actions pinning.** Every `uses:` reference in every CI workflow
   MUST be pinned as `uses: owner/action@<40-char-sha> # vX.Y.Z`. There is one
   tier: the publisher's identity does not matter and the permissions of the
   surrounding job do not matter. The comment MUST name the full semantic
   version, because it is what a reviewer reads to judge what an updated hash
   moved; a major-only `# vN` comment does not satisfy the rule.

   Dependabot pull requests for the `github-actions` ecosystem MUST NOT be
   auto-merged. A human approving each hash change is the control the pin
   buys, and without it a compromised upstream release lands unattended.

   Each repository instance MUST also enable the GitHub Actions allow-list;
   the canonical entry list and fork setup steps are in
   `CONTRIBUTING.md § Fork setup (one-time)`. When adding a new action to a
   workflow, the corresponding `owner/repo@*` entry MUST also be added to
   the list in `CONTRIBUTING.md` and to the allow-list in repository settings.
   See ADR-007 for the criteria, the Dependabot interaction, and the
   conditions the decision rests on.

**Rationale**: Overly broad job permissions expose write credentials to
untrusted fork code and to steps that do not need them. Publishing before
testing allows broken artefacts to reach consumers silently. Provenance labels
and signatures make the build-to-publish chain auditable and enable consumers
to verify what they pull. SHA-pinning every action prevents supply-chain
compromise via tag retargeting, and a single tier means any pin can be judged
from its own line without classifying the action or its job first.

### X. Self-Contained Durable Artefacts

Durable artefacts — any file in git meant to outlive a tracker ticket (code,
Markdown including ADRs and this constitution, YAML, feature specs) — MUST
pass the **strip test**: delete every ephemeral tracker ID (beads, Jira,
Linear, transient GitHub issue numbers, etc.); if any statement then loses
meaning, the substance was not inlined — inline it. A tracker ID MAY remain
only as a non-load-bearing pointer beside inlined substance (e.g. "(tracked in
`<id>`)"); a bare "see `<id>`" standing in for the substance is prohibited. Prefer
a durable anchor (a `specs/NNN` directory or an ADR) over a tracker ID where
one exists.

This constrains durable files only. PR descriptions, commit message bodies,
and `.omc/` scratch are transient and exempt.

**Rationale**: Ephemeral tracker IDs decay — a tracker can be migrated,
renumbered, archived, or replaced, leaving a dangling identifier whose context
must be reconstructed. A pointer deletable without information loss creates no
such dependency; one that replaces the substance does.

### XI. Avoid Duplication (DRY)

Logic, configuration, and documentation defined in one place MUST NOT be
restated or copied elsewhere. When reuse is required, extract a shared
abstraction — role, task file, template, variable — rather than duplicating
the implementation. References to the authoritative source are preferred over
inline repetition.

This applies equally to Ansible tasks, variable definitions, template content,
and documentation, including rules files and specifications.

**Rationale**: Duplication creates a maintenance burden — two definitions drift
apart and the authoritative source becomes ambiguous. A single source of truth
is easier to reason about, test, and update than distributed copies.

### XII. Fail Loud

Any task, playbook, or role that fetches, parses, computes, or depends on a
required value MUST fail with an explicit, actionable error when that value
cannot be obtained. Silent skips, empty-string fallbacks, and
`None`/undefined variable fallthrough are prohibited.

Concrete rules:

- Use `assert` or `fail` to validate required variables before use.
- `default(omit)` and `default('')` MUST NOT substitute for required values.
- `ignore_errors: true` MUST NOT suppress genuine failure conditions.
- `failed_when:` MUST NOT be added to a module task merely to improve its
  error message. On a module task, `failed_when:` **replaces** the module's
  own failure test rather than adding to it, so a guard written to describe a
  failure better instead reclassifies the real failure as `ok` and continues
  silently. To wrap a module failure in a clearer message, use
  `block`/`rescue` with an explicit `fail`, or leave the module's own error
  intact — it already reports the status and the offending value.
- Shell and command tasks that parse output MUST validate the result before
  proceeding.
- Failure messages MUST identify the source (variable name, URL, file path)
  to enable diagnosis without guesswork.

This principle is orthogonal to Principle I (Idempotency) but reinforces
predictability: a loud failure at the point of the gap is easier to diagnose
than a downstream symptom of undetected missing data.

**Rationale**: Silent failures produce systems that appear healthy but are
misconfigured. An explicit error at the point of failure is always faster to
diagnose and fix than tracing downstream symptoms of an undetected data gap.

### XIII. No Empty Artefacts

Directories tracked solely by a `.gitkeep` placeholder MUST be deleted (both
the file and the directory). Files whose only content is an SPDX license header
comment — optionally followed by a YAML `---` document-start marker — MUST be
deleted. Role scaffolding templates MUST NOT include such placeholder files;
files are created only when they carry real content.

**Rationale**: Empty placeholder files inflate the file tree with noise, mislead
readers into expecting content, and propagate silently through every role
scaffolded from the template. If a directory or file is genuinely needed, it is
added at that point with real content.

### XIV. SSH Host-Key Verification by Exposure

SSH connections to internet-exposed hosts (cloud servers such as Hetzner Cloud
or AWS) MUST verify the host key: `StrictHostKeyChecking=accept-new` against a
project-scoped, gitignored `known_hosts` file, with the key removed idempotently
on teardown. Connections whose network path never leaves the local machine
(loopback, host-only, or NAT-bridged targets such as Tart VMs and Docker
containers) MAY disable verification (`StrictHostKeyChecking=no`,
`UserKnownHostsFile=/dev/null`), since a man-in-the-middle there presupposes an
already-compromised host. A changed host key on a known address MUST fail
loudly (Principle XII), never be silently re-trusted. Full rationale, threat
model, and rejected alternatives are in ADR-003.

**Rationale**: Disabling host-key checks on a public network path exposes
automation runs — which may push secrets — to undetected man-in-the-middle
attacks. Matching verification to exposure protects the untrusted path without
adding host-key churn on local targets where the threat is negligible.

### XV. Guards Proven by Failure

A guard is anything whose result is taken as evidence that something is
correct: a test, a CI check, a linter, a detector, an assertion harness. A
guard counts as proven once it has been seen failing on a known-bad input,
either by the agent relying on it or in a recorded run (commit, pull request,
CI log). This includes a detector: zero findings count only after it has
caught a planted instance of what it looks for.

- A new or changed guard MUST be proven in both directions before it is
  merged: break its input and see the guard fail; restore the input and see
  it pass.
- An existing guard with no such record MUST be reported as unproven, not as
  passing.

**Rationale**: A guard that cannot fail looks exactly like a guard that finds
nothing wrong, so a green result alone does not show that the guard checks
anything. For example, a linter that writes SARIF output can exit 0 even when
it reports errors; a CI job built on it never goes red, whatever the code
contains (the guard's own Fail Loud, Principle XII). Seeing the guard fail
once on a known-bad input is the cheapest proof that its green result means
something.

## Technology Stack

- **Automation**: Ansible (playbooks, roles, inventory)
- **Role testing**: Molecule (molecule>=24.0.0 + molecule-plugins[podman])
  with the Podman driver for containerized role validation
- **Local test VMs**: Tart (macOS ARM64), Docker (Linux) for roles that
  cannot be containerized — provisioned via `create-vm.yml`
- **Cloud targets**: AWS EC2 (Linux + Windows Server 2025), Hetzner Cloud (Linux)
- **Guest OS**: Ubuntu Linux (primary), Windows Server 2025 (secondary)
- **Configuration**: `ansible.cfg`, `group_vars`, `host_vars`, `inventories/`
- **Dependencies**: `requirements.yml` (Ansible Galaxy roles/collections),
  `requirements.txt` (Python packages including Molecule)
- **Scripting**: Bash and Python (`scripts/`). Python is preferred for any
  script that carries tests or is large enough for its structure to matter,
  because it supports a natural unit-test layout and scales better as the
  script grows; Bash remains the right choice for short command sequences.
  A Python script MUST ship with a `test_`-prefixed sibling unless it is too
  trivial to test.

This covers tooling run on the control node. No additional runtime languages
(Python services, Node apps, etc.) are introduced on managed hosts without
explicit justification and documentation.

## Python Scripts

These rules bind every Python script under `scripts/` and its tests. A
script's own README MAY add rules specific to that script; it MUST NOT
restate these. Principle XII (Fail Loud) applies to scripts as it does to
tasks: a script MUST stop with an actionable error and never skip silently.
Principle XV (Guards Proven by Failure) applies to every check a script makes.

### Code

- **Standard library before custom code.** Where the standard library already
  solves a part of the problem, a script MUST use it instead of its own
  version.
- **One public entry point.** A module exposes only the functions its callers
  use. Every internal helper carries a `_` prefix.
- **Name by meaning.** A name MUST state what it holds, e.g.
  `for skill in skills`. Single letters are permitted only for the Python
  idioms `e` (caught exception), `k, v` (dict items), `_` (ignored value) and
  `i` (index).
- **One block per intent.** A function longer than five lines MUST separate
  each block that serves one intent by an empty line, under a short comment
  stating the intent. That comment names its block the way `name:` names an
  Ansible task; any further comment follows "Comments State What the Code
  Cannot".
- **Explicit over implicit.** Comparisons MUST be explicit, e.g.
  `name != ""` rather than relying on truthiness, and every `subprocess.run`
  MUST pass `check=`.
- **Formatted and linted by ruff.** Every script MUST pass `ruff format` and
  `ruff check` as configured in `ruff.toml`. The pre-commit hook defined in
  `.pre-commit-config.yaml` enforces both on each commit.

### Tests

- **Test our own logic.** Tests mock the standard library and external tools
  at their boundary. They MUST NOT test the behaviour of either.
- **Outcomes, not call order.** That a program runs all its parts MUST be
  proven through their outcomes, in an integration or acceptance test. A test
  that mocks the order of calls only cements the internal design.
- **A test body reads as its specification.** Mechanics live in helpers named
  by intent, e.g. `assert_skills_deployed()`. A helper that runs the function
  under test is named after it, e.g. `run_platform_check_with`.
- **Top-down order.** A test class lists `setUp`, then the tests, then the
  helpers they call. Module-level fixture builders follow the class.
- **Fixture builders take explicit inputs.** A builder takes its inputs as
  arguments and returns what it builds, so `setUp` shows the data flow.

**Rationale**: Scripts are read far more often than written, and often by
contributors who know another language better than Python. Uniform names,
blocks with stated intent, and explicit comparisons let such a reader follow
any script without knowing Python's idioms, and tests that read as
specifications state what a script promises before showing how it is
checked.

## Secret Management

All sensitive data (cloud credentials, API tokens, SSH keys, vault passwords)
MUST be encrypted with Ansible Vault. Plaintext secrets MUST NOT appear in
any committed file. Vault passwords are provided at runtime via the
`ANSIBLE_VAULT_PASSWORD_FILE` environment variable.

## Documentation Standards

**The documentation strategy, folder structure, project-specific tiers
(working-context specs, co-located role documentation), and migration policy
are defined in the `ansible-review-documentation` skill, which is
self-contained and authoritative for this repository. All agents MUST invoke
`ansible-review-documentation` once at the close of a task, before invoking
`format-markdown`, so documentation is stable before formatting runs.**

All documentation MUST comply with Principle VI (Markdown Quality Standards).

The rules below bind every agent that writes a durable artefact, not only those
that load a documentation skill.

### Write Against Intent, Not Against Implementation Details

Documentation and comments MUST describe intent, purpose, and the *kinds* of a
thing. They MUST NOT state counts, exhaustive enumerations of components, or
other implementation specifics (group names, file paths, variable names, host
targets) that a later change falsifies. An intent-based description stays
correct as long as the intention holds; an implementation-specific one becomes
wrong the moment the code changes, and nothing fails to announce it.

Where an exhaustive list genuinely helps a reader, point at the code that
already enumerates it — a directory, a task file, a `when:` clause — so the
list is derived at read time instead of copied. Where a document must state the
current value of an implementation detail, distinguish the intent from the
current value, so a reader knows which half to update.

Fragile, because it breaks when `hosts:` is renamed:

```text
The play explicitly targets `hosts: tart`
```

Robust, because it holds as long as the play targets local VMs:

```text
The play targets whatever local VMs are in the autogenerated inventory
```

### Comments State What the Code Cannot

A comment MUST carry information that the task name and the code do not: a
reason, a constraint, or a consequence of where the code sits. It MUST NOT
restate the task name, the module, or parameter values. The test is deletion:
if a reader of the task name and the code loses nothing when the comment is
deleted, it stays deleted.

A restating comment costs every reader time and drifts from the code it
repeats, because nothing fails when the two disagree.

Deleted, because it restates the task name:

```yaml
# Install curl
- name: Install curl
```

Kept, because the code shows it only by the task's position outside a gated
block:

```yaml
# Outside the install block: hosts that skip the install still need it.
- name: Install the runtime library the binary links against
```

### Document the Current State, Not Its History

Documentation describes the current status. Git is the record of history. A
durable document MUST NOT state what something used to be, what was removed,
or how a rule was previously enforced.

Exception: history is permitted where it explains a property of the current
document that is otherwise inexplicable — for example, a gap in a requirement
numbering sequence (`specs/007-version-update-playbooks/spec.md`). The test is
whether deleting the sentence leaves the reader unable to account for something
still present in the document.

This does not bind artefacts whose subject IS the history: `CHANGELOG.md` and
Architecture Decision Records, whose Context and Consequences sections record
the situation at decision time, and whose superseded entries are kept on
purpose.

Rules files are additionally subject to the stricter ban in Governance, which
admits no exception: they carry no version history, changelog, or amendment log
at all.

### Document the Variables a Task File Requires

A task file that reads a variable supplied by its caller MUST name that
variable in its header comment, under the heading `Required vars:`. The list
MUST be complete and MUST name only variables the file actually reads: a caller
that satisfies the header cannot fail on an undefined variable, and a header
entry never outlives its reader.

## Agent Environment

The VM running the coding agent is destroyed regularly. Any state stored
outside the git repository — shell history, local memory files, environment
variables, tools installed outside `.venv` — does not survive between sessions.

All durable knowledge MUST be committed to git:

- Ansible patterns and prohibitions → this constitution
- Skill-owned rules (Molecule, commit format, Markdown formatting,
  documentation review) → `.claude/skills/<skill>/SKILL.md`

Never rely on in-session memory or local files for knowledge that must
carry forward to the next agent session.

## Development Workflow

1. **Clarify first**: if instructions are unclear, ambiguous, or contradictory,
   ask clarifying questions before starting work. Resolve ambiguity one
   question at a time.
2. **Feature branch**: create a branch named `###-short-description` from `main`.
3. **Local test**: for roles with a Molecule scenario, run `molecule test` from
   the role directory. For roles without one, follow
   `docs/architecture/concepts/testing.md`.
4. **Commit**: use conventional commit format (Principle V); keep commits small
   and coherent.
5. **Changelog**: before requesting review, record every operator-visible
   change of the branch in `CHANGELOG.md` using the
   `ansible-changelog-entry` skill,
   which is the authoritative source of truth for the format and for which
   changes qualify. A branch whose changes no operator can observe records
   nothing.
6. **User review**: after every commit, request a user review and wait for
   approval before proceeding.

   **AI-orchestrated-loop exception**: For autonomous loops that run an
   automated architect/critic approval pass and a deslop regression re-verify
   pass before completion (e.g. ralph, autopilot, ultrawork) — not ad hoc
   sessions, which keep the per-commit review above — the human review
   checkpoint moves from after every commit to once per completed run: after
   architect/critic approval AND the deslop pass's post-cleanup regression
   re-verification have both passed, so the branch is in its final
   post-cleanup state. That review MUST happen on a GitHub PR opened against
   `origin` (never `upstream` — see "Repository Remotes and Pull-Request
   Workflow" in AGENTS.md for the `gh pr create` mechanics), not local/chat
   diff review.
7. **Peer/self review**: verify idempotency, simplicity and traceability before
   merging. Track all findings as issues with the same priority as the source
   task, blocking the source task's cover issue (Principle VIII).
8. **Merge to main**: rebase the feature branch onto `main` first (only if
   not yet pushed to the remote — rebasing a pushed branch rewrites shared
   history). Merge with `--no-ff` to produce a merge commit. Squash merges
   are prohibited.
9. **Cloud apply**: run the playbook against cloud targets only after local
   validation passes.

### Tracker-Export Commit Exception

A commit whose entire content is the beads tracker export MAY be committed
directly to `main`, without the **Feature branch**, **User review**, and
**Merge to main** steps above. The test is mechanical: the commit changes
`.beads/issues.jsonl` and no other file. A commit that touches any other file,
in addition or instead, is an ordinary change and every step above applies to
it in full.

**Rationale**: the file is generated state, not authored content. It is a
passive export rewritten wholesale by `bd export --all` after every tracker
mutation, and it is the primary durability path for issues and memories — see
"Beads: Data Safety and Workflow Rules" in `AGENTS.md`. A reviewer therefore
has nothing to review: its correctness is decided by the tracker state the
export was taken from, not by the diff. Routing it through a branch and a pull
request would spend one review cycle per tracker mutation while protecting
nothing. The single-file test keeps the exemption checkable without judgement,
so it cannot be stretched to cover a commit that also changes authored content.

## Governance

This constitution supersedes all informal conventions. Any amendment requires:

1. A clear description of the change and its rationale.
2. A version bump following semantic versioning:
   - **MAJOR**: removal or backward-incompatible redefinition of a principle.
   - **MINOR**: new principle or section, or material expansion of guidance.
   - **PATCH**: clarification, wording improvement, typo fix.
3. An update to this file with an incremented version, updated
   `Last Amended` date, and a new Sync Impact Report comment.
4. Propagation checks across `.specify/templates/`, `AGENTS.md`,
   `CLAUDE.md`, and any `.claude/skills/*/SKILL.md` named in this
   constitution.
5. A size review: each addition states a rule and its why. How-to, decision
   tests and examples go to a skill or to `docs/architecture/`, behind a
   pointer that names the authoritative source. The Sync Impact Report
   records the file's word count before → after, so growth is discussed in
   the pull request. The same review applies to every change of `AGENTS.md`.

Complexity exceptions (violations of any Core Principle) MUST be documented
in the `Complexity Tracking` table of the relevant plan.md before
implementation begins.

Rules files (`AGENTS.md`, `CLAUDE.md`, and skill `SKILL.md` files) MUST NOT
contain version history, changelogs, or amendment logs. These files document
current operational rules only. Exception: this constitution retains the
**latest** Sync Impact Report in the HTML comment block at the top of the file
for propagation audits. Prior reports MUST be removed on each amendment; git
history is the canonical record of all past reports.

This exemption applies only to the rules files named above. Feature
specifications under `specs/NNN-*/` are not exempt: they MUST stay consistent
with the current codebase (file paths, names, interfaces) for any feature they
describe, since they serve as the blueprint for recreating the system. Git
history, not an outdated spec, is the record of how an implementation evolved.

All agents working in this repository MUST read this constitution at the start
of any non-trivial task and verify that their plan complies with each principle.
Runtime guidance for AI agents is in `AGENTS.md`; `CLAUDE.md` only points to
it and to this constitution.

**Version**: 2.5.0 | **Ratified**: 2026-03-11 | **Last Amended**: 2026-11-18
