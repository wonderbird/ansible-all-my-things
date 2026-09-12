<!--
Sync Impact Report — 1.23.0 → 1.24.0 (MINOR)
- Development Workflow: new step 5, "Changelog" — every operator-visible
  change of a branch is recorded in `CHANGELOG.md` before review is
  requested, and a branch with no operator-visible change records nothing.
  Subsequent steps renumbered 6-9. The step delegates the format and the
  qualifies-for-an-entry decision to the `changelog-entry` skill, so the rule
  has one definition (Principle XI).
- Placement rationale: the changelog is a deliverable convention of the same
  class as Conventional Commits (Principle V), so it belongs in the ordered
  per-change ritual rather than in agent runtime guidance, which would bind
  agents but not a human opening a pull request by hand. The step sits before
  the review step so the reviewer sees the entry. MINOR: new guidance in an
  existing section, no principle removed or redefined.
- Templates checked for propagation:
  ✅ .specify/templates/plan-template.md — no changes required
  ✅ .specify/templates/tasks-template.md — no changes required
  ✅ .specify/templates/spec-template.md — no changes required
- AGENTS.md checked: propagation required — the Skill index table binds
  constitution-mandated skill invocations, so a `changelog-entry` row is
  added there in the same change. The Repository Remotes and Pull-Request
  Workflow section is deliberately left untouched: a third statement of the
  rule would duplicate it (Principle XI).
