# Agent Instructions

<!-- markdownlint-disable MD013 MD022 MD025 MD031 MD032 MD034 -->
<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:970c3bf2 -->
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

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->
<!-- markdownlint-enable MD013 MD022 MD025 MD031 MD032 MD034 -->

## Beads: Data Safety and Workflow Rules

### `.beads/issues.jsonl` is git-tracked

`.beads/issues.jsonl` is intentionally force-added and tracked in git — the
root `.gitignore` uses `.beads/*` with `!.beads/issues.jsonl` and
`!.beads/config.yaml` negations, because a directory-pattern ignore blocks
any later negation from any ignore file (including a clone-local
`.git/info/exclude` written by a future `bd init`), so the whitelist must
live in the tracked `.gitignore`. This makes the file survive across clones
even without a Dolt remote sync.

`.beads/config.yaml` keeps beads out of git's way: `no-git-ops: true`, so bd
runs no git operation of its own, and no auto-export is configured. bd's
auto-export hardcodes memories, infra, templates, and gates out of every
write (`includeMemories=false`, unconditionally — GH#3650: memories may hold
private agent context that must not land in git history via the automatic
path), and no config key widens that scope. Since memories must be captured
too, the export is manual and full:

```bash
bd export --all -o .beads/issues.jsonl   # run after EACH bd mutation
```

**Always use `--all`, never plain `bd export` and never re-enable
`export.auto`, on this file.** Verified: bd's own overwrite guard compares
the new write's scope against what is already in the file — if a
narrower-scope write (e.g. a plain `bd export`, or auto-export) follows a
`--all` write, it refuses to overwrite (`auto-export shrink guard: refusing
to overwrite ... contains N record(s) outside auto-export scope`) and every
later export silently stops updating the file until manually repaired.
Consistency of scope, not any single flag, is what keeps this working.

Staging and committing the file still follow the normal Agent Context
Profile git policy above (Conservative default: report status, do not
commit without being asked). Bundle the export once per response, after all
bd operations in that response are done — not once per individual `bd`
command.

bd's Dolt-backed sync (`refs/dolt/data`) remains available as a secondary
mechanism, but the tracked, `--all`-exported JSONL is the primary durability
path here: issues and memories are both recoverable from a plain git clone
without ever needing `bd dolt pull`.

### bd's git hooks stay uninstalled

bd offers git hooks that would drive this synchronisation automatically. They
are deliberately not installed, so `bd info` reports its git hooks as missing
and advises `bd hooks install`. That warning is expected here and is not a
task.

Installing them restores the automatic export path, whose scope is the defect
the manual `--all` export exists to avoid, and adds a `prepare-commit-msg`
hook that writes trailers of its own into every commit message — the `commit`
skill is this repository's only authority on commit format.

### Never run `bd list --all`

**NEVER run `bd list --all`** — at ~350 issues it enters an unbounded output
loop (5.6 GB, 100% CPU, SIGKILL, nearly fills the 17 GB agent disk). For bulk
reads, query `.beads/issues.jsonl` directly with `grep`/`jq`. For live queries
use only scoped commands: `bd ready`, `bd list --status <s>`,
`bd list --priority <p>`, `bd show <id>`. If unavoidable, bound it:
`timeout 20 bd list --all`. (Bug tracked: 1fg7)

### Findings are always tied to WIP

A finding discovered during implementation must be filed as an issue and
connected to the active WIP (`in_progress` issue or current branch). A finding
not tied to active WIP must be converted to a normal feature request: its
headline must **not** contain the word "Finding", though the description may
note provenance.

### Findings gates are closed by humans only

**AI agents MUST NOT close a findings gate.** A findings gate is a human
review checkpoint — it signals that a set of findings has been collected and
is awaiting human sign-off. Only the human reviewer closes it after confirming
each child finding has been addressed. This applies regardless of how many
child tasks have been closed.

## Beads: Description Formatting

Beads issue descriptions render in the beads viewer (`bv`). Write them as
structured Markdown so they are readable there, not as one unbroken blob:

- Use `##` headings to separate sections (e.g. Source, Problem, Fix,
  Developer view).
- Separate paragraphs with blank lines; use `-` bullet or numbered lists for
  enumerations.
- Pass real newlines when setting the field. A single-line
  `--description "…"` stores zero line breaks and renders as a blob; instead
  feed a here-doc, e.g.
  `bd update <id> --description "$(cat <<'EOF' … EOF)"`.

This applies to every `bd create` / `bd update` description, including gate and
finding bodies.

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

### Attaching Issues to Epics (epics cannot be gated)

`bd dep add` connects **any pair of issue types except `epic`** — an epic
connects only to another epic. So an epic cannot be gated out of `bd ready`
by its non-epic children:

- `bd dep add` between an epic and a non-epic is rejected in **both**
  directions (`<epic> <non-epic>` and `<non-epic> <epic>`), each printing
  `Error: epics can only block other epics, not tasks` (the message always
  says "not tasks", whatever the real type). A non-epic therefore cannot block
  its epic. Epic↔epic edges ARE permitted; non-epic pairs gate normally (a
  task can block a task, a feature, etc.).
