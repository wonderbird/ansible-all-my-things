<!-- SPDX-License-Identifier: MIT-0 -->
# specify_cli

Ansible role that installs [spec-kit](https://github.com/github/spec-kit)'s
`specify` CLI via `pipx` for each desktop user.

specify-cli is cross-harness — usable from Claude Code, opencode, Codex, and
other agent harnesses — so it is a standalone role rather than bundled into
`claude_code`.

## Requirements

- Ansible 2.19+
- Internet access from target hosts (VCS-style pipx install clones spec-kit
  via `git`)

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to install specify-cli for |
| `specify_cli_version` | `"v0.8.18"` | spec-kit git tag installed via `pipx`, refreshed only by `playbooks/update-versions/perform-updates.yml` |

## Dependencies

None. See `meta/main.yml` for details.

## Example Playbook

```yaml
- hosts: desktops
  roles:
    - role: specify_cli
      vars:
        login_user_names:
          - alice
          - bob
```

## What This Role Does

1. Installs `pipx` and `git`
2. Installs `specify` via `pipx install` from the pinned `specify_cli_version`
   git tag (skipped if already installed)

## License

MIT-0
