# Agent Instructions

<!-- markdownlint-disable MD013 MD031 MD032 -->
<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files
- When an issue's implementation state changes materially, update its description
  to reflect the current state — stale descriptions mislead the next session

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->

<!-- bv-agent-instructions-v2 -->

---

## Beads Workflow Integration

This project uses **bd (beads)** for issue tracking and [beads_viewer](https://github.com/Dicklesworthstone/beads_viewer) (`bv`) for graph-aware triage. Issues are stored in `.beads/` and tracked in git.

### Using bv as an AI sidecar

bv is a graph-aware triage engine for Beads projects (.beads/issues.jsonl). Instead of parsing JSONL or hallucinating graph traversal, use robot flags for deterministic, dependency-aware outputs with precomputed metrics (PageRank, betweenness, critical path, cycles, HITS, eigenvector, k-core).

**Scope boundary:** bv handles *what to work on* (triage, priority, planning). `bd` handles creating, modifying, and closing beads.

**CRITICAL: Use ONLY --robot-* flags. Bare bv launches an interactive TUI that blocks your session.**

#### The Workflow: Start With Triage

**`bv --robot-triage` is your single entry point.** It returns everything you need in one call:
- `quick_ref`: at-a-glance counts + top 3 picks
- `recommendations`: ranked actionable items with scores, reasons, unblock info
- `quick_wins`: low-effort high-impact items
- `blockers_to_clear`: items that unblock the most downstream work
- `project_health`: status/type/priority distributions, graph metrics
- `commands`: copy-paste shell commands for next steps

```bash
bv --robot-triage        # THE MEGA-COMMAND: start here
bv --robot-next          # Minimal: just the single top pick + claim command

# Token-optimized output (TOON) for lower LLM context usage:
bv --robot-triage --format toon
```

Before claiming, verify current state with `bd show <id>` or `bd ready`. `recommendations` can include graph-important blocked or assigned work; only `quick_ref.top_picks` and non-empty `claim_command` fields represent claimable work.

#### Other bv Commands

| Command | Returns |
|---------|---------|
| `--robot-plan` | Parallel execution tracks with unblocks lists |
| `--robot-priority` | Priority misalignment detection with confidence |
| `--robot-insights` | Full metrics: PageRank, betweenness, HITS, eigenvector, critical path, cycles, k-core |
| `--robot-alerts` | Stale issues, blocking cascades, priority mismatches |
| `--robot-suggest` | Hygiene: duplicates, missing deps, label suggestions, cycle breaks |
| `--robot-diff --diff-since <ref>` | Changes since ref: new/closed/modified issues |
| `--robot-graph [--graph-format=json\|dot\|mermaid]` | Dependency graph export |

#### Scoping & Filtering

```bash
bv --robot-plan --label backend              # Scope to label's subgraph
bv --robot-insights --as-of HEAD~30          # Historical point-in-time
bv --recipe actionable --robot-plan          # Pre-filter: ready to work (no blockers)
bv --recipe high-impact --robot-triage       # Pre-filter: top PageRank scores
```

<!-- end-bv-agent-instructions -->
<!-- markdownlint-enable MD013 MD031 MD032 -->

## Beads: Issue Types and Dependency Rules

### Issue Types

Built-in types and when to use each:

| Type        | Use when                                              |
|-------------|-------------------------------------------------------|
| `task`      | Default. General work item. (default when omitted)    |
| `bug`       | Something broken that must be fixed.                  |
| `feature`   | New user-facing capability.                           |
| `chore`     | Maintenance, cleanup, non-functional work.            |
| `epic`      | Large body of work grouping child issues.             |
| `spike`     | Timeboxed investigation to reduce uncertainty.        |
| `story`     | User story (user-centric feature description).        |
| `decision`  | Architectural or design decision to document.         |
| `milestone` | Marks completion of a set of related issues.          |
| `gate`      | Async coordination checkpoint (blocks until cleared). |
| `molecule`  | Beads work template — NOT Ansible Molecule testing.   |

### Epic Gating

Non-epic issues cannot use `blocks` on epics (cross-type restriction).
To gate an epic on required work, use `parent-child`:

```shell
bd dep add <child-id> <epic-id> --type parent-child
```

The epic is excluded from `bd ready` while any open child exists.
Among non-epics, any type may block any other type.

### Beads Dependency Wiring — Cross-Tree Follow-Ups

When an ADR acceptance, review, or policy decision produces follow-up epics
that impose compliance requirements on in-flight work in a **different epic
tree**, add those follow-ups as `bd dep` blockers on the affected issue
immediately. Tracking a follow-up only under its own parent epic — without
connecting it to the constrained feature — allows premature closure of work
that is not yet compliant.

**Type alignment**: beads restricts `blocks` only at the epic boundary — epics
may only block other epics, non-epics may block any other non-epic type.
On epic/non-epic mismatch, use `parent-child` instead; do not create relay
issues as adapters.

**Signal the next action for the next session**: after wiring the deps, claim
both the blocked issue and the immediate actionable follow-up:

```bash
bd update <blocked-issue> --claim   # signals "this goal is in flight"
bd update <follow-up> --claim       # signals "work on this next"
```

Without claiming, triage ranks by graph score. A high-impact unrelated issue
will outrank the follow-up you actually need to work on, causing the next
session to pick up the wrong work.

## Collaboration with the User

- **Language**: chat is in English. For your thinking processes and
  communication with (sub-)agents use the "caveman wenyan-ultra" skill. For user
  facing writing (documentation, code, etc.) and chat use "caveman full".
  Consider all files in `.omc` folder not user facing inter-agent communication.
- **One question at a time**: when asking the user a question, ask one
  question at a time so they can focus.
- **Avoid ambiguity**: if instructions are unclear, contradictory, or
  conflict with rules or earlier instructions, describe the situation and
  ask clarifying questions before proceeding.
- **Hidden files**: the LS tool does not show hidden files; use
  `ls -la <path>` via Bash to check for hidden files or directories.

## Rules are stored in .specify/memory/constitution.md

This project uses spec-kit for guiding the coding agent. Project rules are
stored in `.specify/memory/constitution.md`. That file is the source of
truth and must be read and followed carefully.

## Skill index

The table below lists all skills relevant to this project. Local skills are in
`.claude/skills/`; global skills are installed with the agent runtime. Use it
to decide which skills to invoke for your current task.

| Skill | Scope | When to invoke |
| --- | --- | --- |
| [developer](.claude/skills/developer/SKILL.md) | local | Use when expert knowledge of Ansible is required to analyze, implement, or fix features. Project scope: setting up and maintaining virtual machines. |
| [molecule-testing](.claude/skills/molecule-testing/SKILL.md) | local | Pull in information about the molecule testing setup for Ansible roles. Use when implementing or modifying an Ansible role to set up or maintain its Molecule test scenario. |
| [review-documentation-here](.claude/skills/review-documentation-here/SKILL.md) | local | Extends review-documentation by project-specific documentation structure, including co-located role documentation. Use when reviewing the project documentation. |
| [technical-coach](.claude/skills/technical-coach/SKILL.md) | local | Use when expert knowledge of Ansible is required to advise and tutor on automating setup and maintenance of virtual machines. |
| `commit` | global | Authoritative source for commit format, allowed prefixes, message structure, and co-authorship rules. MUST invoke before creating any commit (Principle V). |
| `format-markdown` | global | Authoritative Markdown linting ruleset. MUST invoke once at close of task after all Markdown files are finalized (Principle VI). |
| `fix-problem` | global | Remediation protocol for unexpected obstacles (test failure, tooling error, regression). MUST invoke before attempting fixes (Principle VII). |
| `review-documentation` | global | Base documentation review strategy and folder structure. Extended by `review-documentation-here` for this project. |

## Test environment host architecture

**Do not assume the architecture of the machine running Claude Code.**
`Platform: linux` in the environment info does not imply AMD64. Docker
containers also do not imply AMD64 — on Apple Silicon they run ARM64 by
default.

When a task requires knowing the current host's architecture (e.g.
deciding which test target to use), check it explicitly with `uname -m`
before proceeding. Only check when it is relevant — not on every task.

The known test hosts and their architectures are listed in [README.md](README.md#overview).

## Architecture documentation

Technology decisions, the top-level decomposition strategy, and platform
constraints are documented in
[`docs/architecture/solution-strategy.md`](docs/architecture/solution-strategy.md)
(arc42 Section 4).

Architecture Decision Records are in
[`docs/architecture/decisions/`](docs/architecture/decisions/).

These are the canonical locations for architectural decisions; they MUST
NOT be recorded in `CLAUDE.md` or agent-specific context files.

## Active Technologies

- YAML (Ansible 2.19+) + `community.general` collection + `ansible.builtin.*`;
  Ubuntu `podman` apt package for rootless containers
