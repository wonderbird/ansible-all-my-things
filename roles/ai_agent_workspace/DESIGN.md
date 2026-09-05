<!-- SPDX-License-Identifier: MIT-0 -->
# ai_agent_workspace — Design Notes

## Clone only — the skill-symlink task stays in claude_code_config

This role clones [wonderbird/ai-agent-workspace](https://github.com/wonderbird/ai-agent-workspace)
to `~/Documents/Cline/ai-agent-workspace` and does nothing else. It
deliberately does **not** create the `~/.claude/skills/<name>` symlinks into
the clone — that task (and its task-level "≥1 skill dir found" assert) stays
in the `claude_code_config` role.

Rationale: a generic skill-library clone and a Claude-Code-specific symlink
step genuinely belong in different roles under this extraction's
single-responsibility goal (Constitution Principle II). Other harnesses may
want the clone without Claude Code's particular symlink convention.

Consequence: `claude_code_config`'s own Molecule `converge.yml` composes this
role together with `claude_code_config`, since the retained symlink
verification needs a real clone to link against. The clone destination path
(`~/Documents/Cline/ai-agent-workspace`) is hardcoded identically in this
role and in `claude_code_config`'s symlink task — a logged Constitution
Principle XI (DRY) exception, accepted because a shared variable would
re-couple the two roles this split is separating.
