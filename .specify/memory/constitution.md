<!--
Sync Impact Report — 1.5.1 → 1.6.0 (MINOR)
- Added Principle VIII: No Untracked Technical Debt
- Development Workflow: step 6 updated to require findings tracking
- Templates requiring updates:
  ✅ .specify/templates/plan-template.md — Constitution Check covers VIII automatically
  ✅ .specify/templates/tasks-template.md — no change needed
  ✅ .specify/templates/spec-template.md — no change needed
- No principles renamed or removed
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
MUST NOT contain implementation logic (tasks, handlers, templates) directly.
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
on a local Vagrant/Tart VM as described in `CONTRIBUTING.md`.

**Rationale**: Roles keep the codebase modular and reusable across different
target hosts without duplicating logic. Molecule container tests provide fast,
repeatable, local validation without requiring a full VM.

### III. Test Locally Before Cloud

Changes to roles or playbooks MUST be validated locally before being applied
to cloud-hosted machines (AWS EC2 or Hetzner).

For roles with a Molecule scenario, run `molecule test` from the role directory
as the primary validation step. This covers the full create → prepare →
converge → idempotence → verify → destroy lifecycle.

For roles without a Molecule scenario (those requiring a full VM), follow the
Vagrant-based procedure in `CONTRIBUTING.md`: isolate the role under test as
the only active role in `configure-linux-roles.yml` and run the playbook
against a local VM.

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

Technical debt MUST NOT be left untracked unless explicitly agreed with the
team. Such agreement MUST be recorded in the relevant issue before the source
task is closed.

**Rationale**: Untracked debt accumulates invisibly and degrades quality
without appearing in any backlog. Matching priority and blocking status ensures
findings are treated with the same urgency as the work that produced them,
preventing silent quality erosion.

## Technology Stack

- **Automation**: Ansible (playbooks, roles, inventory)
- **Role testing**: Molecule (molecule>=24.0.0 + molecule-plugins[podman])
  with the Podman driver for containerized role validation
- **Local test VMs**: Vagrant + Tart (macOS ARM64), Vagrant + Docker (Linux)
  for roles that cannot be containerized
- **Cloud targets**: AWS EC2 (Linux + Windows Server 2025), Hetzner Cloud (Linux)
- **Guest OS**: Ubuntu Linux (primary), Windows Server 2025 (secondary)
- **Configuration**: `ansible.cfg`, `group_vars`, `host_vars`, `inventories/`
- **Dependencies**: `requirements.yml` (Ansible Galaxy roles/collections),
  `requirements.txt` (Python packages including Molecule)
- **Scripting**: Bash (`configure.sh`, `scripts/`)

No additional runtime languages (Python services, Node apps, etc.) are
introduced without explicit justification and documentation.

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

## Agent Environment

The VM running the coding agent is destroyed regularly. Any state stored
outside the git repository — shell history, local memory files, environment
variables, tools installed outside `.venv` — does not survive between sessions.

All durable knowledge MUST be committed to git:

- Ansible patterns and prohibitions → this constitution
- Skill-owned rules (Molecule, commit format, Markdown formatting,
  documentation review) → `.claude/skills/<skill>/SKILL.md`
- Architecture decisions → `docs/architecture/decisions/`

Never rely on in-session memory or local files for knowledge that must
carry forward to the next agent session.

## Development Workflow

1. **Clarify first**: if instructions are unclear, ambiguous, or contradictory,
   ask clarifying questions before starting work. Resolve ambiguity one
   question at a time.
2. **Feature branch**: create a branch named `###-short-description` from `main`.
3. **Local test**: for roles with a Molecule scenario, run `molecule test` from
   the role directory. For roles without one, follow `CONTRIBUTING.md`.
4. **Commit**: use conventional commit format (Principle V); keep commits small
   and coherent.
5. **User review**: after every commit, request a user review and wait for
   approval before proceeding.
6. **Peer/self review**: verify idempotency, simplicity and traceability before
   merging. Track all findings as issues with the same priority as the source
   task, blocking the source task's cover issue (Principle VIII).
7. **Merge to main**: squash or rebase as appropriate; no merge commits unless
   history clarity demands it.
8. **Cloud apply**: run the playbook against cloud targets only after local
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

Complexity exceptions (violations of Principle IV) MUST be documented in the
`Complexity Tracking` table of the relevant plan.md before implementation
begins.

All agents working in this repository MUST read this constitution at the start
of any non-trivial task and verify that their plan complies with each principle.
Runtime guidance for AI agents is in `AGENTS.md`; `CLAUDE.md` only points to
it and to this constitution.

**Version**: 1.6.0 | **Ratified**: 2026-03-11 | **Last Amended**: 2026-05-15
