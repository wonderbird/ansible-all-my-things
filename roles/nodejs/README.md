<!-- SPDX-License-Identifier: MIT-0 -->
# nodejs

Ansible role that installs a specific Node.js LTS release system-wide,
plus a set of frequently used global npm packages (`eslint`,
`markdownlint-cli`, `prettier`, `typescript`).

Node.js is cross-harness — several roles and CLIs in this repo (notably
`claude_code_config`'s `omc` CLI install) need a working Node/npm toolchain,
so it is a standalone role rather than bundled into any one consumer.

## Requirements

- Ansible 2.19+
- Internet access from target hosts (downloads the release archive)

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `node_version` | *(pinned, e.g. `"v24.18.0"`)* | Node.js LTS release to install, refreshed only by `playbooks/update-versions/perform-updates.yml` |
| `node_platform_map` | `{x86_64: x64, aarch64: arm64}` | Maps `ansible_architecture` to nodejs.org's release-archive platform fragment |
| `node_sha256_x64` / `node_sha256_arm64` | *(pinned)* | Per-arch sha256 checksums for `node_version`'s release tarball |

The installed version is frozen on first install to whatever `node_version`
is pinned to. A `stat` gate on `/usr/local/bin/node` short-circuits the whole
download block once Node.js is installed, so re-running the role never
re-downloads an already-installed binary. To upgrade, bump the pin (or run
`perform-updates.yml`), remove `/usr/local/bin/node`, and re-run the role.

## Dependencies

None. See `meta/main.yml` for details.

## Example Playbook

```yaml
- hosts: desktops
  roles:
    - role: nodejs
```

## What This Role Does

Skipped entirely (Node.js install) once `/usr/local/bin/node` exists. On
first install it:

1. Downloads the architecture-specific release archive for the pinned
   `node_version` and verifies it against the pinned per-arch sha256
   checksum using Ansible-native SHA256 checking, which fails atomically
   (leaving no partial file) on mismatch
2. Extracts the verified archive to `/usr/local/lib/nodejs` and symlinks
   `node`, `npm`, `npx`, and `corepack` into `/usr/local/bin`

Regardless of whether Node.js was just installed or already present, it then
installs the global npm packages (`eslint`, `markdownlint-cli`, `prettier`,
`typescript`) system-wide via `npm install --global --prefix /usr/local`,
skipped once already installed.

## License

MIT-0
