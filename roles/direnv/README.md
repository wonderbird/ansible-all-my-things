<!-- SPDX-License-Identifier: MIT-0 -->
# direnv

Ansible role that installs [direnv](https://direnv.net) as a system-wide
binary at `/usr/local/bin/direnv` on Linux and hooks it into bash for every
login user.

See [DESIGN.md](DESIGN.md) for non-obvious decisions and the integrity model.

## Boundary

The role installs the `direnv` binary and adds the bash hook
(`eval "$(direnv hook bash)"`) to each login user's `~/.bashrc`. It does not
create or manage any project-level `.envrc` files, does not configure
direnv's own settings (`~/.config/direnv/direnv.toml`), and does not hook any
shell other than bash.

## Requirements

- Ansible 2.19+
- Linux x86_64 or aarch64
- Internet access to `github.com` from the target host

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to add the direnv bash hook for |
| `direnv_version` | `"v2.37.1"` | Pinned direnv release tag (`v`-prefixed). |
| `direnv_sha256_amd64` | *(see defaults)* | SHA-256 of `direnv.linux-amd64` for `direnv_version`. |
| `direnv_sha256_arm64` | *(see defaults)* | SHA-256 of `direnv.linux-arm64` for `direnv_version`. |
| `direnv_install_path` | `/usr/local/bin/direnv` | Path where the binary is installed. |

The three pinned values (version + both checksums) are updated together by
`playbooks/update-versions/perform-updates.yml`.

## Dependencies

None. See `meta/main.yml`.

## Example Playbook

```yaml
- hosts: developers
  roles:
    - role: direnv
      vars:
        login_user_names:
          - alice
          - bob
```

## License

MIT-0
