# Documentation & Rules Consistency Review

**Reviewed by**: GitHub Copilot
**Review date**: 2026-03-12
**Scope**: Changes introduced after commit `90cdfaab` up to and including `HEAD` (`2ff9ba0`)

## Commits Reviewed

| Hash | Message |
|---|---|
| `0423a55` | docs: ratify project constitution v1.0.0 |
| `45457ba` | docs: replace general rules symlink with selective rule links; add --no-pager rule to CLAUDE.md |
| `ee13108` | docs: make constitution self-contained and fix backtick formatting |
| `1191dd2` | feat: add spec-kit commands, templates and scripts |
| `85acad9` | fix: create .bash_profile before modifying it |
| `2ff9ba0` | docs: claude considers spec-kit constitution |

## Files Changed

- `.specify/memory/constitution.md` — new file (project constitution)
- `CLAUDE.md` — updated with spec-kit references and --no-pager rule
- `.cursor/rules/general` — replaced single directory symlink with four individual file symlinks
- `.specify/scripts/bash/` — new spec-kit bash scripts
- `.specify/templates/` — new spec-kit templates
- `.claude/commands/speckit.*.md` — new spec-kit commands for Claude Code
- `playbooks/setup-homebrew.yml` — removed .bash_profile task
- `playbooks/setup-users.yml` — added .bash_profile creation task

## Findings

Findings are sorted by priority (P1 = critical, P4 = low).

---

### [P1] CLAUDE.md references the wrong path for the project constitution

**Priority**: Critical
**Affected file**: `CLAUDE.md`
**Related commit**: `2ff9ba0` (docs: claude considers spec-kit constitution)

**Description**:
`CLAUDE.md` tells every AI agent that the constitution lives at `.specify/constitution.md`. The
actual file path is `.specify/memory/constitution.md`. This appears both in the section heading
("Rules are stored in .specify/constitution and in .cursor/rules") and in the body text that
reads: "rules important for developing the project are stored in `.specify/constitution.md`".

**Impact**:
Any AI agent that follows `CLAUDE.md` to locate and read the constitution will look in the wrong
place. It will either get a "file not found" error or silently skip the constitution. As a result
the agent will proceed without knowledge of the project's core principles (idempotency, role-first
organisation, conventional commits, etc.).

**Suggested resolution**:
Update `CLAUDE.md` to replace every occurrence of `.specify/constitution.md` (and the heading
reference) with the correct path `.specify/memory/constitution.md`.

**Resolution**: Fixed in `CLAUDE.md` — heading and body text updated to `.specify/memory/constitution.md`.

---

### [P2] Playbooks contain implementation logic instead of only orchestrating roles

**Priority**: High
**Affected files**: `playbooks/setup-users.yml` and 7 other playbooks
**Related commit**: `85acad9` (fix: create .bash_profile before modifying it)

**Description**:
This is a general design mismatch between the pre-existing codebase and Constitution
Principle II (Role-First Organisation), which was ratified in commit `0423a55`. All eight
playbooks in `playbooks/` pre-date the constitution and contain direct task lists. No
migration was performed when the constitution was ratified. Commit `85acad9` became the
first post-ratification addition to compound this debt by adding a new task directly to
`playbooks/setup-users.yml`.

**Resolution**: Recorded as **TD-002** in
[docs/architecture/technical-debt/technical-debt.md](docs/architecture/technical-debt/technical-debt.md).
To be addressed in a dedicated refactoring effort.

---

### [P3] Memory bank location used in the repository differs from what the rule describes

**Priority**: Medium
**Affected files**: `.cursor/rules/general/500-cline-memory-bank.mdc`, `CLAUDE.md`
**Related commits**: `45457ba`, `2ff9ba0`

**Description**:
The memory bank rule (`.cursor/rules/general/500-cline-memory-bank.mdc`) states:

> "The memory bank is stored in the folder `memory-bank/` next to the `.cursor/` folder."

This repository places memory bank files in `memory-bank-branches/<branch-name>/` (for example
`memory-bank-branches/feat.command.restrictions/`). There is no `memory-bank/` directory at the
repository root. Neither `CLAUDE.md` nor the constitution document this deviation or explain the
`memory-bank-branches/` folder structure.

