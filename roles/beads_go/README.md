<!-- SPDX-License-Identifier: MIT-0 -->
# beads_go

Ansible role that installs the [beads](https://github.com/gastownhall/beads)
issue tracker (`bd`, the Go implementation) and clones the beads source
repository for each desktop user.

beads is cross-harness — usable from Claude Code, opencode, Codex, and other
agent harnesses — so it is a standalone role rather than bundled into
`claude_code`. It is a sibling of `dolt_sql_server` (beads is Dolt-backed).
The beads viewer (`bv`) is installed by the separate `beads_viewer` role.

## Requirements

- Ansible 2.19+
- Internet access from target hosts (downloads the bd release archive)

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to clone the beads source for |

The binary's version and checksum are pinned in `defaults/main.yml`
(`beads_go_version`/`beads_go_sha256_amd64`/`beads_go_sha256_arm64`), refreshed
only by `playbooks/update-versions/perform-updates.yml`. The role does not
auto-upgrade an already-installed `bd` when the pin changes; remove the binary
and re-run the role to pick up a new pin.

## Dependencies

None. See `meta/main.yml` for details.

## Example Playbook

```yaml
- hosts: desktops
  roles:
    - role: beads_go
      vars:
        login_user_names:
          - alice
          - bob
```

## What This Role Does

1. Installs `git` (needed to clone the beads source repository)
2. Installs the beads issue tracker (`bd`) to `/usr/local/bin/bd`,
   system-wide, by downloading the pinned `beads_go_version` release archive
   from [gastownhall/beads](https://github.com/gastownhall/beads) and
   verifying it against the pinned per-arch sha256 checksum before
   extraction. Skipped if `bd` is already installed.
3. Clones the beads source repository to `~/Documents/Cline/beads` for each
   desktop user

## License

MIT-0
