<!-- SPDX-License-Identifier: MIT-0 -->
# claude_code

Ansible role that installs [Anthropic's Claude Code](https://claude.ai/code) CLI
binary on Linux for each desktop user, verifying its integrity against a pinned
per-platform sha256 checksum.

This role is install-only: it does not touch `~/.claude` or otherwise
opinionate the binary's configuration. Global `~/.claude` configuration
(settings.json, plugins, skills symlinks, MCP servers, the `omc` CLI) is
provisioned by the separate `claude_code_config` role, which depends on this
one — see its `README.md`/`DESIGN.md` for that scope.

## Requirements

- Ansible 2.19+
- Internet access from target hosts (downloads the Claude Code binary)

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `claude_code_manifest_base_url` | Google Storage URL | Base URL for the Claude Code release manifest |
| `claude_code_platform_map` | `{x86_64: linux-x64, aarch64: linux-arm64}` | Maps `ansible_architecture` to Claude Code platform string |
| `desktop_user_names` | *(required)* | List of local usernames to install Claude Code for |

## Dependencies

None. See `meta/main.yml`.

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
2. Installs `jq`, `git` and `curl` (used by consumers of this binary, such as
   `claude_code_config`)
3. Downloads the binary for the pinned `claude_code_version` directly from
   the manifest-derived URL for each user (skipped if already installed),
   verifying it against the pinned per-platform sha256 checksum BEFORE
   placement via Ansible-native SHA256 checking
4. Adds `~/.local/bin` to each user's `PATH` via `.bashrc`

## License

MIT-0
