<!-- SPDX-License-Identifier: MIT-0 -->
# skill_factory — Design Notes

## Clone only — no skill is activated from the clone

This role clones [wonderbird/skill-factory](https://github.com/wonderbird/skill-factory)
to `~/Documents/Cline/skill-factory` and does nothing else. It deliberately
activates no skill in any tool: it creates no `~/.claude/skills/<name>` links
into the clone and imports nothing into Skill Manager (`sm`). The
`claude_code_config` role imports the skills into `sm` from GitHub, not from
this clone.

Rationale: a skill-authoring source clone and a tool-specific skill
activation step belong in different roles (Constitution Principle II), the
same split `ai_agent_workspace` follows.

## Tracks the `fork` branch, not `main`

wonderbird/skill-factory is a fork. Its `main` branch mirrors the upstream
repository, and the owner's own changes live on the `fork` branch, which is
also the repository's default branch. The role checks out `fork` by name so
the clone carries the owner's changes even if the default branch changes.

The branch is not pinned to a commit, so the role registers nothing in the
version-update mechanism: re-provisioning pulls the branch head, as for
`ai_agent_workspace`.

## Applied only where the opinionated Claude Code setup is

The base play does not list this role. The clone belongs to the owner's Claude
Code way of working, so the role runs in the play for hosts that opt into the
opinionated Claude Code configuration, next to `ai_agent_workspace`. Hosts
without that opt-in get no clone. No other role reads the clone, so the
position in that play is orchestration only and no role declares a
`meta/main.yml` dependency on this one (Constitution Principle II).
