# OMC Setup — Conductor Prompt

You are the **conductor**. You drive a *second* Claude Code session running in a tmux pane and make it install and verify oh-my-claudecode (OMC). You and that session share the same filesystem, so your final source of truth is the files on disk — **never** the other agent's prose claims.

## Operating principles (read first)

1. **Verify, don't trust.** The inner agent can claim success while being wrong, or warn about a non-problem. After it finishes, you independently check artifacts on disk (Step 6). Its summary is a hint, not evidence.
2. **Every wait is bounded.** The inner agent can stall, crash, hit a usage limit, or show an unexpected menu. No loop may run forever — each has a timeout and an abort path (Step 0).
3. **Detect state from UI chrome, not generated words.** Claude Code invents new spinner verbs constantly (`Cogitated`, `Razzmatazzing`, …). Do not match verbs. Match stable chrome instead (Step 0).
4. **Two-call rule for ALL TUI input.** `send-keys 'text' Enter` in one call does not submit. Send text, then a bare `Enter`, as separate calls. (Plain shell commands, outside the Claude TUI, may use the combined form.)

## Step 0 — Primitives

**The pane id must be hardcoded into every block.** Your Bash tool calls do *not* share shell state — an env var set in one call is empty in the next. So you cannot rely on `$PANE` persisting. Step 1 prints the pane id once (a stable token like `%3`); from then on **substitute that literal id** wherever a block shows `PANE=%3` or `-t "$PANE"`. Do not guess `session:win.pane`; use the `%N` id.

**State signals (wording-independent):**
- **Busy** (a turn is running): footer line contains `esc to interrupt`.
- **Idle** (turn ended, input box ready): footer contains `⏵⏵ bypass permissions` but **not** `esc to interrupt`.
- **Shell returned** (Claude exited): no `❯` box and no `bypass permissions` footer; a shell prompt like `…$ ` is present.
- **Abort conditions** (anywhere in output): `usage limit`, `limit reached`, `Invalid API key`, `authentication`, `rate limit`, `Press any key`, or an unexpected `(y/n)` you cannot safely answer.

**Always capture with scrollback** so output that scrolled off is still seen: `tmux capture-pane -t "$PANE" -p -S -200`.

**`wait_idle` — submit happened, now block until the turn ends. Two-phase (busy must appear, then clear) and bounded.** Run as a single Bash call (internal `sleep` is allowed; chained `sleep N && cmd` is not). Replace `%3` with the real pane id:

```bash
PANE=%3
start_deadline=$(( $(date +%s) + 30 ))      # busy must appear within 30s of submit (fresh restarts load hooks/skills and can take >15s)
idle_deadline=$(( $(date +%s) + 600 ))      # then idle within 10 min
saw_busy=0; result=PENDING
while :; do
  pane=$(tmux capture-pane -t "$PANE" -p -S -200)
  if echo "$pane" | grep -qiE "usage limit|limit reached|invalid api key|authentication|rate limit"; then result=ABORT; break; fi
  if echo "$pane" | grep -q "esc to interrupt"; then saw_busy=1
  elif [ "$saw_busy" = 1 ]; then result=IDLE; break; fi
  now=$(date +%s)
  if [ "$saw_busy" = 0 ] && [ "$now" -ge "$start_deadline" ]; then result=NOSTART; break; fi
  [ "$now" -ge "$idle_deadline" ] && { result=TIMEOUT; break; }
  sleep 2
done
echo "$result"
```

- `IDLE` → turn finished cleanly; inspect output and proceed.
- `NOSTART` → busy never appeared, so the `Enter` did not submit. Send one more bare `Enter`, then re-run `wait_idle` **once**. If it returns `NOSTART` again, treat as stuck and report.
- `TIMEOUT` → busy started but never cleared within 10 min; capture the full pane, report to the user, stop. Do not loop again.
- `ABORT` → capture the offending line, report to the user, stop.

## Step 1 — Launch

This is the **only** place a pane is created. The `echo "$PANE"` prints the id (e.g. `%3`) — record it and substitute it literally into every later block:

```bash
PANE=$(tmux split-window -h -P -F '#{pane_id}'); echo "$PANE"
tmux send-keys -t "$PANE" 'claude --dangerously-skip-permissions' Enter
```

Wait until the welcome banner and an empty `❯` box are visible (substitute the real id for `%3`):

```bash
PANE=%3
deadline=$(( $(date +%s) + 60 ))
until tmux capture-pane -t "$PANE" -p | grep -q "bypass permissions"; do
  [ "$(date +%s)" -ge "$deadline" ] && { echo "BANNER_TIMEOUT"; break; }
  sleep 2
done
```

## Step 2 — Send setup prompt

Clear any stray buffer first, then type, then submit. **Clearing the input control needs two `Escape` presses with a short gap** — a single Escape does not reliably clear it:

```bash
tmux send-keys -t "$PANE" Escape; sleep 0.3; tmux send-keys -t "$PANE" Escape
tmux send-keys -t "$PANE" 'run omc setup, install globally, configure suggested defaults, skip MCP configuration. The caveman plugin is also installed and active. Configure the HUD statusline so that the caveman mode badge appears last in the status line.'
tmux send-keys -t "$PANE" '' Enter
```

Then run `wait_idle` (Step 0).

## Step 3 — Monitor through to completion

The setup runs several turns. After each `wait_idle` returns `IDLE`, decide:

- **Interactive menu present** (`Select`/`Choose`/`Which`/`[1]`/`(y/n)` and the input box is *not* a plain empty `❯`): inspect the options. Prefer the pre-highlighted/default choice — usually just a bare `Enter` — over guessing a number. For a yes/no that matches the requested defaults (e.g. overwrite CLAUDE.md, which the script backs up), send `y`. If a menu is genuinely ambiguous or could misconfigure, **stop and ask the human** rather than guess. After answering, run `wait_idle` again.
- **`Setup complete` (or equivalent success summary) visible** in `capture-pane -S -200`: proceed to Step 4.
- **Neither, but idle**: the agent may be between turns or waiting on you. Re-capture; if it asked a question, answer it; otherwise nudge with a bare `Enter` and `wait_idle` once more.

Do not rely on the literal string `Setup complete` alone — Step 6 is the real gate.

**Before proceeding to Step 4**, verify that setup actually finished by checking two artifacts on disk:

```bash
grep -q "<!-- OMC:START -->" ~/.claude/CLAUDE.md && echo "CLAUDE.md: ok" || echo "CLAUDE.md: MISSING — do not proceed"
test -f ~/.claude/.omc-config.json && echo "omc-config: ok" || echo "omc-config: MISSING — nudge needed"
```

If `omc-config` is MISSING, the setup did not reach its final phase (it saves progress mid-run and can go idle before writing the config). Nudge the inner agent:

```bash
tmux send-keys -t "$PANE" 'finalize omc setup — create .omc-config.json if the setup is otherwise complete'
tmux send-keys -t "$PANE" '' Enter
```

Run `wait_idle`, re-run the check, then proceed to Step 4 once both show `ok`.

## Step 4 — Restart to activate the HUD

The HUD statusline only takes effect on a fresh start. Exit cleanly — the agent often leaves a follow-up suggestion typed in, so clear the buffer with **two** `Escape` presses first:

```bash
tmux send-keys -t "$PANE" Escape; sleep 0.3; tmux send-keys -t "$PANE" Escape
tmux send-keys -t "$PANE" '/exit'
tmux send-keys -t "$PANE" '' Enter
```

Wait for the shell to return (Claude UI gone), bounded:

```bash
PANE=%3
deadline=$(( $(date +%s) + 60 ))
until ! tmux capture-pane -t "$PANE" -p | grep -q "bypass permissions"; do
  [ "$(date +%s)" -ge "$deadline" ] && { echo "EXIT_TIMEOUT"; break; }
  sleep 1
done
```

Restart (shell command — single call is fine):

```bash
tmux send-keys -t "$PANE" 'claude --dangerously-skip-permissions' Enter
```

Wait for the banner again (reuse the Step 1 wait).

## Step 5 — Run doctor

```bash
tmux send-keys -t "$PANE" 'run omc doctor'
tmux send-keys -t "$PANE" '' Enter
```

Run `wait_idle`, then capture the report:

```bash
tmux capture-pane -t "$PANE" -p -S -200
```

Note whether it reports `HEALTHY` / `DEGRADED` / `CRITICAL`.

## Step 6 — Independent verification (do not skip)

This is the real success gate. You run these yourself, against the shared filesystem — they do not depend on what the inner agent said:

```bash
# OMC installed in global CLAUDE.md
grep -q "<!-- OMC:START -->" ~/.claude/CLAUDE.md && echo "CLAUDE.md: OMC ok" || echo "CLAUDE.md: MISSING"
# Pre-existing import preserved (the inner agent has falsely warned this was lost)
grep -q "@RTK" ~/.claude/CLAUDE.md && echo "RTK: preserved" || echo "RTK: CHECK backup"
# statusLine wired up and caveman badge appears last in live output
# (inner agent may use a wrapper script — test live output, not the command string)
{ jq -r '.statusLine.command' ~/.claude/settings.json 2>/dev/null | grep -q "caveman" \
  || sh -c "$(jq -r '.statusLine.command' ~/.claude/settings.json 2>/dev/null)" 2>/dev/null | grep -q "CAVEMAN"; } \
  && echo "statusLine: caveman-last ok" || echo "statusLine: CHECK"
# config + HUD artifacts exist
test -f ~/.claude/.omc-config.json && echo "omc-config: ok" || echo "omc-config: MISSING"
ls ~/.claude/hud/*.mjs >/dev/null 2>&1 && echo "HUD: installed" || echo "HUD: MISSING"
```

Confirm the live statusline in the running pane shows the OMC segment first and the caveman badge last (e.g. `[OMC#...L] | ... [CAVEMAN]`).

## Step 7 — Report

Summarize to the user: doctor verdict **plus** your independent Step 6 results. If any check failed or any wait returned `TIMEOUT`/`ABORT`, say so explicitly with the captured evidence — do not soften a partial result into "done".

## Constraints

- **Two-call rule for ALL Claude Code TUI input** (prompts, commands, confirmations): text call, then bare `Enter` call. Shell commands outside the TUI may use the combined form.
- **Never poll with `sleep N && cmd` chained in one Bash call** — the harness blocks it. Use a single Bash call containing a `while`/`until` loop with an internal `sleep` (as in Step 0).
- **Shell state does not persist between your Bash calls.** Hardcode the literal pane id (`%N` from Step 1) into every block; do not depend on `$PANE` surviving from an earlier call.
- **Every wait is bounded** with a deadline and a defined abort/escalate path. Never loop unconditionally.
- **Detect state from chrome** (`esc to interrupt`, `bypass permissions`), not from spinner verbs or specific summary wording.
- **Clear the input buffer with two `Escape` presses** (short gap between, e.g. `Escape; sleep 0.3; Escape`) before typing into the TUI — a single Escape does not reliably clear it, and you would concatenate onto stray text.
- **Trust the filesystem over the inner agent.** Its claims and warnings (especially "you lost X") can be wrong; verify in Step 6.
- Do not use `/omc` slash commands to start setup; plain text triggers the hook chain that loads the skills.
- The HUD statusline activates only after a full restart, not mid-session.
- Capture with `-S -200` so output that scrolled off the visible region is still inspected.
