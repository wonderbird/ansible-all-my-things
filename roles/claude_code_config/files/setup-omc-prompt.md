# OMC Setup — Conductor Prompt

You are the **conductor**. You drive a *second* Claude Code session running in a tmux pane and make it install and verify oh-my-claudecode (OMC). You and that session share the same filesystem, so your final source of truth is the files on disk — **never** the other agent's prose claims.

## Operating principles (read first)

1. **Verify, don't trust.** The inner agent can claim success while being wrong, or warn about a non-problem. After it finishes, you independently check artifacts on disk (Step 6). Its summary is a hint, not evidence.
2. **Every wait is bounded.** The inner agent can stall, crash, hit a usage limit, or show an unexpected menu. No loop may run forever — each has a timeout and an abort path (Step 0). A single Bash-tool call cannot be timed out past **600000ms (10 min) — this is a hard ceiling the harness enforces**, not a suggestion. Every bounded loop below keeps its *internal* deadline comfortably under that ceiling and chains additional bounded waits if genuinely still progressing, rather than requesting one long call that risks colliding with the hard cap (Step 0, `wait_idle`).
3. **Detect state from UI chrome, not generated words.** Claude Code invents new spinner verbs constantly (`Cogitated`, `Razzmatazzing`, …). Do not match verbs. Match stable chrome instead (Step 0).
4. **Two-call rule for ALL TUI input.** `send-keys 'text' Enter` in one call does not submit. Send text, then a bare `Enter`, as separate calls. (Plain shell commands, outside the Claude TUI, may use the combined form.)
5. **Never send a key into the TUI immediately after another key changed its state.** Escape (clearing), typing, and Enter (submitting) each trigger a render/reconciliation pass in the Ink-based UI. Sending the next key before that pass settles is how input gets silently swallowed — a real failure mode, not a hypothetical: a bare `Escape` clear directly preceding text-entry has dropped the text's first character, and text-entry directly preceding `Enter` has swallowed the `Enter` (typing `/exit` opened the slash-command autocomplete dropdown, which absorbed the first `Enter` as a menu action rather than a submit). Fix: put a short settle delay (`sleep 0.4`) after every discrete TUI keystroke action, and verify the visible result before trusting it (Step 0, "Reliable TUI text entry").
6. **A second `Escape` on an already-empty input box can open a `Rewind` (checkpoint restore) menu instead of clearing anything** — observed in practice, not hypothetical. This is destructive if confirmed. After any `Escape`, capture the pane and check for `Rewind`/`Restore` chrome before proceeding; if seen, press `Escape` again to cancel and **never** press `Enter` on it.
7. **Text visible in the input box after a turn ends is routinely an inert placeholder, not real buffer content** — this is not a rare edge case: it surfaced on *every* idle turn-end in one full run (Claude Code auto-populating a suggested next command), and survived both `Escape` and `Ctrl-U` untouched. Don't assume "text is visible" means "text is staged to submit," but don't spend a verification round-trip on it either — the normal clear/type/verify flow (Step 0) already overwrites it safely every time. Just type your own command directly; only stop to investigate if the type-verify loop itself fails.

## Step 0 — Primitives

**The pane id must be hardcoded into every block.** Your Bash tool calls do *not* share shell state — an env var set in one call is empty in the next. So you cannot rely on `$PANE` persisting. Step 1 prints the pane id once (a stable token like `%3`); from then on **substitute that literal id** wherever a block shows `PANE=%3` or `-t "$PANE"`. Do not guess `session:win.pane`; use the `%N` id. Also derive a per-pane scratch filename by stripping the leading `%` (e.g. pane `%3` → `/tmp/omc-presnap-3.txt`) and substitute that literally too — shell state doesn't persist between calls, so this file (not a variable) is how a "before" snapshot survives from one Bash call to the next.

**State signals (wording-independent):**
- **Busy** (a turn is running): footer line contains `esc to interrupt` **or** a spinner status line matching `· ↓ .*tokens` (e.g. `✶ Levitating… (1m 21s · ↓ 5.2k tokens · thinking)`). **Claude Code v2.1.207 never displayed `esc to interrupt` at all during a full observed run** — the spinner line was the only busy chrome. Treat the two as alternates; require neither one specifically.
- **Idle** (turn ended, input box ready): **no** busy signal (neither `esc to interrupt` nor a `· ↓ .*tokens` spinner line) **and** the captured pane content is byte-identical across **2–3 consecutive polls** (see `wait_idle` below). Content stability is the version-proof condition — make it required, not a fallback: in the observed run, absence-of-`esc to interrupt` alone produced a false `IDLE` while the inner agent was still mid-work.
- **Shell returned** (Claude exited): no `❯` box and no `bypass permissions` footer; a shell prompt like `…$ ` is present.
- **Abort conditions** (anywhere in output): `usage limit exceeded`, `limit reached`, `invalid api key`, `please...authenticat`, `rate limit exceeded`, `Press any key`, or an unexpected `(y/n)` you cannot safely answer. Use full phrases, not bare words like `authentication`/`rate limit` — those match ordinary scrollback (e.g. a plugin-update notice) and produce false `ABORT`s, observed in practice. **Extra reason once setup succeeds**: the newly installed HUD statusline renders *inside the monitored pane's footer* — usage-percent bars, a `[CAVEMAN]` badge line, and similar text — so any grep over the pane must tolerate that footer noise; full-phrase matching is what keeps it from tripping abort or badge checks.

**Always capture with scrollback** so output that scrolled off is still seen: `tmux capture-pane -t "$PANE" -p -S -200`.