**Impact**:
An AI agent that reads the memory bank rule will look for `memory-bank/` and find nothing. It
will either fail to load the memory bank or treat the repository as having no prior context. This
undermines the entire memory bank workflow.

**Suggested resolution**:
Either:
1. Add a note to `CLAUDE.md` that explains the project-specific path:
   "Memory banks for this project are stored under `memory-bank-branches/<branch-name>/` instead
   of `memory-bank/`. When following the memory bank rule, substitute the appropriate
   `memory-bank-branches/<branch-name>/` path."
2. Alternatively, restructure memory banks to use the standard `memory-bank/` path (renaming
   `memory-bank-branches/` to `memory-bank/` and using subdirectories named after branches).

**Resolution**: Created `.cursor/rules/general/510-memory-bank-branches.mdc` — a project-specific
rule (read after `500-cline-memory-bank.mdc`) that documents the `memory-bank-branches/`
structure and instructs the agent to ask the user to select a feature at session start.

---

### [P4] "Follow your custom instructions" workflow in CLAUDE.md omits the mandatory constitution read

**Priority**: Low
**Affected file**: `CLAUDE.md`
**Related commit**: `2ff9ba0`

**Description**:
The constitution states: "All agents working in this repository MUST read this constitution at
the start of any non-trivial task and verify that their plan complies with each principle."

The `CLAUDE.md` section "How to follow your custom instructions" describes this sequence:

1. Read `500-cline-memory-bank.mdc`
2. Read the memory bank and identify the next action
3. Read applicable rules
4. Confirm readiness as described in `900-confirm-readiness.mdc`

Reading the constitution is not explicitly listed as a step. An agent following these instructions
to the letter may load the memory bank and proceed without ever reading the constitution.

**Impact**:
Low, because `CLAUDE.md` does instruct agents to read `.specify/constitution.md` (albeit with
the wrong path — see P1). An agent that manages to read the rules section before the workflow
section will find the reference. However, the omission creates an ambiguous ordering: it is
unclear whether "read applicable rules" in step 3 is meant to include the constitution.

**Suggested resolution**:
Add an explicit "Read the constitution" step to the "How to follow your custom instructions"
workflow, for example as step 1 or immediately after reading the memory bank:

> "Read the project constitution at `.specify/memory/constitution.md` and verify your plan
> complies with each principle."

**Resolution**: Added an explicit constitution-reading step to the "How to follow your custom
instructions" workflow in `CLAUDE.md`, placed after reading the memory bank and before reading
applicable rules.

---

### [P4] speckit.constitution command references a non-existent directory for command files

**Priority**: Low
**Affected file**: `.claude/commands/speckit.constitution.md`
**Related commit**: `1191dd2`

**Description**:
The `speckit.constitution` command (`/speckit.constitution`) includes a consistency propagation
step (step 4) that reads:

> "Read each command file in `.specify/templates/commands/*.md` (including this one) to verify
> no outdated references remain when generic guidance is required."

The command files for this project are stored in `.claude/commands/` (for example
`.claude/commands/speckit.analyze.md`). The path `.specify/templates/commands/` does not exist;
`.specify/templates/` contains only six template files, not a `commands/` subdirectory.

**Impact**:
When the `/speckit.constitution` command is run, its step 4 will silently find no command files
to check, leaving spec-kit commands unchecked during constitution updates. This bypasses the
safety check that guards against stale principle references in commands.

**Suggested resolution**:
Update line 49 of `.claude/commands/speckit.constitution.md` to reference the correct path:

> "Read each command file in `.claude/commands/speckit.*.md` (including this one) to verify
> no outdated references remain when generic guidance is required."

**Resolution**: Fixed in `.claude/commands/speckit.constitution.md`. The path `.specify/templates/commands/*.md`
has been corrected to `.claude/commands/speckit.*.md`.

**Note**: The incorrect path `.specify/templates/commands/` originates from the upstream spec-kit
repository template. This should be investigated and reported to the spec-kit maintainer via
GitHub, as other projects using spec-kit will have the same broken cross-check.
