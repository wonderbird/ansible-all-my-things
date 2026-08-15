<!-- SPDX-License-Identifier: MIT-0 -->

# claude_code role — Design Notes

## Why auto-update is disabled

Unlike `rtk`/`beads`/`nodejs`, which have no self-update mechanism, the
Claude Code binary itself checks for and installs updates in the background
(on startup and periodically) by default for native/npm-style installs —
only Homebrew/WinGet/apt/dnf/apk installs skip this. `install-claude-code.yml`
downloads the binary directly via `get_url` against the pinned
`claude_code_version`, which bypasses the native installer's
versioned-directory layout but not the binary's own baked-in auto-update
behavior. Left unconstrained, the running `claude` version could silently
drift away from the pinned default the next time a user launches it —
defeating the explicit-pin-controlled-only-by-`perform-updates.yml` model
this project applies to every pinned tool.

The auto-update-disable settings.json keys (`DISABLE_AUTOUPDATER`,
`DISABLE_UPDATES`) are set by `claude_code_config`, since they live in
`~/.claude/settings.json` — see that role's `DESIGN.md`.

## Install-only scope: no `~/.claude` opinionation

This role installs only the binary, its OS package prerequisites (`jq`,
`git`, `curl`), and the `PATH` entry. It deliberately does not create or
write into `~/.claude` in any way, so a host can have Claude Code installed
without any global configuration opinion — the prerequisite for an
install-only profile. All `~/.claude` configuration (settings.json merge,
plugin installs, skills symlinks, MCP servers, the `omc` CLI) lives in the
separate `claude_code_config` role, which declares this role as a
`meta/main.yml` dependency.
