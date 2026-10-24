<!-- SPDX-License-Identifier: MIT-0 -->

# claude_code_config role — Design Notes

## Skills symlinks: pure Ansible over the repo's shell script

`wonderbird/ai-agent-workspace` ships `scripts/create-skills-links-in-home.sh`,
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
if the clone is empty or the `skills` directory is absent (Principle XII).

## Skills in sm: imported, not deployed

The ai-agent-workspace skills are made available in Skill Manager (`sm`) for
every login user, but none is deployed to any tool. The owner activates a
skill deliberately with `sm add`, per project or globally.

The import runs `sm install https://github.com/wonderbird/ai-agent-workspace
--force`. It clones the repository as an `sm` source and imports each skill
into the `sm` store; it creates no deployment link for Claude Code or Codex.

- **Why `--force`**: upstream ai-agent-workspace is the single source of
  truth for these skills. Without `--force`, `sm` prompts before replacing a
  skill whose content changed and, with no terminal, skips it; with it, every
  run refreshes changed skills and overwrites edits made only in the `sm`
  store. `sm source add --install` runs the same import but has no `--force`
  option.
- **Rejected: `sm install` inside a clone**: it applies the repository's
  `.skills.json` manifest, whose entries deploy every skill globally to
  Claude Code and Codex.
- **Rejected: `sm import <dir>`**: it deploys each imported skill to Claude
  Code and Codex.

`sm` prints one line per skill and a summary line naming the source and its
skill count. The count is followed by a parenthesised `installed` or
`updated` tally only when a skill was written, so `changed_when` keys on that
tally; a re-run with no upstream change prints the summary without it.

`sm` reports a skill that failed to import on stdout and still exits 0. A
separate `assert` therefore fails the run when the summary line is missing,
reports zero skills, or any skill failed (Principle XII). It is an `assert`
rather than `failed_when` so the command's own failure test stays intact.

The import depends on the `sm` config the `skill_manager` role deploys: with
auto-adopt left on, every `sm` command would move unmanaged skills from the
working directory and the user's tool directories into the store. The task
also runs from the user's home directory, not from a project checkout.

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

## settings.json: layered on top of claude_code's baseline

`claude_code`'s own `configure.yml` creates `~/.claude` and writes
`DISABLE_AUTOUPDATER`/`DISABLE_UPDATES` before this role ever runs (hard
`meta/main.yml` dependency, see "Why this is a separate role" below). See
`claude_code/DESIGN.md`'s "Why auto-update is disabled" for that rationale —
those two keys are general and safe for any project, so they are not this
role's concern. This role's own jq merge in `configure.yml` only adds its
own opinionated keys (agent-team env vars, `teammateMode`, the rtk/bd-guard
hooks) on top of the file `claude_code` already created, using the same
read-current-merge-write pattern so neither role's keys clobber the other's.

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
`/usr/local/bin/rtk`), but `rtk init -g` writes into `~/.claude` — an
opinionated choice to use rtk at all, not something every Claude Code
install needs — and no other harness reads it. So the binary install stays
in the `rtk` role; the `~/.claude`-targeting init runs here (`configure.yml`),
next to the settings.json wiring it belongs with. This role's own Molecule
`converge.yml` composes the `rtk` role so the binary exists before this task
runs.

## Why this is a separate role from `claude_code`

`claude_code` installs the binary and writes only the two settings.json keys
that protect its own version-pin contract (general and safe for any
project); this role owns every task that is a specific, opinionated choice
for sophisticated development (settings.json's agent-team/hook keys,
plugins, skills symlinks, MCP servers, the `omc` CLI, `rtk init -g`). The
split lets a host install the Claude Code binary with only the minimal
version-pin protection, leaving every actual usage decision open — the
prerequisite for an install-only profile (see
`docs/architecture/concepts/role-dependency-declaration.md` for the
dependency-declaration reasoning: this role hard-needs the `claude` binary
from `claude_code`, e.g. `claude plugin`/`claude mcp` calls, and needs
`claude_code`'s `configure.yml` to have already created `~/.claude` and
written the baseline settings.json, so it declares `claude_code` in
`meta/main.yml` `dependencies:` in addition to explicit play ordering).
