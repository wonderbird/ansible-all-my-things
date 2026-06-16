<!-- SPDX-License-Identifier: MIT-0 -->
# claude_code

Ansible role that installs [Anthropic's Claude Code](https://claude.ai/code) CLI
on Linux for each desktop user, verifies binary integrity, installs the
[oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) and
[caveman](https://github.com/JuliusBrussee/caveman) Claude Code plugins,
clones the [ai-agent-workspace](https://github.com/eudicy/ai-agent-workspace)
with its skill library, and configures the [Exa](https://exa.ai) MCP server
for web search.

## Requirements

- Ansible 2.19+
- `git` present on target hosts (not managed by this role)
- Internet access from target hosts (downloads Claude Code, plugins, beads)

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `claude_code_manifest_base_url` | Google Storage URL | Base URL for the Claude Code release manifest |
| `claude_code_platform_map` | `{x86_64: linux-x64, aarch64: linux-arm64}` | Maps `ansible_architecture` to Claude Code platform string |
| `desktop_user_names` | *(required)* | List of local usernames to install Claude Code for |
| `desktop_users` | *(required)* | List of user objects with `name`, `password`, and `exa_api_key` |

## Dependencies

None. See `meta/main.yml` for details.

## Example Playbook

```yaml
- hosts: desktops
  roles:
    - role: claude_code
      vars:
        desktop_user_names:
          - alice
          - bob
        desktop_users:
          - name: alice
            password: "{{ vault_alice_password }}"
            exa_api_key: "{{ vault_alice_exa_api_key }}"
          - name: bob
            password: "{{ vault_bob_password }}"
            exa_api_key: "{{ vault_bob_exa_api_key }}"
```

## What This Role Does

1. Verifies the target architecture is supported
2. Fetches the latest Claude Code version and release manifest
3. Downloads and runs the official Claude Code installer for each user
   (skipped if already installed)
4. Verifies the installed binary checksum against the release manifest
5. Adds `~/.local/bin` to each user's `PATH` via `.bashrc`
6. Clones the oh-my-claudecode source repo to `~/Documents/Cline/oh-my-claudecode`
7. Installs the [beads](https://github.com/steveyegge/beads) issue tracker (`bd`)
8. Clones [ai-agent-workspace](https://github.com/eudicy/ai-agent-workspace) to
   `~/Documents/Cline/ai-agent-workspace` and symlinks its skills into
   `~/.claude/skills/` (idempotent; re-provision pulls updates and re-links)
9. Registers and installs the oh-my-claudecode Claude Code plugin
10. Registers and installs the caveman Claude Code plugin
11. Configures the [Exa](https://exa.ai) MCP server (`exa`) with the user's API
    key (skipped if already registered)

## Post-install Manual Steps

After running the playbook, each user must complete initial setup interactively:

1. Run `claude` to open a Claude Code session
2. Run `/setup` inside the session. The Exa MCP server is configured
   automatically by this role. If the GitHub MCP is desired, a GitHub personal
   access token is required.
3. Run `/caveman` to activate caveman mode

## License

MIT-0