### Reliable TUI text entry

Clearing and typing raced in practice (first character dropped). Don't just delay-and-hope — delay *and* verify the pane actually shows what you typed before you trust it enough to submit. Replace `%3` with the real pane id and `TEXT` with the literal prompt:

```bash
PANE=%3
TEXT='run omc setup, install globally, configure suggested defaults. The caveman plugin is also installed and active, but do not configure its statusline badge. Ignore any caveman STATUSLINE SETUP NEEDED or STATUSLINE REPAIR NEEDED message and do not offer to act on it: the statusline is composed separately after setup finishes. Leave statusLine exactly as the OMC HUD setup writes it.'
clear_input() {
  tmux send-keys -t "$PANE" Escape; sleep 0.4
  tmux capture-pane -t "$PANE" -p -S -5 | grep -qi "rewind\|restore" && { tmux send-keys -t "$PANE" Escape; sleep 0.4; }
}
clear_input
tmux send-keys -t "$PANE" -l "$TEXT"
sleep 0.4
attempt=0
while ! tmux capture-pane -t "$PANE" -p | tr '\n' ' ' | grep -qF "${TEXT:0:24}"; do
  attempt=$((attempt+1))
  if [ "$attempt" -ge 3 ]; then echo "TYPE_VERIFY_FAILED — capture pane and inspect manually"; break; fi
  clear_input
  tmux send-keys -t "$PANE" -l "$TEXT"
  sleep 0.4
done
echo "typed ok (attempt $attempt)"
```

`-l` sends the text literally (no tmux key-name interpretation). Checking the first 24 characters is enough to catch a dropped leading character without being thrown off by line-wrap inside the input box. If `TYPE_VERIFY_FAILED` prints, stop and inspect — don't submit unverified text.

Then, in a **separate** call (two-call rule), snapshot the pane and submit:

```bash
PANE=%3
tmux capture-pane -t "$PANE" -p -S -50 > /tmp/omc-presnap-3.txt
tmux send-keys -t "$PANE" '' Enter
```

The snapshot feeds the `NOSTART` aliasing guard in `wait_idle` below.

**For slash commands specifically** (text starting with `/`, e.g. `/exit`): send `Enter` twice, with a settle gap, proactively — the autocomplete dropdown that a slash command opens can consume the first `Enter` as a selection rather than a submit, and waiting for `wait_idle` to time out and tell you that wastes a full detection cycle:

```bash
PANE=%3
tmux capture-pane -t "$PANE" -p -S -50 > /tmp/omc-presnap-3.txt
tmux send-keys -t "$PANE" '' Enter
sleep 0.5
tmux send-keys -t "$PANE" '' Enter
```

### `wait_idle` — submit happened, now block until the turn ends

Two-phase (busy must appear, then clear) and bounded, with three hardening fixes over a naive version:
- **Version-proof busy detection**: busy = `esc to interrupt` **or** a `· ↓ .*tokens` spinner line, and idle additionally requires the captured pane to be byte-identical across consecutive polls. v2.1.207 shipped without `esc to interrupt` entirely; a loop keyed on that string alone declares `IDLE` while the agent is still working.
- **Debounce**: idle is only declared after 2–3 consecutive clean *and content-stable* polls — a single-poll miss of busy chrome between chained tool calls inside one long agent turn is normal and must not be read as "done."
- **Aliasing guard on `NOSTART`**: if busy chrome is never seen within the start budget, don't assume the `Enter` failed — it's also possible the whole turn ran and finished faster than the poll cadence caught it (this happened with a short `omc doctor` run). Diff the current pane against the presubmit snapshot; if content moved, treat it as `IDLE`, not `NOSTART`.
- **Deadline margin**: keep the internal `idle_deadline` at 540s (9 min) — comfortably under the Bash tool's hard 600000ms ceiling — and request a Bash-tool `timeout` of ~595000ms for the call. Never set the two equal; a prior run set both to exactly 600s/600000ms and the harness's own kill won the race, silently discarding the script's own `TIMEOUT`/result line.

Run as a single Bash call (internal `sleep` is allowed; chained `sleep N && cmd` is not), with the Bash tool's own `timeout` param set to `595000`. Replace `%3` with the real pane id and `/tmp/omc-presnap-3.txt` with its snapshot file:

```bash
PANE=%3
PRESNAP=/tmp/omc-presnap-3.txt
poll=1
start_budget=30          # busy must appear within 30s of submit (fresh restarts load hooks/skills and can take >15s)
idle_budget=540          # then idle within 9 min — stays under the Bash tool's 600000ms hard cap with margin
start_deadline=$(( $(date +%s) + start_budget ))
idle_deadline=$(( $(date +%s) + idle_budget ))
saw_busy=0; idle_streak=0; required_streak=3; result=PENDING; prev=""
while :; do
  pane=$(tmux capture-pane -t "$PANE" -p -S -200)
  if echo "$pane" | grep -qiE "usage limit exceeded|limit reached|invalid api key|please.*authenticat|rate limit exceeded"; then result=ABORT; break; fi
  if echo "$pane" | grep -q "esc to interrupt" || echo "$pane" | grep -qE '· ↓ .*tokens'; then
    saw_busy=1; idle_streak=0
  elif [ "$saw_busy" = 1 ] && [ "$pane" = "$prev" ]; then
    idle_streak=$((idle_streak+1))
    [ "$idle_streak" -ge "$required_streak" ] && { result=IDLE; break; }
  else
    idle_streak=0
  fi
  prev="$pane"
  now=$(date +%s)
  if [ "$saw_busy" = 0 ] && [ "$now" -ge "$start_deadline" ]; then
    if [ -f "$PRESNAP" ] && ! diff -q <(tmux capture-pane -t "$PANE" -p -S -50) "$PRESNAP" >/dev/null 2>&1; then
      result=IDLE   # pane content moved even though "esc to interrupt" was never caught — trust the diff over the miss
    else
      result=NOSTART
    fi
    break
  fi
  [ "$now" -ge "$idle_deadline" ] && { result=TIMEOUT; break; }
  sleep "$poll"
done
echo "$result"
```

