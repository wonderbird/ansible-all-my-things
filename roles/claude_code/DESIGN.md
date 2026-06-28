<!-- SPDX-License-Identifier: MIT-0 -->

# claude_code role — Design Notes

## Skills symlinks: pure Ansible over the repo's shell script

`eudicy/ai-agent-workspace` ships `scripts/create-skills-links-in-home.sh`,
which creates `~/.claude/skills/<name>` symlinks into the repo clone. The role
uses `ansible.builtin.find` + `ansible.builtin.file state: link` instead of
calling that script via `ansible.builtin.command`.

Reason: Principle I prefers built-in modules over shell tasks. `file state: link`
reports `changed` only when a symlink is actually created; a `command` task
requires a `changed_when` guard keyed on the script's stdout format, coupling
correctness to the upstream script's output — a silent regression risk if
upstream ever changes the log line. The pure-Ansible approach is self-contained
and idempotent without coupling to external stdout.

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
