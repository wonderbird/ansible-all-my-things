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

Read `.cursor/rules/general/310-collaboration.mdc` — it governs all interaction
with the user.

If rules conflict, then you MUST ask the user for clarification before
proceeding. The full collaboration rules (language, one-question-at-a-time,
avoiding ambiguity) are in `.cursor/rules/general/310-collaboration.mdc`.

## How to follow your custom instructions

Whenever the user says "follow your custom instructions", then you must read
`.cursor/rules/general/500-cline-memory-bank.mdc`.

Then read `.cursor/rules/510-memory-bank-branches.mdc` to learn where the
memory bank is stored in this project.

If there is no memory bank, then you MUST ask the user for clarification
before proceeding.

Then read the memory bank and identify the immediate next action.

Afterwards, read the project constitution at `.specify/memory/constitution.md`
and verify that your plan complies with each principle.

Then identify the applicable rules and read them.

Finally, confirm readiness as described in `.cursor/rules/general/900-confirm-readiness.mdc`.

## LS tool does not show hidden files

When you want to check whether a hidden file or directory exists, then
you MUST use the Bash tool to run `ls -la <path>`. The LS tool does not handle
hidden files.

## Rule index

The table below lists every rule file in `.cursor/rules/general/` and
project-specific rules in `.cursor/rules/` with the description from
their frontmatter. Use it to decide which rules to read for your current
task.

| Rule | When to read |
| --- | --- |
| [020-rule-confirmation.mdc](.cursor/rules/general/020-rule-confirmation.mdc) | Always applied |
| [310-collaboration.mdc](.cursor/rules/general/310-collaboration.mdc) | Always applied |
| [330-git-usage.mdc](.cursor/rules/general/330-git-usage.mdc) | Use for documenting version information and when committing to git |
| [340-molecule-testing.mdc](.cursor/rules/340-molecule-testing.mdc) | Use when implementing or modifying an Ansible role to set up or maintain its Molecule test scenario |
| [380-remediation-protocol.mdc](.cursor/rules/general/380-remediation-protocol.mdc) | Use when an unexpected obstacle prevents progress |
| [400-markdown-formatting.mdc](.cursor/rules/general/400-markdown-formatting.mdc) | Use after creating or modifying a markdown file (`*.md`, `*.mdc`) |
| [500-cline-memory-bank.mdc](.cursor/rules/general/500-cline-memory-bank.mdc) | Use when following 'follow your custom instructions' to understand the memory bank concept |
| [600-documentation-strategy.mdc](.cursor/rules/general/600-documentation-strategy.mdc) | Use when creating and updating documentation |
| [610-project-specific-documentation-strategy.mdc](.cursor/rules/610-project-specific-documentation-strategy.mdc) | Read immediately after 600-documentation-strategy.mdc; project-specific documentation structure |
| [900-confirm-readiness.mdc](.cursor/rules/general/900-confirm-readiness.mdc) | Use when responding to the "follow your custom instructions" command |

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