- `IDLE` → turn finished cleanly; inspect output and proceed.
- `NOSTART` → the aliasing guard already ruled out "it actually ran," so the `Enter` really didn't land. Send one more bare `Enter`, then re-run `wait_idle` **once** (refresh `PRESNAP` first). If it returns `NOSTART` again, treat as stuck and report — don't keep sending blind `Enter`s, since if a menu is open for an unrelated reason a stray `Enter` can select something unintended.
- `TIMEOUT` → busy started but didn't clear within 9 min. Capture the pane: if `esc to interrupt` is still present, this may be a genuinely long step (cold plugin/npm install) rather than a hang — re-run `wait_idle` again, up to **3 chained calls total** (~27 min combined) before giving up. If pane content is byte-identical to a capture taken a poll or two earlier while chrome still claims busy, that's a frozen render, not slow progress — stop chaining and report immediately.
- `ABORT` → capture the offending line, report to the user, stop.

## Step 1 — Launch

This is the **only** place a pane is created. `split-window` targets whatever tmux session is current — no need to create or attach a session first, an existing attached session is fine. But **no tmux server running at all is a real, observed failure mode** (`error connecting to /tmp/tmux-1001/default (No such file or directory)`), not just a hypothetical — `split-window` has nothing to target. Bootstrap a session first if none exists:

```bash
tmux has-session 2>/dev/null || tmux new-session -d -s omc-boot -x 220 -y 50
```

The `echo "$PANE"` prints the id (e.g. `%3`) — record it and substitute it literally into every later block:

```bash
PANE=$(tmux split-window -h -P -F '#{pane_id}'); echo "$PANE"
tmux send-keys -t "$PANE" 'claude --dangerously-skip-permissions' Enter
```

Record the run start time once, so Step 3 can tell this run's `setupCompleted` marker from one left by an earlier setup (substitute the real id in the filename, as for the snapshot file):

```bash
date +%s > /tmp/omc-runstart-3.txt
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

Use the **Reliable TUI text entry** pattern from Step 0: clear with the guarded `clear_input` (Escape, then cancel `Rewind` if it appears), type with `-l` and verify the first 24 characters actually landed, then in a separate call snapshot the pane and submit with `Enter`.

Then run `wait_idle` (Step 0) with Bash-tool `timeout: 595000`.

## Step 3 — Monitor through to completion

The setup runs several turns. After each `wait_idle` returns, decide:

- **`IDLE` + interactive menu present** (`Select`/`Choose`/`Which`/`[1]`/`(y/n)` and the input box is *not* a plain empty `❯`): inspect the options. Prefer the pre-highlighted/default choice — usually just a bare `Enter` — over guessing a number. For a yes/no that matches the requested defaults (e.g. overwrite CLAUDE.md, which the script backs up), send `y`. If a menu is genuinely ambiguous or could misconfigure, **stop and ask the human** rather than guess. After answering, run `wait_idle` again (refresh `PRESNAP` first). The setup agent may also auto-answer a menu from the prompt text, or batch several questions into one multi-question form; answer each question, then confirm the form's submit step. Don't wait for a menu that never appears. Known menus, in the order setup asks them (OMC 5.6.1):

  | Menu (question text) | When it appears | Answer |
  |---|---|---|
  | "OMC is already configured. What would you like to do?" | Re-run on a machine where `.omc-config.json` has `setupCompleted` | `Run full setup again`. The quick-update option skips the HUD, teams and the later phases. |
  | "Found a previous setup session. Would you like to resume or start fresh?" | An earlier run was interrupted | `Start fresh` |
  | "Where should I configure oh-my-claudecode?" | Setup did not take "install globally" from the prompt | `Global (all projects)` |
  | "Global setup will change your base Claude config" | Base `CLAUDE.md` exists without OMC markers (observed every fresh install) | `1. Overwrite base CLAUDE.md (Recommended)`. It backs up the old file first and is normally pre-highlighted. |
  | "Task management tool for OMC to use?" | `bd` or `br` is on `PATH` | `1. Built-in Tasks (Default)`. It is pre-highlighted, so a bare `Enter` picks it. |
  | "Would you like to install the OMC CLI globally…?" | `omc` is not on `PATH` | `Yes (Recommended)` |
  | "Would you like to enable agent teams?" | Always (Phase 3) | `Yes, enable teams (Recommended)` |
  | "How should teammates be displayed?" | Teams were enabled | `Auto (Recommended)`. See the tmux note below. |
  | "How many agents should teams spawn by default?" / "Which CLI provider should teammates use by default?" | Teams were enabled | `3 agents (Recommended)` / `claude (Recommended)` |
  | "…would you like to support the project by starring it on GitHub?" | `gh` is logged in and the repo is not starred yet | `No thanks`. Starring acts on the human's GitHub account, so never choose it without their explicit consent. |

  **tmux note on teammate display.** Inside tmux, `Auto` resolves to split panes, the same as choosing `tmux`. This machine also sets `CLAUDE_CODE_SPAWN_BACKEND=tmux` in `settings.json`. Setup itself spawns no teammates, and every block here targets the literal `%N` pane id, so the run is not affected. A later `/team` run inside the driven pane, however, splits the conductor's own tmux window and shrinks the monitored pane. Do not start teams in the driven pane while a conductor is monitoring it.
- **`IDLE` + `Setup complete` (or equivalent success summary) visible** in `capture-pane -S -200`: run the gate below, then proceed to Step 3b.
- **`IDLE`, neither of the above**: the agent may be between turns or waiting on you. Re-capture; if it asked a question, answer it; otherwise nudge with a bare `Enter` and `wait_idle` once more.
- **`TIMEOUT`**: follow the chaining rule from Step 0 — keep waiting (up to 3 chained calls) only while pane content is still visibly moving; stop and report if it's static.
- **`NOSTART`**: follow Step 0's guard — this already accounted for "it actually finished fast," so a real `NOSTART` here means the prompt genuinely didn't submit. Retry once as described, then report if it recurs.

Do not rely on the literal string `Setup complete` alone — Step 6 is the real gate.

**Before proceeding to Step 3b**, verify that setup actually finished by checking artifacts on disk. Gate on `.omc-config.json` containing **`setupCompleted`**, not on the file merely existing. In OMC 5.6.1 setup writes the config in stages: `taskTool` in Phase 2 (only when a beads tool is on `PATH`), `team` in Phase 3, and `setupCompleted` plus `setupVersion` only in the final Phase 4. A bare `test -f` can therefore pass while the last phase is still running. This is exactly what let a prior run advance to Step 4 and `Escape`-interrupt the still-running final phase.

Two more conditions close the remaining gaps. `setupCompleted` must be **newer than the run start** recorded in Step 1, because on a re-run the marker from the previous setup is already present. `setupVersion` must **match the installed plugin version** in Claude Code's registry, because a mismatch means the config was completed by an older OMC:

```bash
grep -q "<!-- OMC:START -->" ~/.claude/CLAUDE.md && echo "CLAUDE.md: ok" || echo "CLAUDE.md: MISSING — do not proceed"
CFG=~/.claude/.omc-config.json
DONE=$(jq -r '.setupCompleted // empty' "$CFG" 2>/dev/null)
START=$(cat /tmp/omc-runstart-3.txt 2>/dev/null || echo 0)
if [ -n "$DONE" ] && [ "$(date -d "$DONE" +%s 2>/dev/null || echo 0)" -ge "$START" ]; then
  echo "omc-config: complete"
