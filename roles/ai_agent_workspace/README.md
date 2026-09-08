<!-- SPDX-License-Identifier: MIT-0 -->
# ai_agent_workspace

Ansible role that clones the
[ai-agent-workspace](https://github.com/wonderbird/ai-agent-workspace) skill
library source repository for each desktop user.

This is a generic, cross-harness clone with no Claude-Code-specific logic —
see `DESIGN.md` for why the `~/.claude/skills` symlink step stays in the
`claude_code_config` role instead of here.

## Requirements

- Ansible 2.19+
- Internet access from target hosts

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to clone ai-agent-workspace for |

## Dependencies

- `git` (declared in `meta/main.yml`) — provides the `git` binary the
  clone task requires.

## Example Playbook

```yaml
- hosts: desktops
  roles:
    - role: ai_agent_workspace
      vars:
        login_user_names:
          - alice
          - bob
```

## What This Role Does

1. Clones ai-agent-workspace to `~/Documents/Cline/ai-agent-workspace`
   (idempotent; re-provision pulls updates)

## License

MIT-0
