# OMC Setup — Conductor Prompt

Use this prompt in an existing Claude Code session (the **conductor**) to automate
OMC setup in a fresh parallel session. Prerequisites: `oh-my-claudecode` plugin
installed, `omc` CLI installed, tmux running.

## Prompt

```text
Spawn a new tmux pane, start `claude --dangerously-skip-permissions` in it, and
act as conductor for that session.

Once the Claude Code prompt appears, send this exact text (no leading slash —
plain text only, not a slash command):

  run omc setup, install globally, configure suggested defaults, skip MCP configuration.
  The caveman plugin is also installed and active. Configure the HUD statusline so
  that the caveman mode badge appears last in the status line.

Monitor pane output until setup reports "Setup complete". Then exit Claude Code
in that pane and restart it with `claude --dangerously-skip-permissions`. Once
the new session prompt appears, send:

  run omc doctor

Wait for the doctor report and summarize the result.
```

## Key constraints discovered during development

- **No `/omc` slash command.** Claude Code's UI intercepts unknown `/`-prefixed
  commands before the `UserPromptSubmit` hook runs. The hook's `skill-injector.mjs`
  never executes, so skills never load. Use plain text instead.
- **Plain text triggers the hook chain.** Sending `run omc setup …` as a regular
  user prompt causes `skill-injector.mjs` to inject the skill list, and Claude AI
  invokes `oh-my-claudecode:setup` via the Skill tool automatically.
- **All preferences upfront → non-interactive.** Specifying scope (globally),
  defaults (suggested), and MCP (skip) in the initial prompt lets setup complete
  without any follow-up questions.
- **Restart required.** The HUD statusline (`statusLine` in `settings.json`) only
  activates after a full Claude Code restart, not mid-session.
- **Polling for completion.** Use `tmux capture-pane` in a loop to monitor the
  other session. Check for absence of spinner keywords (`Whirring`, `Incubating`,
  `Crunching`) and presence of a completion marker (`Setup complete`, `HEALTHY`).