- CLAUDE.md checked: no propagation required
- .claude/skills/*/SKILL.md checked: `.claude/skills/changelog-entry/SKILL.md`
  already owns the format rules and the entry-qualification list; no other
  skill states when a changelog entry is due.
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

Every reusable capability MUST be implemented as a standalone Ansible role
inside the `roles/` directory. Playbooks MUST only orchestrate roles; they
MUST NOT contain implementation logic (tasks, handlers, templates) directly
(narrow carve-out: see the Maintenance-playbook exception below).
Roles MUST have a clear single responsibility.

Every role that can be exercised in a container MUST include a Molecule test
scenario in `molecule/default/` covering the full
create → prepare → converge → idempotence → verify → destroy lifecycle.

**The scenario file contract, required content of `prepare.yml`,
`converge.yml`, `verify.yml`, and `molecule.yml` are defined in the
`molecule-testing` skill, which is the authoritative source of truth. All
agents MUST invoke it when creating or modifying a role's Molecule scenario.**

Roles that cannot be exercised in a container (e.g., desktop environment
configuration, display managers, hardware drivers) MUST instead be validated
on a local Tart or Docker VM as described in
`docs/architecture/concepts/testing.md`.

Every role that pins a tool version in `defaults/main.yml` MUST also register
the tool in the version-update mechanism:

- A fetch task file under `playbooks/update-versions/tasks/` implementing the
  upstream version query.
- A read-current-pin task and an upstream-query task in
  `playbooks/update-versions/query-versions.yml`.
- An update task and matching fetch task include in
  `playbooks/update-versions/perform-updates.yml`.

A role that installs a versioned tool without this wiring silently escapes
version tracking. The mechanism structure is documented in
`docs/architecture/version-update-playbooks.md`.

A role whose tasks unconditionally require an artefact that only another
specific role provisions — such that the task would hard-fail for any
consumer that has not already applied that other role — MUST declare that
role in its own `meta/main.yml` `dependencies:` list, **in addition to**
(not instead of) explicit ordering in the consuming playbook and any
Molecule `converge.yml`. A role relationship that exists only for this
project's own orchestration convenience, without a hard runtime need, MUST
NOT be declared as a `meta/main.yml` dependency — express it via explicit
ordering only. The full decision test, worked examples, and caveats are in
`docs/architecture/concepts/role-dependency-declaration.md`, which is the
authoritative source of truth for this distinction.

**Maintenance-playbook exception**: Three directories of operator-invoked
procedural playbooks are exempt from the role-only rule above and MAY contain
inline task logic: `playbooks/update-versions/` (control-node tools that query
upstream release sources and rewrite local `defaults/main.yml` pins),
`playbooks/backup/`, and `playbooks/restore/` (data-movement tools that archive
and restore a user's files to and from a target host). These are operator-run
procedures, not host role configuration; any reuse they need is already served
by shared task files — `backup.yml` and `restore.yml` are each included by the
per-application playbooks in their directory. Wrapping such a procedure in a
role would add role lifecycle and Molecule scaffolding that buys nothing for a
control-plane operation, violating Principle IV (YAGNI). The exemption is a
**closed allowlist of these three directories**: any new maintenance playbook
MUST amend this principle to be added. A playbook not on the list — including
any that installs, templates, or otherwise configures a managed host — MUST
orchestrate roles only. `backup/` and `restore/` run against a managed host yet
remain exempt — allowlist membership, not the target host, is the gate.

**Rationale**: Roles keep the codebase modular and reusable across different
target hosts without duplicating logic. Molecule container tests provide fast,
repeatable, local validation without requiring a full VM. Version-update
registration prevents pinned tools from drifting silently behind upstream
releases. Declaring genuine hard dependencies in `meta/main.yml` makes a
role self-defending for any future consumer, while explicit ordering keeps
the full apply order human-auditable from one flat playbook file; Ansible's
role deduplication means requiring both costs nothing at runtime. Exempting a
closed set of operator-run maintenance procedures from the role wrapper avoids
lifecycle scaffolding that adds nothing to a control-plane operation, while the
closed allowlist keeps the carve-out from eroding the role-only rule for
managed-host configuration.

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

4. **GitHub Actions pinning.** All CI workflows MUST pin third-party actions
   following the two-tier policy:
   - **Tier A — SHA pin required** (`uses: owner/action@<sha> # vX.Y.Z`):
     any action in a job holding `packages: write`, `id-token: write`,
     `contents: write`, `security-events: write`, or cloud credentials; any
     action that signs, builds, pushes, or releases an artefact; container
     actions (`docker://...`); any action in a transitive publish chain
     (e.g. `upload-artifact` feeding a publish job). Default for anything
     not clearly Tier B.
   - **Tier B — floating major tag permitted** (`@vN`): only actions from
     the `actions/` or `github/` GitHub org that do NOT hold elevated
     permissions.

   Each repository instance MUST also enable the GitHub Actions allow-list;
   the canonical entry list and fork setup steps are in
   `CONTRIBUTING.md § Fork setup (one-time)`. When adding a new action to a
   workflow, the corresponding `owner/repo@*` entry MUST also be added to
   the list in `CONTRIBUTING.md` and to the allow-list in repository settings.
   See ADR-002 for full criteria, examples, and Dependabot interaction.

**Rationale**: Overly broad job permissions expose write credentials to
untrusted fork code and to steps that do not need them. Publishing before
testing allows broken artefacts to reach consumers silently. Provenance labels
and signatures make the build-to-publish chain auditable and enable consumers
to verify what they pull. SHA-pinning credential-bearing and artefact-handling
actions prevents supply-chain compromise via tag retargeting.

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

## Secret Management

All sensitive data (cloud credentials, API tokens, SSH keys, vault passwords)
MUST be encrypted with Ansible Vault. Plaintext secrets MUST NOT appear in
any committed file. Vault passwords are provided at runtime via the
`ANSIBLE_VAULT_PASSWORD_FILE` environment variable.

## Documentation Standards

**The documentation strategy, folder structure, project-specific tiers
(working-context specs, co-located role documentation), and migration policy
are defined in the `review-documentation` skill and its project-specific
extension `review-documentation-here`. All agents MUST invoke
`review-documentation-here` once at the close of a task, before invoking
`format-markdown`, so documentation is stable before formatting runs.**

All documentation MUST comply with Principle VI (Markdown Quality Standards).

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

This binds every agent that writes a durable artefact, not only those that load
a documentation skill.

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
   change of the branch in `CHANGELOG.md` using the `changelog-entry` skill,
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

**Version**: 1.24.0 | **Ratified**: 2026-03-11 | **Last Amended**: 2026-09-12
