<!-- SPDX-License-Identifier: MIT-0 -->
# opencode

Ansible role that installs the [OpenCode](https://opencode.ai) AI coding agent
CLI as a system-wide binary at `/usr/local/bin/opencode` on Linux.

See [DESIGN.md](DESIGN.md) for non-obvious decisions and the integrity model.

## Boundary

The role installs the `opencode` binary only. It does not configure LLM
providers, manage per-user shell PATH (`/usr/local/bin` is already on every
user's `PATH`), or initialise `AGENTS.md` for any project. Those are
session-level operations outside this role's scope.

## Requirements

- Ansible 2.19+
- Linux x86_64 (`x64`) or aarch64 (`arm64`)
- Internet access to `github.com` from the target host

## Role Variables

All variables have safe defaults. None are required from the caller.

| Variable | Default | Description |
| --- | --- | --- |
| `opencode_version` | `"v1.17.10"` | Pinned OpenCode release tag (`v`-prefixed). |
| `opencode_sha256_amd64` | *(see defaults)* | SHA-256 of `opencode-linux-x64.tar.gz` for `opencode_version`. |
| `opencode_sha256_arm64` | *(see defaults)* | SHA-256 of `opencode-linux-arm64.tar.gz` for `opencode_version`. |
| `opencode_install_path` | `/usr/local/bin/opencode` | Path where the binary is installed. |

The three pinned values (version + both checksums) are updated together by
`playbooks/update-versions/perform-updates.yml`.

## Dependencies

None. See `meta/main.yml`.

## Example Playbook

```yaml
- hosts: developers
  roles:
    - role: opencode
```

## License

MIT-0