- `--parent` attaches a child for display/scope only. It does NOT gate
  readiness and does NOT exclude the parent from `bd ready`.

```shell
bd update <child-id> --parent <epic-id>
```

An epic with open children therefore REMAINS in `bd ready`. Do not rely on
`bd ready` exclusion to track epic scope — read the epic's CHILDREN section
via `bd show <epic-id>` instead. See
[triage.md](docs/architecture/concepts/issue-tracking/triage.md) for the
validated dep-add type matrix and `--parent` / `bd ready` semantics
(bd v1.0.4).

### Beads Dependency Wiring — Cross-Tree Follow-Ups

Operationalizes Principle VIII (cross-tree blocking). When a policy or review
decision constrains in-flight work in another tree, wire the blocking dep
**immediately** — but mind the type rule: `bd dep add` cannot make an `epic`
block a non-epic (rejected; see "Attaching Issues to Epics" above). If the
follow-up is tracked as an epic, use a **non-epic** issue as the actual
blocker — a concrete task under that epic, or a `gate` checkpoint (verified:
a `gate` blocks a non-epic and gates it out of `bd ready`). Wire it as
`bd dep add <in-flight-issue> <non-epic-blocker>` (in-flight depends on
blocker).

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

This repository has a single remote:

- **`origin`** — `wonderbird/ansible-all-my-things`: the canonical upstream
  and the agent's workspace. **All pushes go to `origin`.**

**`gh pr create`:** with a single remote, `gh pr create` targets `origin`
by default. Specifying the target repo explicitly keeps the command
unambiguous:

```bash
gh pr create --repo wonderbird/ansible-all-my-things \
  --head <branch> --base main
```

**Branch naming:** branch names MUST allow the associated epic (or work item)
to be inferred, so work-in-progress can be recovered from the git branch alone
when no issue is marked `in_progress`.

## Collaboration with the User

- **Language**: English throughout. Apply the caveman skill by audience —
  `caveman full` for user-facing content (chat, code, comments, documentation,
  beads issues); `caveman wenyan-ultra` for internal and inter-agent content
  (thinking, subagents, MCP, tool calls, and every file an agent framework
  keeps its own state in — `.omc/`, `.omo/`). Code blocks, commit messages,
  and security warnings stay in normal English regardless of mode, and so do
  plan files wherever a framework writes them (`.omc/plans/`, `.omo/plans/`):
  a plan is read and reviewed by people, and a compressed one cannot be
  reviewed unambiguously. The skills define each mode.
- **One question at a time**: when asking the user a question, ask one
  question at a time so they can focus.
- **Avoid ambiguity**: if instructions are unclear, contradictory, or
  conflict with rules or earlier instructions, describe the situation and
  ask clarifying questions before proceeding.
- **Issue IDs carry their goal**: never mention a beads issue ID without its
  goal. If the surrounding text does not already make the goal clear, add it
  in a few words in parentheses right after the ID, e.g.
  `<id> (retry on rate-limited download)`. This
  applies to chat, summaries, status reports, and every list of issues. A bare
  ID forces the reader to look it up before they can follow the text.
- **Label evidence in reports**: in a status report, review, or handoff, mark
  every factual claim about code, tool behaviour, or system state as VERIFIED
  (you ran it and read the output) or INFERRED (reasoned, predicted, or
  reported by another agent). Never present another agent's assurance as
  evidence. Re-verify a claim on the exact branch or state where it will be
  used. An unlabelled claim makes the reader trust a guess as much as a test
  result; for when a guard's result counts as evidence at all, see Principle
  XV.
- **Hidden files**: the LS tool does not show hidden files; use
  `ls -la <path>` via Bash to check for hidden files or directories.

## Mandatory skill invocations

Skills whose invocation is mandatory, and the rule that makes it so. The agent
runtime injects the full skill catalog (names + descriptions) each session;
only the mandatory bindings are restated here. The rule named is a principle or
section of the constitution unless the entry says otherwise.

| Skill | Invoke when | Mandated by |
| --- | --- | --- |
| `caveman` | always; mode depends on audience | Collaboration with the User, in this file |
| `ansible-changelog-entry` | before requesting review on a pull request | Development Workflow |
| `commit` | before creating any commit | V |
| `format-markdown` | at task close, after all Markdown finalized | VI |
| `fix-problem` | before fixing any unexpected obstacle | VII |
| `ansible-molecule-testing` | when creating/modifying a role's Molecule scenario | II |
| `ansible-review-documentation` | at task close, before `format-markdown` | Documentation Standards |

Skills without the `ansible-` prefix live outside this repository and are not
pinned by it, so the rules they carry can change without review here.
`caveman` comes from a third party; the others are authored by the repository
owner. Adopting a skill from outside that set changes the trust boundary and is
a decision to take deliberately.

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
