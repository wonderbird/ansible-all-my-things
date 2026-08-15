<!-- SPDX-License-Identifier: MIT-0 -->

# claude_code role — Design Notes

## Why auto-update is disabled

The Claude Code binary self-updates in the background by default, which
would let the running version drift away from this role's pinned
`claude_code_version`. See `claude_code_config/DESIGN.md`'s "Why auto-update
is disabled" section for the full rationale — the settings.json keys that
enforce the pin live there, since they live in `~/.claude/settings.json`.

## Install-only scope: no `~/.claude` opinionation

This role installs only the binary, its OS package prerequisites (`jq`,
`git`, `curl`), and the `PATH` entry. It deliberately does not create or
write into `~/.claude` in any way, so a host can have Claude Code installed
without any global configuration opinion — the prerequisite for an
install-only profile. All `~/.claude` configuration (settings.json merge,
plugin installs, skills symlinks, MCP servers, the `omc` CLI) lives in the
separate `claude_code_config` role, which declares this role as a
`meta/main.yml` dependency.
