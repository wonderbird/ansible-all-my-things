# Agent Instructions

<!-- markdownlint-disable MD013 MD031 MD032 -->
<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

## Golden Rule

**Always prefix commands with `rtk`**. If RTK has a dedicated filter, it uses it. If not, it passes through unchanged. This means RTK is always safe to use.

**Important**: Even in command chains with `&&`, use `rtk`:
```bash
# ❌ Wrong
git add . && git commit -m "msg" && git push

# ✅ Correct
rtk git add . && rtk git commit -m "msg" && rtk git push
```

## RTK Commands by Workflow

### Build & Compile (80-90% savings)
```bash
rtk cargo build         # Cargo build output
rtk cargo check         # Cargo check output
rtk cargo clippy        # Clippy warnings grouped by file (80%)
rtk tsc                 # TypeScript errors grouped by file/code (83%)
rtk lint                # ESLint/Biome violations grouped (84%)
rtk prettier --check    # Files needing format only (70%)
rtk next build          # Next.js build with route metrics (87%)
```

### Test (60-99% savings)
```bash
rtk cargo test          # Cargo test failures only (90%)
rtk go test             # Go test failures only (90%)
rtk jest                # Jest failures only (99.5%)
rtk vitest              # Vitest failures only (99.5%)
rtk playwright test     # Playwright failures only (94%)
rtk pytest              # Python test failures only (90%)
rtk rake test           # Ruby test failures only (90%)
rtk rspec               # RSpec test failures only (60%)
rtk test <cmd>          # Generic test wrapper - failures only
```

### Git (59-80% savings)
```bash
rtk git status          # Compact status
rtk git log             # Compact log (works with all git flags)
rtk git diff            # Compact diff (80%)
rtk git show            # Compact show (80%)
rtk git add             # Ultra-compact confirmations (59%)
rtk git commit          # Ultra-compact confirmations (59%)
rtk git push            # Ultra-compact confirmations
rtk git pull            # Ultra-compact confirmations
rtk git branch          # Compact branch list
rtk git fetch           # Compact fetch
rtk git stash           # Compact stash
rtk git worktree        # Compact worktree
```

Note: Git passthrough works for ALL subcommands, even those not explicitly listed.

### GitHub (26-87% savings)
```bash
rtk gh pr view <num>    # Compact PR view (87%)
rtk gh pr checks        # Compact PR checks (79%)
rtk gh run list         # Compact workflow runs (82%)
rtk gh issue list       # Compact issue list (80%)
rtk gh api              # Compact API responses (26%)
```

### JavaScript/TypeScript Tooling (70-90% savings)
```bash
rtk pnpm list           # Compact dependency tree (70%)
rtk pnpm outdated       # Compact outdated packages (80%)
rtk pnpm install        # Compact install output (90%)
rtk npm run <script>    # Compact npm script output
rtk npx <cmd>           # Compact npx command output
rtk prisma              # Prisma without ASCII art (88%)
```

### Files & Search (60-75% savings)
```bash
rtk ls <path>           # Tree format, compact (65%)
rtk read <file>         # Code reading with filtering (60%)
rtk grep <pattern>      # Search grouped by file (75%). Format flags (-c, -l, -L, -o, -Z) run raw.
rtk find <pattern>      # Find grouped by directory (70%)
```

### Analysis & Debug (70-90% savings)
```bash
rtk err <cmd>           # Filter errors only from any command
rtk log <file>          # Deduplicated logs with counts
rtk json <file>         # JSON structure without values
rtk deps                # Dependency overview
rtk env                 # Environment variables compact
rtk summary <cmd>       # Smart summary of command output
rtk diff                # Ultra-compact diffs
```

### Infrastructure (85% savings)
```bash
rtk docker ps           # Compact container list
rtk docker images       # Compact image list
rtk docker logs <c>     # Deduplicated logs
rtk kubectl get         # Compact resource list
rtk kubectl logs        # Deduplicated pod logs
```

### Network (65-70% savings)
```bash
rtk curl <url>          # Compact HTTP responses (70%)
rtk wget <url>          # Compact download output (65%)
```

### Meta Commands
```bash
rtk gain                # View token savings statistics
rtk gain --history      # View command history with savings
rtk discover            # Analyze Claude Code sessions for missed RTK usage
rtk proxy <cmd>         # Run command without filtering (for debugging)
rtk init                # Add RTK instructions to CLAUDE.md
rtk init --global       # Add RTK to ~/.claude/CLAUDE.md
```

## Token Savings Overview

| Category | Commands | Typical Savings |
|----------|----------|-----------------|
| Tests | vitest, playwright, cargo test | 90-99% |
| Build | next, tsc, lint, prettier | 70-87% |
| Git | status, log, diff, add, commit | 59-80% |
| GitHub | gh pr, gh run, gh issue | 26-87% |
| Package Managers | pnpm, npm, npx | 70-90% |
| Files | ls, read, grep, find | 60-75% |
| Infrastructure | docker, kubectl | 85% |
| Network | curl, wget | 65-70% |

Overall average: **60-90% token reduction** on common development operations.
<!-- /rtk-instructions -->

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
- When a feature issue transitions to `in_progress`, instantiate the `pr-review-cycle`
  molecule and attach its user story as a child of the feature:
  ```bash
  bd mol pour pr-review-cycle        # instantiate; note the returned story ID
  bd update <story-id> --parent <feature-id>  # attach story to feature
  ```

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

### Epic Gating and Attaching Issues to Epics

Non-epic issues cannot block epics (`bd dep add epic non-epic` fails with
"epics can only block other epics"). Use `--parent` instead:

```shell
bd update <child-id> --parent <epic-id>
```

This attaches the child to the epic and gates it: the epic is excluded from
`bd ready` while any open child exists.

**Common case — findings discovered during WIP:** when a bug or task is
found while working on an epic (e.g. a test failure on the feature branch),
attach it immediately:

```shell
bd update <finding-id> --parent <epic-id>
```

Do NOT attempt `bd dep add <epic-id> <finding-id>` — that errors.

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

## Repository Remotes and Pull-Request Workflow

This repository is a fork. Two remotes exist:

- **`origin`** — `eudicy/ansible-all-my-things`: the fork and the agent's
  workspace. **All pushes go to `origin` only.**
- **`upstream`** — `wonderbird/ansible-all-my-things`: **READ-ONLY.** Never
  push, force-push, merge, or otherwise write to it. Pull requests that target
  `wonderbird` are merged manually by the user on GitHub. Never run
  `gh pr merge`, push directly to `upstream`, or merge locally and push to
  `upstream`.

**`gh pr create` gotcha:** in a fork, `gh pr create` defaults the *target*
repository to `upstream`, and without `--repo` it may not reference the fork
where the commits actually live. For a cross-repo PR (fork branch → upstream
`main`):

```bash
gh pr create --repo wonderbird/ansible-all-my-things \
  --head eudicy:<branch> --base main
```

**Branch naming:** branch names MUST allow the associated epic (or work item)
to be inferred, so work-in-progress can be recovered from the git branch alone
when no issue is marked `in_progress`.

## Collaboration with the User

- **Language and style**: Use English throughout. For all user-facing
  content — chat, code, comments, documentation, beads issues — apply the
  `caveman full` skill: drop articles, filler, and hedging; fragments OK;
  short synonyms; technical terms exact. For internal thought processes and
  inter-LLM communication (subagents, MCP, tool calls) apply the
  `caveman wenyan-ultra` skill: maximum compression, classical Chinese
  register. Code blocks, commit messages, and security warnings are always
  written in normal English regardless of mode.
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
