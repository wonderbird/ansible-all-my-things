<!-- SPDX-License-Identifier: MIT-0 -->
# bun

Ansible role that installs the [Bun](https://bun.sh) JavaScript runtime as a
system-wide binary at `/usr/local/bin/bun` on Linux, together with its package
runner `bunx` at `/usr/local/bin/bunx`.

See [DESIGN.md](DESIGN.md) for non-obvious decisions and the integrity model.

## Boundary

The role installs the `bun` binary and the `bunx` entry point only. It does not
install any JavaScript package, does not configure a package registry, and does
not manage per-user shell PATH (`/usr/local/bin` is already on every user's
`PATH`). Roles that need a specific tool at run time invoke it through `bunx`
themselves.

## Requirements

- Ansible 2.19+
- Linux x86_64 (`x64`) or aarch64 (`aarch64`)
- Internet access to `github.com` from the target host

## Role Variables

All variables have safe defaults. None are required from the caller.

| Variable | Default | Description |
| --- | --- | --- |
| `bun_version` | `"bun-v1.4.2"` | Pinned Bun release tag (`bun-v`-prefixed, as upstream tags it). |
| `bun_sha256_x64` | *(see defaults)* | SHA-256 of `bun-linux-x64.zip` for `bun_version`. |
| `bun_sha256_aarch64` | *(see defaults)* | SHA-256 of `bun-linux-aarch64.zip` for `bun_version`. |
| `bun_install_path` | `/usr/local/bin/bun` | Path where the binary is installed. |
| `bun_bunx_path` | `/usr/local/bin/bunx` | Path of the `bunx` symlink to that binary. |

The three pinned values (version + both checksums) are updated together by
`playbooks/update-versions/perform-updates.yml`.

## Dependencies

None. See `meta/main.yml`. The role installs `unzip` itself, because upstream
publishes the Linux builds as `.zip` archives only.

## Example Playbook

```yaml
- hosts: developers
  roles:
    - role: bun
```

## License

MIT-0
