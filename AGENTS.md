# Agent Instructions

## Collaboration with the User

- **Language**: chat is in English.
- **One question at a time**: when asking the user a question, ask one
  question at a time so they can focus.
- **Avoid ambiguity**: if instructions are unclear, contradictory, or
  conflict with rules or earlier instructions, describe the situation and
  ask clarifying questions before proceeding.
- **Custom instructions**: when the user says "follow your custom
  instructions", use the `/memory-bank-by-cline` skill to understand the
  memory bank concept. If no memory bank exists, ask for clarification.
  Otherwise read the memory bank, identify the next action, read the
  applicable rules, summarize understanding ending with the next immediate
  action, then ask whether to execute it.
- **Hidden files**: the LS tool does not show hidden files; use
  `ls -la <path>` via Bash to check for hidden files or directories.

## Rules are stored in .specify/memory/constitution.md

This project uses spec-kit for guiding the coding agent. Project rules are
stored in `.specify/memory/constitution.md`. That file is the source of
truth and must be read and followed carefully.

## Skill index

The table below lists every skill file in `.claude/skills/` with the description from
their frontmatter. Use it to decide which skills to read for your current
task.

| Skill | When to read |
| --- | --- |
| [molecule-testing](.claude/skills/molecule-testing/SKILL.md) | Pull in information about the molecule testing setup for Ansible roles. Use when implementing or modifying an Ansible role to set up or maintain its Molecule test scenario. |
| [review-documentation-here](.claude/skills/review-documentation-here/SKILL.md) | Extends review-documentation by project-specific documentation structure, including co-located role documentation. Use when reviewing the project documentation. |
| [technical-coach](.claude/skills/technical-coach/SKILL.md) | Use when expert knowledge of Ansible is required to advise and tutor on automating setup and maintenance of virtual machines. |

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

## Active Technologies

- YAML (Ansible 2.19+) + `community.general` collection + `ansible.builtin.*`;
  Ubuntu `podman` apt package for rootless containers

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
