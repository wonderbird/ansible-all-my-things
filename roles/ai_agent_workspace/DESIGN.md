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

Consequence: `claude_code_config`'s own Molecule `converge.yml` composes this
role together with `claude_code_config`, since `claude_code_config` declares
it as a `meta/main.yml` dependency.

## Applied only where the opinionated Claude Code setup is

The base play does not list this role. `claude_code_config` is the only
consumer of the clone, so the role runs in the play for hosts that opt into
that configuration, listed before `claude_code_config`, which also declares
it as a hard `meta/main.yml` dependency. Hosts without that opt-in get no
clone.
