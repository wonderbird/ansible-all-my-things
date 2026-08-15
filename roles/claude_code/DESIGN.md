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

`configure.yml` sets both `DISABLE_AUTOUPDATER=1` (stops the background
update check) and `DISABLE_UPDATES=1` (also blocks manual `claude update`/
`claude install`, the stronger guarantee) in `settings.json`'s `env` key, so
the pinned version can only change via `perform-updates.yml`.

## Minimal `~/.claude` footprint: general and safe, not opinionated

This role's `configure.yml` creates `~/.claude` and writes only the two
auto-update-disable keys above — nothing else. The boundary test: does this
setting protect a guarantee `claude_code` itself makes (the version pin), or
is it a choice about *how* to use Claude Code (which plugins, which agent
workflow, which companion tools)? Only the former belongs here. Every
opinionated setting.json key (agent-team env vars, `teammateMode`, the
rtk/bd-guard hooks), plugin install, skills symlink, and MCP server
configuration is a specific tool choice for sophisticated development and
lives in the separate `claude_code_config` role instead, which layers its
own `configure.yml` merge onto the same `settings.json` file after this
role has run (see that role's `DESIGN.md`).

This keeps a host able to install Claude Code with only the minimum
configuration needed to protect its own version pin — the prerequisite for
an install-only profile — while still leaving every actual usage decision
open.
