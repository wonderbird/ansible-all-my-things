# CLAUDE.md

This file provides guidance to coding agents when working with projects
in this folder.

## Rules are stored in .specify/memory/constitution.md and in .cursor/rules

This project uses spec-kit for guiding the coding agent. Thus, rules important
for developing the project are stored in `.specify/memory/constitution.md`.
This file is the source of truth for the project and must be read and followed
carefully.

Rules describing the interaction between the coding agent and the user
are stored in the .cursor/rules directory and in contained subdirectories.

Read `.cursor/rules/general/020-rule-confirmation.mdc` — it applies to
every response you produce.

If rules conflict, then you MUST ask the user for clarification before
proceeding. The full collaboration rules (language, one-question-at-a-time,
avoiding ambiguity) are in `.cursor/rules/general/310-collaboration.mdc`.

## How to follow your custom instructions

Whenever the user says "follow your custom instructions", then you must read .cursor/rules/general/500-cline-memory-bank.mdc.

Then read .cursor/rules/510-memory-bank-branches.mdc to learn where the
memory bank is stored in this project.

If there is no memory bank, then you MUST ask the user for clarification
before proceeding.

Then read the memory bank and identify the immediate next action.

Afterwards, read the project constitution at `.specify/memory/constitution.md`
and verify that your plan complies with each principle.

Then identify the applicable rules and read them.

Finally, confirm readiness as described in .cursor/rules/general/900-confirm-readiness.mdc.

## LS tool does not show hidden files

When you want to check whether a hidden file or directory exists, then
you MUST use a tool native to the operating system you are running on.
The LS tool does not handle hidden files.

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
