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

**Rationale**: Infrastructure automation that is not idempotent causes
unpredictable drift and makes re-runs unsafe. Idempotency is the single
most important property of reliable Ansible code.

### II. Role-First Organisation

Every reusable capability MUST be implemented as a standalone Ansible role
inside the `roles/` directory. Playbooks MUST only orchestrate roles; they
MUST NOT contain implementation logic (tasks, handlers, templates) directly.
Roles MUST have a clear single responsibility and MUST be independently
testable on a local Vagrant/Tart VM.

**Rationale**: Roles keep the codebase modular and reusable across different
target hosts without duplicating logic.

### III. Test Locally Before Cloud

Changes to roles or playbooks MUST be validated on a local VM (Vagrant +
Tart or Docker) before being applied to cloud-hosted machines (AWS EC2 or
Hetzner). The test procedure defined in `CONTRIBUTING.md` MUST be followed:
isolated role testing with the role under test as the only active role in
`configure-linux-roles.yml`.

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

Every git commit MUST use one of the following conventional commit prefixes:
`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `ci:`, `build(deps):`.
If the correct prefix is unclear, ask the user before committing.

Commit messages MUST represent a small, coherent, working increment.

**Commit format, headline conventions, co-authorship requirements, and the
AI agent co-author table are defined in
`.cursor/rules/general/330-git-usage.mdc`, which is the authoritative source
of truth for all commit formatting. All agents MUST read and follow that file
before creating any commit.**

**Rationale**: Consistent commit messages make history machine-readable and
auditable; co-authorship credits are required by the collaboration agreement.

### VI. Markdown Quality Standards

All Markdown files in this repository (`.md`, `.mdc`) MUST comply with:

- Section headers MUST use ATX heading syntax (`#`, `##`, `###`, …). Bold
  text (`**text**`) MUST NOT be used as a substitute for headings.
- Every list (ordered or unordered) MUST be preceded and followed by a blank
  line.
- No trailing whitespace on any line.
- No multiple consecutive blank lines — use exactly one blank line to
  separate sections.
- Every file MUST end with exactly one newline character.
- Heading hierarchy MUST be consistent throughout the file (H1 → H2 → H3;
  no skipped levels).

**The full linting ruleset, tool invocation, and installation instructions are
defined in `.cursor/rules/general/400-markdown-formatting.mdc`, which is the
authoritative source of truth. All agents MUST read and follow that file
whenever creating or modifying a Markdown file.**

**Rationale**: Consistent formatting ensures readability across editors and
rendering tools, and makes diffs easier to review.

### VII. Structured Problem Solving

When an unexpected obstacle arises (test failure, tooling error, regression,
incorrect command output), the remediation protocol MUST be followed:

1. **Stop** the current primary task immediately.
2. **Document** the obstacle (in chat or a spec artifact) before attempting
   a fix.
3. **One obstacle at a time** — select only the first obstacle; ignore
   others until it is fully resolved. Solving multiple issues simultaneously
   is forbidden.
4. **Hypothesize** — form a specific, testable hypothesis for the cause.
5. **Test the hypothesis** — make the minimal change needed to confirm or
   refute it (a minimal failing test for code bugs; a minimal command
   execution for tooling bugs).
6. **Fix** — implement the minimal fix; verify no regressions.
7. **Commit** — use a commit message that names the specific obstacle
   resolved.
8. **Repeat** for remaining obstacles, or resume the primary task when all
   are cleared.

**Rationale**: Attempting to fix multiple interleaved issues simultaneously
introduces uncontrolled changes and makes root-cause analysis impossible.

## Technology Stack

- **Automation**: Ansible (playbooks, roles, inventory)
- **Local test VMs**: Vagrant + Tart (macOS ARM64), Vagrant + Docker (Linux)
- **Cloud targets**: AWS EC2 (Linux + Windows Server 2025), Hetzner Cloud (Linux)
- **Guest OS**: Ubuntu Linux (primary), Windows Server 2025 (secondary)
- **Configuration**: `ansible.cfg`, `group_vars`, `host_vars`, `inventories/`
- **Dependencies**: `requirements.yml` (Ansible Galaxy roles/collections),
  `requirements.txt` (Python packages)
