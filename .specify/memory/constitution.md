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

**Headline conventions by type:**

- `feat:` — describes the new capability (what the project can now do), not
  what was implemented. Write "feat: backup claude configuration", not
  "feat: implement backup script".
- `fix:` — describes the most important symptom of the problem in past tense.
  The commit body describes the root cause and major fix steps.
- `test:` — describes the capability under test as a BDD-style requirement
  ("test: playbook runs idempotently on Ubuntu 24.04").
- `docs:` — used for commits that change only documentation files. MUST NOT
  use `refactor:` for documentation-only changes.
- `ci:` — describes the new capability added to the CI/CD pipeline.
- `build(deps):` — describes dependency updates in `requirements.yml`,
  `requirements.txt`, or similar files.

**Body rules:**

- Subject, body and trailers MUST each be separated by a blank line.
- The commit body MUST NOT exceed 50 words.
- Version history MUST NOT be embedded in documents — git is the sole source
  of version and author information.

**AI agent co-authorship:**

AI coding agents MUST be credited using a `Co-authored-by:` trailer on every
commit they help produce. Use the agent name and email from the table below:

| Agent | Email |
|---|---|
| Claude Code | `noreply@anthropic.com` |
| Cursor Agent | `cursoragent@cursor.com` |
| GitHub Copilot | `175728472+Copilot@users.noreply.github.com` |

If a commit has a body, also add the following line at the end of the body:

```text
🤖 Generated with [MODEL_NAME](MODEL_VENDOR_URL)
```

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

Documentation is organised in three tiers:

| Location | Purpose |
|---|---|
| `README.md` | Minimal developer onboarding — quick start, prerequisites, links only. No duplication of content held elsewhere. |
| `specs/<feature>/` | Working context per feature: spec, plan, research, tasks (managed by spec-kit). Promoted to `docs/` when stable and feature-agnostic. |
| `docs/` | Stable reference material — architecture (arc42-inspired), user manual, long-term decisions. |

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

**Version**: 1.0.0 | **Ratified**: 2026-03-11 | **Last Amended**: 2026-03-11
