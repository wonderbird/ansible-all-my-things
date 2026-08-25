<!-- SPDX-License-Identifier: MIT-0 -->
# beads_rust

Ansible role that installs the [beads_rust](https://github.com/Dicklesworthstone/beads_rust)
issue tracker (`br`, the Rust implementation) and clones the beads_rust source
repository for each desktop user.

beads is cross-harness -- usable from Claude Code, opencode, Codex, and other
agent harnesses -- so it is a standalone role rather than bundled into
`claude_code`. It is a sibling of `beads_go` (the Go implementation, `bd`) and
`beads_viewer` (the read-only viewer, `bv`): three independent beads-family
roles.

## Requirements

- Ansible 2.19+
- Internet access from target hosts (downloads the br release archive)

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to clone the beads_rust source for |

The binary's version and checksum are pinned in `defaults/main.yml`
(`beads_rust_version`/`beads_rust_sha256_amd64`/`beads_rust_sha256_arm64`), refreshed
only by `playbooks/update-versions/perform-updates.yml`. The role does not
auto-upgrade an already-installed `br` when the pin changes; remove the binary
and re-run the role to pick up a new pin.

## Dependencies

None. See `meta/main.yml` for details.

## Example Playbook

```yaml
- hosts: desktops
  roles:
    - role: beads_rust
      vars:
        login_user_names:
          - alice
          - bob
```

## What This Role Does

1. Installs `git` (needed to clone the beads_rust source repository)
2. Installs the beads_rust issue tracker (`br`) to `/usr/local/bin/br`,
   system-wide, by downloading the pinned `beads_rust_version` release archive
   from [Dicklesworthstone/beads_rust](https://github.com/Dicklesworthstone/beads_rust)
   and verifying it against the pinned per-arch sha256 checksum before
   extraction. Skipped if `br` is already installed.
3. Clones the beads_rust source repository to `~/Documents/Cline/beads_rust`
   for each desktop user

## License

MIT-0