elif [ -n "$DONE" ]; then
  echo "omc-config: STALE — setupCompleted ($DONE) predates this run; final phase not reached yet, nudge needed"
elif test -f "$CFG"; then
  echo "omc-config: PARTIAL — file exists but no setupCompleted; final phase still running/incomplete, nudge needed"
else
  echo "omc-config: MISSING — nudge needed"
fi
CFG_V=$(jq -r '.setupVersion // empty' "$CFG" 2>/dev/null)
PLUGIN_V=$(jq -r '.plugins["oh-my-claudecode@omc"][0].version // empty' ~/.claude/plugins/installed_plugins.json 2>/dev/null)
[ -n "$CFG_V" ] && [ "$CFG_V" = "$PLUGIN_V" ] && echo "setupVersion: $CFG_V ok" || echo "setupVersion: CHECK — config ${CFG_V:-(none)} vs plugin ${PLUGIN_V:-(none)}"
```

If `omc-config` is MISSING, PARTIAL **or STALE**, the setup did not reach its final phase in this run. Nudge the inner agent using the same clear/type/verify pattern from Step 0:

```bash
PANE=%3
TEXT='finalize omc setup — complete the final phase so .omc-config.json gets its setupCompleted marker, if the setup is otherwise complete'
tmux send-keys -t "$PANE" Escape; sleep 0.4
tmux capture-pane -t "$PANE" -p -S -5 | grep -qi "rewind\|restore" && { tmux send-keys -t "$PANE" Escape; sleep 0.4; }
tmux send-keys -t "$PANE" -l "$TEXT"
sleep 0.4
tmux capture-pane -t "$PANE" -p | tr '\n' ' ' | grep -qF "${TEXT:0:24}" && echo "typed ok" || echo "TYPE_VERIFY_FAILED"
```

```bash
PANE=%3
tmux capture-pane -t "$PANE" -p -S -50 > /tmp/omc-presnap-3.txt
tmux send-keys -t "$PANE" '' Enter
```

Run `wait_idle`, re-run the check, then proceed to Step 3b once CLAUDE.md shows `ok` and omc-config shows `complete`. **Safety valve:** if after one nudge + `wait_idle` the `setupCompleted` marker still does not appear, but the pane shows a completion summary and the other Step 6 artifacts (HUD, `statusLine`, CLAUDE.md marker) are all present, treat setup as complete and proceed — note it in the Step 7 report rather than looping indefinitely (guards against a future config-schema change that renames the marker).

## Step 3b — Compose the statusline (you do this, after setup)

`settings.json` holds exactly **one** `statusLine.command`. OMC HUD wants it and the caveman badge wants it, and neither ships a way to share it, so a combiner script has to own the slot and call both. **You** install the combiner yourself, directly on the shared filesystem. Do not delegate it to the inner agent: every inner agent that wrote its own combiner reinvented it, and that is where the failures came from. The script below is tested and is installed verbatim.

**Do this only after the Step 3 gate passes, and before the Step 4 restart.** Setup's Phase 2.1 always runs `hud setup`, which resets `statusLine` to the plain `omc-hud.mjs`. A combiner wired while setup is still running is silently overwritten. The Step 4 restart then activates the composed line.

**Resolving the caveman script.** Since caveman 3.1.0, the plugin keeps a **stable copy** of its statusline script at `$CLAUDE_CONFIG_DIR/hooks/caveman-statusline.sh`. Its SessionStart hook creates that copy when it suggests a statusline. On every later session start it refreshes the copy, but only when `statusLine.command` names that path as a literal absolute path. A path written with `~` or `$VAR` is treated as unknown and is not refreshed. The copy has mode `600`, so always run it as `bash <path>`, never execute it directly.

| Source | When | How the combiner uses it |
|---|---|---|
| Stable copy `$CLAUDE_CONFIG_DIR/hooks/caveman-statusline.sh` | It exists (normal case) | Run with `bash`. Its quoted absolute path is an argument in `statusLine.command`, so the caveman hook detects it and keeps it current. |
| Registry `installPath` + `/src/hooks/caveman-statusline.sh` | No stable copy, or the argument path is gone | Resolved **at render time** inside the combiner. Never baked into the script or `settings.json`. |

Never hard-code `installPath`. It contains the version (`.../plugins/cache/caveman/caveman/3.1.0`), so a hard-coded path breaks on the next caveman update. An older copy also renders nothing, because its whitelist does not know the current mode ids. Do **not** resolve by scanning `plugins/cache/caveman/caveman/*` and sorting by `mtime`, and do **not** treat `plugins/marketplaces/caveman/` as an install. The marketplace directory is the git clone that updates are *pulled from*; `claude plugin update` refreshes it before the cache is rebuilt, so an mtime sort can select a copy that is not the plugin Claude Code loads.

**What the combiner must get right** (each one was hit while building it):

- Read stdin **once** and replay the same buffer to both sub-commands. Both read stdin, and the second one gets nothing otherwise.
- Append the badge to the end of the **first** line. The HUD can print several lines (the agent tree in `full`/`multiline` layouts), so "last" means last on the main status line, not after the tree.
- Discard both sub-commands' stderr. The HUD prints diagnostics such as `[worktree] non-git directory provided…` there, and merged stderr would land in the status bar.
- Give each sub-command a timeout and keep whatever it printed before failing, so one stuck script cannot blank the whole line.

### 1. Back up `settings.json` and install the combiner

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak.statusline-$(date +%s)
mkdir -p ~/.claude/hud
cat > ~/.claude/hud/omc-hud-combined.mjs <<'EOF'
#!/usr/bin/env node
// Combined statusline: OMC HUD first, caveman mode badge last.
// settings.json holds one statusLine.command, so this script owns the slot and calls both.
//
// Usage: node omc-hud-combined.mjs "<absolute path to caveman-statusline.sh>"
// The caveman path is passed as an argument so the caveman SessionStart hook can find it
// in statusLine.command and keep that stable copy current. If the argument is missing or
// the file is gone, the path is resolved from Claude Code's plugin registry at render time.
import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const configDir = process.env.CLAUDE_CONFIG_DIR || join(homedir(), '.claude');
const TIMEOUT_MS = 2000;

// Both sub-commands read stdin, so read it once and replay the same buffer to each.
let input = '';
try {
  input = readFileSync(0, 'utf8');
} catch {
  // No stdin (e.g. run from a terminal): render with an empty payload.
}

function run(command, args) {
  const result = spawnSync(command, args, {
    input,
    encoding: 'utf8',
    timeout: TIMEOUT_MS,
    stdio: ['pipe', 'pipe', 'ignore'],
  });
  // Keep partial output from a timed-out or failing sub-command rather than blanking the line.
  return result.stdout || '';
}

function cavemanScript() {
  const fromArg = process.argv[2];
  if (fromArg && existsSync(fromArg)) return fromArg;
  try {
    const registry = JSON.parse(readFileSync(join(configDir, 'plugins', 'installed_plugins.json'), 'utf8'));
    const entries = registry.plugins?.['caveman@caveman'] ?? [];
    const entry = entries.find((e) => e.scope === 'user') ?? entries[0];
    const script = entry && join(entry.installPath, 'src', 'hooks', 'caveman-statusline.sh');
    return script && existsSync(script) ? script : null;
  } catch {
    return null;
  }
}

const hudLines = run(process.execPath, [join(configDir, 'hud', 'omc-hud.mjs')]).replace(/\n+$/, '').split('\n');
const script = cavemanScript();
const badge = script ? run('bash', [script]).trim() : '';

if (badge) {
  // Append to the main status line; any further HUD lines (agent tree) stay below it.
  hudLines[0] = hudLines[0] ? `${hudLines[0]}\x1b[2m | \x1b[0m${badge}` : badge;
}
process.stdout.write(hudLines.join('\n'));
EOF
chmod 755 ~/.claude/hud/omc-hud-combined.mjs
echo "combiner installed"
```

### 2. Verify by executing it, before touching `settings.json`

A missing segment does not throw — the line still renders, just without the badge, which is why this failure survives a casual glance. So verify by *executing* the composed command, never by checking that a file exists.

The badge is per session. The caveman script reads `.caveman-sessions/<session_id>.mode` and falls back to the global `.caveman-active` flag when that file is missing. A check that stages `full` can therefore pass through the global flag even when the combiner drops the session id. Stage a throwaway session with a mode that the global flag is unlikely to hold (`review` renders `[CAVEMAN:REVIEW]`) and assert that exact badge. Two more cases cover the fallback path and a missing payload:

```bash
SID="verify-$(date +%s)-$$"
CMD="node \${CLAUDE_CONFIG_DIR:-\$HOME/.claude}/hud/omc-hud-combined.mjs \"$HOME/.claude/hooks/caveman-statusline.sh\""
mkdir -p ~/.claude/.caveman-sessions && printf 'review\n' > ~/.claude/.caveman-sessions/"$SID".mode
# 1. Normal case: both segments, badge last, from the staged session
OUT=$(printf '{"session_id":"%s"}' "$SID" | sh -c "$CMD" 2>/dev/null)
case "$OUT" in
  *"[OMC"*"[CAVEMAN:REVIEW]"*) echo "composed: ok" ;;
  *) echo "composed: CHECK — ${OUT:-(empty)}" ;;
esac
# 2. Wrong caveman path: the registry fallback must still find the badge
OUT=$(printf '{"session_id":"%s"}' "$SID" | node ~/.claude/hud/omc-hud-combined.mjs /nonexistent/caveman-statusline.sh 2>/dev/null)
case "$OUT" in *"[CAVEMAN:REVIEW]"*) echo "fallback: ok" ;; *) echo "fallback: CHECK — ${OUT:-(empty)}" ;; esac
# 3. No payload at all: the line must still render
OUT=$(node ~/.claude/hud/omc-hud-combined.mjs "$HOME/.claude/hooks/caveman-statusline.sh" </dev/null 2>/dev/null)
case "$OUT" in *"[OMC"*) echo "empty stdin: ok" ;; *) echo "empty stdin: CHECK — ${OUT:-(empty)}" ;; esac
rm -f ~/.claude/.caveman-sessions/"$SID".mode
```

All three must print `ok`. If any prints `CHECK`, stop and report; do not write `settings.json`.

### 3. Wire it

Write exactly the command that was checked. The OMC part may keep `$VAR`; the quoted caveman path must be absolute:

```bash
S=~/.claude/settings.json
CMD="node \${CLAUDE_CONFIG_DIR:-\$HOME/.claude}/hud/omc-hud-combined.mjs \"$HOME/.claude/hooks/caveman-statusline.sh\""
T=$(mktemp "$S.tmp.XXXXXX") && jq --arg c "$CMD" '.statusLine = {"type": "command", "command": $c}' "$S" > "$T" && mv "$T" "$S"
jq -c .statusLine "$S"
```

If `~/.claude/hud/verify-statusline.mjs` is already present from an earlier run, it performs the same staged-session check against whatever `settings.json` actually has configured: `node ~/.claude/hud/verify-statusline.mjs`.

## Step 4 — Restart to activate the HUD

The HUD statusline, including the combiner wired in Step 3b, only takes effect on a fresh start. Exit cleanly.

**First, confirm the inner agent is *still* idle.** The setup skill chains its phases across separate turns and can go briefly idle *between* them, so an earlier `wait_idle=IDLE` does not guarantee it is idle now. This matters because the first keystroke below is an `Escape`, and **`Escape` sent into a busy turn is an interrupt, not an input-clear** — that is exactly how a prior run aborted the setup's final phase mid-write. Gate the exit on a fresh idle check:

```bash
PANE=%3
if tmux capture-pane -t "$PANE" -p | grep -qE "esc to interrupt|· ↓ .*tokens"; then
  echo "BUSY — run wait_idle first, do NOT send Escape yet"
else
  echo "idle — safe to send the exit sequence"
fi
```

If it prints `BUSY`, run `wait_idle` (Step 0) and re-check; only run the `/exit` block below once it prints `idle`. (With the `setupCompleted` gate from Step 3 already passed, the agent has no remaining setup work to chain into, so this should read `idle` on the first try — the guard is defense-in-depth.)

`/exit` is a slash command, so use the proactive double-`Enter` pattern from Step 0 (dropdown autocomplete otherwise eats the first `Enter`):

```bash
PANE=%3
tmux send-keys -t "$PANE" Escape; sleep 0.4
tmux capture-pane -t "$PANE" -p -S -5 | grep -qi "rewind\|restore" && { tmux send-keys -t "$PANE" Escape; sleep 0.4; }
tmux send-keys -t "$PANE" -l '/exit'
sleep 0.4
```

```bash
PANE=%3
tmux capture-pane -t "$PANE" -p -S -50 > /tmp/omc-presnap-3.txt
tmux send-keys -t "$PANE" '' Enter
sleep 0.5
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

## Step 5 — Run doctor (mandatory, do not skip even if Step 6 already looks green)

Plain text, not a slash command — no dropdown risk, but still use the verified-entry pattern since it's cheap and closes off the dropped-character failure mode entirely:

```bash
PANE=%3
TEXT='run omc doctor'
tmux send-keys -t "$PANE" -l "$TEXT"
sleep 0.4
tmux capture-pane -t "$PANE" -p | tr '\n' ' ' | grep -qF "${TEXT:0:12}" && echo "typed ok" || echo "TYPE_VERIFY_FAILED"
```

```bash
PANE=%3
tmux capture-pane -t "$PANE" -p -S -50 > /tmp/omc-presnap-3.txt
tmux send-keys -t "$PANE" '' Enter
```

Run `wait_idle` (Step 0; a shorter `idle_budget=300`/Bash `timeout: 340000` is plenty for doctor), then capture the report:

```bash
tmux capture-pane -t "$PANE" -p -S -200
```

Note whether its summary reports `HEALTHY` or `ISSUES FOUND`, and record each check row marked `WARN` or `CRITICAL`. A `caveman-statusline.sh` listed under `~/.claude/hooks/` is the caveman plugin's stable copy, not a legacy OMC script.

## Step 6 — Independent verification (do not skip)

This is the real success gate. You run these yourself, against the shared filesystem — they do not depend on what the inner agent said:

```bash
# OMC installed in global CLAUDE.md
grep -q "<!-- OMC:START -->" ~/.claude/CLAUDE.md && echo "CLAUDE.md: OMC ok" || echo "CLAUDE.md: MISSING"
# Pre-existing import preserved (the inner agent has falsely warned this was lost)
grep -q "@RTK" ~/.claude/CLAUDE.md && echo "RTK: preserved" || echo "RTK: CHECK backup"
# statusLine renders BOTH segments, in order — run the configured command, never grep the command string.
# A staged throwaway session keeps the badge from being blank merely for lack of an active caveman mode.
# The `review` mode renders [CAVEMAN:REVIEW], which the global .caveman-active fallback is unlikely to produce,
# so a combiner that drops the session id cannot pass this check by accident (Step 3b).
SID="verify-$(date +%s)-$$"
mkdir -p ~/.claude/.caveman-sessions && printf 'review\n' > ~/.claude/.caveman-sessions/"$SID".mode
OUT=$(printf '{"session_id":"%s"}' "$SID" | sh -c "$(jq -r '.statusLine.command' ~/.claude/settings.json 2>/dev/null)" 2>/dev/null)
rm -f ~/.claude/.caveman-sessions/"$SID".mode
case "$OUT" in
  *"[OMC"*"[CAVEMAN:REVIEW]"*) echo "statusLine: caveman-last ok" ;;
  *"[CAVEMAN"*"[OMC"*)         echo "statusLine: CHECK — badge renders before the OMC segment" ;;
  *"[OMC"*"[CAVEMAN"*)         echo "statusLine: CHECK — badge renders, but not the staged mode (session id dropped?)" ;;
  *"[OMC"*)                    echo "statusLine: CHECK — OMC renders, caveman badge missing" ;;
  *)                           echo "statusLine: CHECK — output: ${OUT:-(empty)}" ;;
esac
# The command names the stable caveman copy by its literal absolute path, so the caveman hook keeps it current (Step 3b)
jq -r '.statusLine.command' ~/.claude/settings.json | grep -qF "\"$HOME/.claude/hooks/caveman-statusline.sh\"" \
  && echo "caveman path: stable copy, refreshable" || echo "caveman path: CHECK — command does not name the stable copy by absolute path"
# The caveman hook accepts the command: it records a command it considers broken in .caveman-statusline-stale,
# and it flags a stable copy that differs from the loaded plugin's script as outdated.
STALE=$(cat ~/.claude/.caveman-statusline-stale 2>/dev/null)
[ -n "$STALE" ] && [ "$STALE" = "$(jq -r '.statusLine.command' ~/.claude/settings.json)" ] \
  && echo "caveman hook: CHECK — it reported this statusLine as broken" || echo "caveman hook: command accepted"
IP=$(jq -r '.plugins["caveman@caveman"] | map(select(.scope == "user")) [0].installPath // .plugins["caveman@caveman"][0].installPath' ~/.claude/plugins/installed_plugins.json)
cmp -s "$IP/src/hooks/caveman-statusline.sh" ~/.claude/hooks/caveman-statusline.sh \
  && echo "caveman copy: current" || echo "caveman copy: CHECK — stable copy differs from the loaded plugin's script"
# config + HUD artifacts exist (gate on the setupCompleted marker, not mere file existence)
grep -q '"setupCompleted"' ~/.claude/.omc-config.json 2>/dev/null && echo "omc-config: complete" || { test -f ~/.claude/.omc-config.json && echo "omc-config: PARTIAL — no setupCompleted" || echo "omc-config: MISSING"; }
# HUD wrapper plus the helper module it imports since OMC 5.x
test -f ~/.claude/hud/omc-hud.mjs && test -f ~/.claude/hud/lib/config-dir.mjs && echo "HUD: installed" || echo "HUD: MISSING (omc-hud.mjs or lib/config-dir.mjs)"
```

Confirm the live statusline in the running pane shows the OMC segment first and the caveman badge last (e.g. `[OMC#...L] | ... [CAVEMAN]`).

Also confirm the caveman SessionStart hook did not ask for a statusline after the Step 4 restart. On a fresh install it says `STATUSLINE SETUP NEEDED … Proactively offer to set this up`, and an inner agent running with bypassed permissions may act on it by writing a caveman-only `statusLine` that drops the HUD. Hook output is often collapsed in the TUI, so a missing match in the pane proves little; the `caveman hook` and `statusLine` checks above are the real evidence. A match is still a red flag worth reporting:

```bash
PANE=%3
tmux capture-pane -t "$PANE" -p -S -200 | grep -E "STATUSLINE (SETUP|REPAIR) NEEDED" \
  && echo "caveman nudge: CHECK — the hook still asks for a statusline" || echo "caveman nudge: none visible"
```

## Step 7 — Report

Summarize to the user: doctor verdict **plus** your independent Step 6 results. If a combiner script owns `statusLine`, say so and note that two things rewrite `statusLine.command` back to the plain `omc-hud.mjs` and silently drop the badge: any later `/oh-my-claudecode:hud <preset>` run, and every `omc-setup` re-run, because setup's Phase 2 always runs `hud setup`. That includes refreshing OMC after an upgrade. After either, the command must be re-pointed and re-verified (Step 3b). If any check failed or any wait returned `TIMEOUT`/`ABORT`, say so explicitly with the captured evidence — do not soften a partial result into "done". If any `wait_idle` resolved via the aliasing guard (pane diff instead of catching `esc to interrupt` directly) or any `TYPE_VERIFY_FAILED`/retry occurred, mention it — it's a signal the pane is behaving oddly even if the end state looks fine.

## Constraints

- **Two-call rule for ALL Claude Code TUI input** (prompts, commands, confirmations): text call, then bare `Enter` call. Shell commands outside the TUI may use the combined form.
- **Settle delay after every discrete TUI keystroke action** (`sleep 0.4` after Escape, after typing, before the next action) — sending the next key before the Ink UI's render pass settles is how characters and `Enter` presses get silently dropped.
- **Verify typed text before submitting** (Step 0's clear/type/verify loop) instead of trusting a blind `send-keys` — this catches a dropped leading character before it becomes a mistyped command, rather than discovering it after the fact.
- **Slash commands get a proactive double-`Enter`** (Step 0) — the autocomplete dropdown can consume the first one as a selection, not a submit.
- **`wait_idle` requires 2 consecutive clean polls before declaring `IDLE`**, and falls back to a presubmit-snapshot diff before declaring `NOSTART` — a single missed poll of `esc to interrupt` between chained tool calls, or a turn that finished faster than the poll caught it, must not be misread.
- **Never poll with `sleep N && cmd` chained in one Bash call** — the harness blocks it. Use a single Bash call containing a `while`/`until` loop with an internal `sleep` (as in Step 0).
- **A single Bash call cannot be timed out past 600000ms (10 min).** Keep `wait_idle`'s internal `idle_deadline` at 540s and request Bash-tool `timeout: 595000` — never set the internal deadline equal to (or above) the Bash-tool timeout; a prior run set both to 600s/600000ms and the harness's own kill silently discarded the script's result. If a step is legitimately slow, chain additional bounded `wait_idle` calls (cap ~3) rather than requesting one longer call.
- **Shell state does not persist between your Bash calls.** Hardcode the literal pane id (`%N` from Step 1) into every block, and use a file (e.g. `/tmp/omc-presnap-3.txt`), not a shell variable, to carry a snapshot from one call to the next.
- **Detect state from chrome** (`esc to interrupt`, the `· ↓ .*tokens` spinner line, `bypass permissions`), not from spinner *verbs* or specific summary wording — and require pane-content stability across polls before declaring idle. `esc to interrupt` alone is not reliable: v2.1.207 never rendered it, and a loop keyed on it declared idle mid-turn.
- **Clear the input buffer with `Escape`, then check for `Rewind`/`Restore` chrome before doing anything else** — a second blind `Escape` (or an `Escape` on an already-empty box) can open a checkpoint-restore menu instead of clearing; if seen, cancel with one more `Escape` and never `Enter` it (use the `clear_input` guard from Step 0).
- **Never send `Escape` (or any key) into a *busy* turn** — while a turn is running (`esc to interrupt` in the footer) `Escape` is an **interrupt**, not an input-clear, and aborts the inner agent mid-work; a prior run interrupted the setup's final phase this way. Before any input step whose first keystroke is `Escape` (notably Step 4's exit), capture the pane and confirm `esc to interrupt` is absent; if present, `wait_idle` first. The setup skill chains phases across turns, so one earlier `IDLE` does not prove it is still idle.
- **Gate the exit/restart on `setupCompleted` in `.omc-config.json`, not mere file existence** — earlier phases write `taskTool` and `team`; only the final phase adds `setupCompleted` and `setupVersion`. A bare `test -f` can pass while the final phase is still running, which is what let a prior run proceed to Step 4 and interrupt it. On a re-run, also require `setupCompleted` to be newer than the run start, and `setupVersion` to match the plugin version in `installed_plugins.json` (Step 3). Keep the Step 3 nudge + safety-valve so a renamed marker in a future version cannot deadlock the flow.
- **Text sitting in the input box may be an inert placeholder, not real buffer content** — it can survive `Escape` and `Ctrl-U` untouched. Don't trust "text is visible" as "text will submit"; if clearing does nothing, it's cosmetic — type your own command directly.
- **Trust the filesystem over the inner agent.** Its claims and warnings (especially "you lost X") can be wrong; verify in Step 6.
- **Resolve plugin file paths from `~/.claude/plugins/installed_plugins.json`** (`<plugin>@<marketplace>` → `installPath`), never by scanning hashed cache dirs by `mtime` and never from `plugins/marketplaces/*`, which is the update source rather than the loaded copy. `installPath` contains the plugin version, so resolve it at run time and never hard-code it. For caveman, prefer the stable copy at `$CLAUDE_CONFIG_DIR/hooks/caveman-statusline.sh`, which the caveman plugin keeps current. Run it with `bash`, and name it by its quoted absolute path in `statusLine.command` (Step 3b).
- **Verify a composed statusline by executing it with a synthetic payload before wiring it into `settings.json`** — a dropped segment renders a plausible-looking line rather than an error, so file-existence checks prove nothing (Step 3b). Back up `settings.json` before writing `statusLine`.
- **Compose the statusline yourself, after the Step 3 gate and before the Step 4 restart.** Setup's Phase 2.1 always resets `statusLine` to the plain HUD, so a combiner wired during setup is overwritten. Install the tested combiner from Step 3b verbatim instead of letting the inner agent write one, and tell the inner agent to ignore caveman's statusline nudge (Step 2).
- Do not use `/omc` slash commands to start setup; plain text triggers the hook chain that loads the skills.
- The HUD statusline activates only after a full restart, not mid-session.
- Capture with `-S -200` so output that scrolled off the visible region is still inspected.