- **Scripting**: Bash (`configure.sh`, `scripts/`)

No additional runtime languages (Python services, Node apps, etc.) are
introduced without explicit justification and documentation.

**Secret Management**: All sensitive data (cloud credentials, API tokens, SSH
keys, vault passwords) MUST be encrypted with Ansible Vault. Plaintext
secrets MUST NOT appear in any committed file. Vault passwords are provided
at runtime via the `ANSIBLE_VAULT_PASSWORD_FILE` environment variable.

## Documentation Standards

**The documentation strategy, folder structure, and migration policy are
defined in `.cursor/rules/general/600-documentation-strategy.mdc`, which is
the authoritative source of truth. All agents MUST read and follow that file
when creating or updating documentation.**

This project extends the base strategy with one additional documentation tier:

- `specs/<feature>/` — Working context per feature: spec, plan, research,
  and tasks (managed by spec-kit). Promoted to `docs/` when stable and
  feature-agnostic.

Technology decisions, platform constraints, and the top-level decomposition
strategy are documented in `docs/architecture/solution-strategy.md`
(arc42 Section 4). Detailed Architecture Decision Records are kept in
`docs/architecture/decisions/`. These are the canonical locations for
architectural decisions; they MUST NOT be recorded in `CLAUDE.md` or
agent-specific context files.

**Migration policy**: content moves from `specs/` to `docs/` when it becomes
stable, reusable across features, and no longer tied to a single increment.

All documentation MUST comply with Principle VI (Markdown Quality Standards).

## Development Workflow

1. **Clarify first**: if instructions are unclear, ambiguous, or contradictory,
   ask clarifying questions before starting work. Resolve ambiguity one
   question at a time.
2. **Feature branch**: create a branch named `###-short-description` from `main`.
3. **Local test**: follow `CONTRIBUTING.md` — isolate the new/changed role and
   run the playbook against a local VM.
4. **Commit**: use conventional commit format (Principle V); keep commits small
   and coherent.
5. **User review**: after every commit, request a user review and wait for
   approval before proceeding.
6. **Peer/self review**: verify idempotency, simplicity and traceability before
   merging.
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
4. Propagation checks across `.specify/templates/` and referenced docs.

Complexity exceptions (violations of Principle IV) MUST be documented in the
`Complexity Tracking` table of the relevant plan.md before implementation
begins.

All agents working in this repository MUST read this constitution at the start
of any non-trivial task and verify that their plan complies with each principle.
Runtime guidance for AI agents is in `CLAUDE.md` and `.cursor/rules/`.

<!-- Sync Impact Report 1.1.1 (2026-03-26)
  Principle VI: Added delegation pointer to
  `.cursor/rules/general/400-markdown-formatting.mdc` as the authoritative
  source for the full linting ruleset, tool invocation, and installation
  instructions. Agents must now read that file whenever creating or modifying
  a Markdown file. The inline semantic rules in Principle VI are retained as
  a concise summary; the rule file is definitive.
  Propagation: CLAUDE.md updated to reference 400-markdown-formatting.mdc
  for markdown formatting guidance.
-->
<!-- Sync Impact Report 1.1.0 (2026-03-25)
  Principle V: Removed redundant co-authorship table, headline conventions,
  and body-rule details. `.cursor/rules/general/330-git-usage.mdc` is now
  the authoritative source for all commit formatting; the constitution retains
  only the prefix list and the high-level coherence requirement.
  Documentation Standards: Added pointer to
  `.cursor/rules/general/600-documentation-strategy.mdc` as authoritative
  source. Named `docs/architecture/solution-strategy.md` (arc42 Section 4)
  and `docs/architecture/decisions/` as canonical locations for architectural
  decisions; prohibited recording these in CLAUDE.md or agent context files.
  Re-added migration policy. Retained project-specific `specs/<feature>/`
  tier extension.
  Propagation: `.specify/templates/agent-file-template.md` updated — "Active
  Technologies" section now points agents to `docs/architecture/solution-strategy.md`
  instead of inlining technology lists; "Recent Changes" section retained.
-->
**Version**: 1.1.1 | **Ratified**: 2026-03-11 | **Last Amended**: 2026-03-26
