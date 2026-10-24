<!-- SPDX-License-Identifier: MIT-0 -->
# ai_agent_workspace — Design Notes

## Clone only — no skill is activated from the clone

This role clones [wonderbird/ai-agent-workspace](https://github.com/wonderbird/ai-agent-workspace)
to `~/Documents/Cline/ai-agent-workspace` and does nothing else. It
deliberately activates no skill in any tool: it creates no
`~/.claude/skills/<name>` links into the clone and imports nothing into
Skill Manager (`sm`). The `claude_code_config` role imports the
ai-agent-workspace skills into `sm` from GitHub, not from this clone.

Rationale: a generic skill-library clone and a tool-specific skill
activation step genuinely belong in different roles under this extraction's
single-responsibility goal (Constitution Principle II). Other harnesses may
want the clone without any tool's activation step.

Consequence: `claude_code_config` does not depend on this role. Its Molecule
`converge.yml` does not compose it, and it reads nothing from the clone.

## Applied only where the opinionated Claude Code setup is

The base play does not list this role. The clone belongs to the owner's Claude
Code way of working, so the role runs in the play for hosts that opt into the
opinionated Claude Code configuration, listed before `claude_code_config`.
Hosts without that opt-in get no clone. The order is orchestration only:
`claude_code_config` has no hard runtime need for the clone, so it declares no
`meta/main.yml` dependency (Constitution Principle II).
