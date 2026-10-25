<!-- SPDX-License-Identifier: MIT-0 -->
# uv

Ansible role that installs [uv](https://docs.astral.sh/uv/), the Python
package and project manager from Astral, as system-wide binaries on Linux:
`uv` and its tool runner `uvx`, both in `/usr/local/bin`.

See [DESIGN.md](DESIGN.md) for non-obvious decisions and the integrity model.

## Boundary

The role installs the `uv` and `uvx` binaries only. It does not install a
Python interpreter, any Python package or tool, shell completions, or per-user
configuration, and it does not run `uv self update`: the version is owned by
the pin. `/usr/local/bin` is already on every user's `PATH`.

## Requirements

- Ansible 2.19+
- Linux x86_64 or aarch64 with glibc (upstream's `*-unknown-linux-gnu` builds)
- Internet access to `github.com` from the target host

## Role Variables

All variables have safe defaults. None are required from the caller.

| Variable | Default | Description |
| --- | --- | --- |
| `uv_version` | *(see defaults)* | Pinned uv release tag (bare semver, no `v` prefix, as upstream tags it). |
| `uv_platform_map` | x86_64 and aarch64 | Ansible architecture fact to upstream target triple. |
| `uv_sha256_x86_64_gnu` | *(see defaults)* | SHA-256 of the x86_64 release archive for `uv_version`. |
| `uv_sha256_aarch64_gnu` | *(see defaults)* | SHA-256 of the aarch64 release archive for `uv_version`. |

The version and every checksum pin are updated together by the
version-update mechanism.

## Dependencies

None. See `meta/main.yml`. uv is a self-contained binary and needs no system
Python; it can download and manage Python versions itself.

## Example Playbook

```yaml
- hosts: developers
  roles:
    - role: uv
```

## License

MIT-0
