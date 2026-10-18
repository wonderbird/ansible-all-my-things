<!-- SPDX-License-Identifier: MIT-0 -->
# claude_code_config

Ansible role that applies opinionated [Anthropic's Claude Code](https://claude.ai/code)
CLI configuration for sophisticated development, on top of the general,
safe-for-any-project baseline `claude_code` creates: installs the
[oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) and
[caveman](https://github.com/JuliusBrussee/caveman) Claude Code plugins,
clones the [ai-agent-workspace](https://github.com/wonderbird/ai-agent-workspace)
skill library and symlinks its skills into `~/.claude/skills`,
configures the [Exa](https://exa.ai) MCP server for web search, installs the
`omc` CLI, and merges its own opinionated keys into `settings.json`.

`beads` and `specify_cli` are cross-harness CLI tools installed by their own
single-purpose roles, not by this role. The `claude_code` role installs only
the Claude Code binary; this role depends on it — see `DESIGN.md` for why the
ai-agent-workspace clone, the `omc` CLI install and `rtk init -g` live here
rather than in their own roles.

## Requirements

- Ansible 2.19+
- The `git` role applied first, providing the `git` binary for the
  ai-agent-workspace and oh-my-claudecode source clones and the Claude Code
  plugin marketplaces
- The `claude_code` role applied first, providing the `claude` binary
- The `rtk` role applied first, providing `/usr/local/bin/rtk`
- The `nodejs` role applied first, providing a system-wide Node.js LTS
  install (`/usr/local/bin/node`/`npm`)
- Internet access from target hosts (downloads plugins and the omc CLI)

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to configure Claude Code for |
| `login_users` | *(required)* | List of user objects with `name`, `password`, and `exa_api_key` |

## Dependencies

`rtk`, `nodejs`, `git`, `claude_code`. See `meta/main.yml`.

## Example Playbook

```yaml
- hosts: desktops
  roles:
    - role: claude_code_config
      vars:
        login_user_names:
          - alice
          - bob
        login_users:
          - name: alice
            password: "{{ vault_alice_password }}"
            exa_api_key: "{{ vault_alice_exa_api_key }}"
          - name: bob
            password: "{{ vault_bob_password }}"
            exa_api_key: "{{ vault_bob_exa_api_key }}"
```

## What This Role Does

1. Clones ai-agent-workspace to `~/Documents/Cline/ai-agent-workspace`
   (re-provision pulls updates) and symlinks its skills into
   `~/.claude/skills/` (idempotent; re-provision re-links)
2. Registers and installs the oh-my-claudecode Claude Code plugin
3. Registers and installs the caveman Claude Code plugin
4. Registers the claude-plugins-official marketplace and installs the
   context7 plugin
5. Configures the [Exa](https://exa.ai) MCP server (`exa`) with the user's API
   key (skipped if already registered)
6. Clones the oh-my-claudecode source repo and installs the `omc` CLI
   (`oh-my-claude-sisyphus`, skipped if already installed)
7. Initializes rtk globally (`rtk init -g`) for each desktop user
8. Merges its own opinionated keys (agent-team env vars, `teammateMode`,
   rtk/bd-guard hooks) into `settings.json`, on top of the baseline
   `claude_code` already wrote — see `DESIGN.md`
9. Sets `CLAUDE_PLUGIN_ROOT` in `.bashrc`
10. Copies the OMC setup prompt to `~/Documents/Cline/setup-omc-prompt.md`

## Post-install Manual Steps

After running the playbook, each user must complete initial setup interactively.
The role installs the plugins but does not configure them — that requires a
running Claude Code session. To simplify the process, the role copies a prompt
file to `~/Documents/Cline/setup-omc-prompt.md` to automate the setup steps.

1. `cd ~/Documents/Cline`
2. Run `claude` to open a Claude Code session.
3. Copy paste this prompt verbatim: `@setup-omc-prompt.md`
   The prompt instructs Claude to:
   - spawn a second Claude Code session in a new tmux pane
   - run `omc setup` in that pane (global install, suggested defaults, no MCP,
     caveman badge in the statusline)
   - restart the pane session and run `omc doctor` to verify the result

   The Exa MCP server is pre-configured by the role and does not need to be set
   up through `omc setup`. If the GitHub MCP is desired, a GitHub personal access
   token is required and must be provided when prompted.
4. Run `/caveman` to activate caveman mode.

## License

MIT-0
