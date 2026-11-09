<!-- SPDX-License-Identifier: MIT-0 -->
# skill_factory

Ansible role that clones the
[skill-factory](https://github.com/wonderbird/skill-factory) skill-authoring
source repository for each login user.

This is a generic, cross-harness clone with no Claude-Code-specific logic:
it activates no skill in any tool — see `DESIGN.md`.

## Requirements

- Ansible 2.19+
- Internet access from target hosts

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to clone skill-factory for |

## Dependencies

- `git` (declared in `meta/main.yml`) — provides the `git` binary the
  clone task requires.

## Example Playbook

```yaml
- hosts: desktops
  roles:
    - role: skill_factory
      vars:
        login_user_names:
          - alice
          - bob
```

## What This Role Does

1. Clones skill-factory to `~/Documents/Cline/skill-factory`, checking out
   the `fork` branch (idempotent; re-provision pulls updates)

## License

MIT-0
