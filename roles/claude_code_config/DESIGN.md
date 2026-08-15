<!-- SPDX-License-Identifier: MIT-0 -->

# claude_code_config role — Design Notes

## Skills symlinks: pure Ansible over the repo's shell script

`eudicy/ai-agent-workspace` ships `scripts/create-skills-links-in-home.sh`,
which creates `~/.claude/skills/<name>` symlinks into the repo clone. The role
uses `ansible.builtin.find` + `ansible.builtin.file state: link` instead of
calling that script via `ansible.builtin.command`.

Reason: Constitution Principle I prefers built-in modules over shell tasks.
`file state: link` reports `changed` only when a symlink is actually created;
a `command` task requires a `changed_when` guard keyed on the script's stdout
format, coupling correctness to the upstream script's output — a silent
regression risk if upstream ever changes the log line. The pure-Ansible
approach is self-contained and idempotent without coupling to external
stdout.

The `find` result is checked with `assert matched > 0` per user to fail loudly
if the clone is empty or the `.claude/skills` directory is absent (Principle XII).

## Plugin idempotency: explicit existence checks before `claude plugin` calls

`ansible.builtin.shell` tasks for marketplace registration and plugin installation
are guarded by prior `claude plugin marketplace list` and `claude plugin list`
checks. The `claude plugin` commands are not idempotent — re-running them against
an already-registered marketplace or installed plugin produces an error.
`changed_when` is not applicable here; the guards prevent the task from running
when not needed.

## settings.json: jq merge, not template

`configure.yml` merges required keys into `settings.json` with `jq` rather than
deploying a template. The file may contain user-managed keys that a template
would overwrite. The jq script detects whether the target state already exists
and prints `NO_CHANGE` or `CHANGED`, which `changed_when` uses to report
accurately.

## Why auto-update is disabled

Unlike `rtk`/`beads`/`nodejs`, which have no self-update mechanism, the
Claude Code binary itself checks for and installs updates in the background
(on startup and periodically) by default for native/npm-style installs —
only Homebrew/WinGet/apt/dnf/apk installs skip this. `claude_code`'s
`install-claude-code.yml` downloads the binary directly via `get_url` against
the pinned `claude_code_version`, which bypasses the native installer's
versioned-directory layout but not the binary's own baked-in auto-update
behavior. Left unconstrained, the running `claude` version could silently
drift away from the pinned default the next time a user launches it —
defeating the explicit-pin-controlled-only-by-`perform-updates.yml` model
this project applies to every pinned tool.

`configure.yml` sets both `DISABLE_AUTOUPDATER=1` (stops the background
update check) and `DISABLE_UPDATES=1` (also blocks manual `claude update`/
`claude install`, the stronger guarantee) in `settings.json`'s `env` key, so
the pinned version can only change via `perform-updates.yml`.

## settings.json: bd-guard hook via jq --arg

The bd-guard `PreToolUse` hook blocks `bd list --all`, which enters an unbounded
output loop at ~350 issues in this repo (5.6 GB output, 100% CPU, SIGKILL).

The hook command contains embedded single quotes (shell guards, jq calls, the
JSON error payload), making it impossible to embed literally inside a jq
expression that is itself single-quoted in bash. `configure.yml` therefore
assigns the command string via a quoted heredoc (`<<'HOOKEOF'`) to a
`BD_HOOK_CMD` variable and passes it to jq as `--arg bdcmd "$BD_HOOK_CMD"`.
The jq expression references `$bdcmd` without quoting issues.

The idempotency check uses `.command | contains("bd list --all")` rather than an
exact string match so that minor future rewrites of the hook command do not cause
duplicate entries.

The hook uses `grep -qE '(^|[[:space:]])(bd)[[:space:]]+list[[:space:]]+--all'`
so it only fires when `bd` appears at the start of the command or after
whitespace. This avoids false positives when the literal string
`bd list --all` appears inside a grep argument (`grep -qF 'bd list --all'`)
or a jq expression (`contains("bd list --all")`), where `bd` is preceded
by a quote character, not whitespace.

## Why the omc CLI install lives here, not in its own role

`omc` (oh-my-claudecode) is itself an orchestration layer built specifically
for Claude Code sessions — it has no life outside one, unlike a general
binary such as `rtk` that any harness or shell can invoke standalone. The
deciding test: does this concern have any life outside a Claude Code
session? `omc` does not; the settings.json wiring it sits alongside
(`install-omc-cli.yml`, `configure.yml`) does not either.

The Node.js/npm dependency this role's `omc` CLI install needs is provisioned
by the `nodejs` role, declared as a hard `meta/main.yml` dependency (it
unconditionally invokes `npm`, per the decision test in
`docs/architecture/concepts/role-dependency-declaration.md`). This role's own
Molecule `converge.yml` composes `nodejs` alongside it, so a green
`molecule test` validates the real dependency, not an isolated fixture.

## Why `rtk init -g` lives here, not in the `rtk` role

Same test as above, applied to rtk: `rtk`'s binary install genuinely has
life outside a Claude Code session (any harness can shell out to
`/usr/local/bin/rtk`), but `rtk init -g` writes into `~/.claude` — this
role's own config directory, not rtk's install path — and no other harness
reads it. So the binary install stays in the `rtk` role; the
`~/.claude`-targeting init runs here (`configure.yml`), next to the
directory creation and settings.json wiring it belongs with. This role's own
Molecule `converge.yml` composes the `rtk` role so the binary exists before
this task runs.

## Why this is a separate role from `claude_code`

`claude_code` installs the binary only; this role owns every task that
opinionates `~/.claude` (settings.json, plugins, skills symlinks, MCP
servers, the `omc` CLI). The split lets a host install the Claude Code binary
without any global configuration opinion — the prerequisite for an
install-only profile (see `docs/architecture/concepts/role-dependency-declaration.md`
for the dependency-declaration reasoning: this role hard-needs the `claude`
binary from `claude_code`, e.g. `claude plugin`/`claude mcp` calls, so it
declares `claude_code` in `meta/main.yml` `dependencies:` in addition to
explicit play ordering).
