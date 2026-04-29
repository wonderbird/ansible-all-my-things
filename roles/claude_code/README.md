#SPDX-License-Identifier: MIT-0
# claude_code

Ansible role that installs [Anthropic's Claude Code](https://claude.ai/code) CLI
on Linux for each desktop user, verifies binary integrity, and installs the
[oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) and
[caveman](https://github.com/JuliusBrussee/caveman) Claude Code plugins.

## Requirements

- Ansible 2.19+
- `git` present on target hosts (not managed by this role)
- `curl` present on target hosts (used by the beads installer)
- Internet access from target hosts (downloads Claude Code, plugins, beads)

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `claude_code_manifest_base_url` | Google Storage URL | Base URL for the Claude Code release manifest |
| `claude_code_platform_map` | `{x86_64: linux-x64, aarch64: linux-arm64}` | Maps `ansible_architecture` to Claude Code platform string |
| `desktop_user_names` | *(required)* | List of local usernames to install Claude Code for |

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
```

## What This Role Does

1. Verifies the target architecture is supported
2. Fetches the latest Claude Code version and release manifest
3. Downloads and runs the official Claude Code installer for each user (skipped if already installed)
4. Verifies the installed binary checksum against the release manifest
5. Adds `~/.local/bin` to each user's `PATH` via `.bashrc`
6. Clones the oh-my-claudecode source repo to `~/Documents/Cline/oh-my-claudecode`
7. Installs the [beads](https://github.com/steveyegge/beads) issue tracker (`bd`)
8. Registers and installs the oh-my-claudecode Claude Code plugin
9. Registers and installs the caveman Claude Code plugin

## Post-install Manual Steps

After running the playbook, each user must complete initial setup interactively:

1. Run `claude` to open a Claude Code session
2. Run `/setup` inside the session. If the [Exa](https://exa.ai) and GitHub MCPs
   are desired, then corresponding API keys (PATs) are required.
3. Run `/caveman` to activate caveman mode

## License

MIT-0
