<!-- SPDX-License-Identifier: MIT-0 -->
# beads_viewer

Ansible role that installs the
[beads viewer](https://github.com/Dicklesworthstone/beads_viewer) (`bv`)
system-wide.

`bv` is a read-only graph/triage view over beads issue data. It is
tracker-agnostic — it operates on the beads database regardless of which
tracker implementation produced it — so it is a standalone role rather than
being bundled with `beads_go`. The tracker (`bd`) is installed by the separate
`beads_go` role.

## Requirements

- Ansible 2.19+
- Internet access from target hosts (downloads the bv release archive)

## Role Variables

None required. The binary's version and checksum are pinned in
`defaults/main.yml` (`beads_viewer_version`, `beads_viewer_sha256_amd64`,
`beads_viewer_sha256_arm64`), refreshed only by
`playbooks/update-versions/perform-updates.yml`. The role installs
`bv` when it is missing or `bv --version` does not report the pinned
version, so a pin bump upgrades an existing host on the next run.

## Dependencies

- `binary_version_gate` (called through `include_role`, not declared in
  `meta/main.yml`) — tells whether the installed `bv` reports the pinned
  version.

## Example Playbook

```yaml
- hosts: desktops
  roles:
    - role: beads_viewer
```

## What This Role Does

Installs the beads viewer (`bv`) to `/usr/local/bin/bv`, system-wide, by
downloading the pinned `beads_viewer_version` release archive from
[Dicklesworthstone/beads_viewer](https://github.com/Dicklesworthstone/beads_viewer)
and verifying it against the pinned per-arch sha256 checksum before
extraction. Skipped if `bv` already reports the pinned version.

## License

MIT-0
