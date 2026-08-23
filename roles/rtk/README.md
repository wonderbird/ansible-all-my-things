<!-- SPDX-License-Identifier: MIT-0 -->
# rtk

Ansible role that installs [rtk (Rust Token Killer)](https://github.com/rtk-ai/rtk),
a token-optimized CLI proxy for AI coding agents, to `/usr/local/bin/rtk`.

rtk's binary is cross-harness — usable from Claude Code, opencode, Codex, and
other agent harnesses — so it is a standalone role rather than bundled into
`claude_code_config`. Initializing rtk's Claude-Code-specific global config
(`rtk init -g`, which writes into `~/.claude`) is done by the
`claude_code_config` role instead — see its `DESIGN.md` for why.

## Requirements

- Ansible 2.19+
- Internet access from target hosts (downloads the release archive)

The version and checksum are pinned in `defaults/main.yml` (`rtk_version`,
`rtk_sha256_x86_64_musl`, `rtk_sha256_aarch64_gnu`), refreshed only by
`playbooks/update-versions/perform-updates.yml`. A `stat` gate short-circuits
the whole download-and-verify block once `/usr/local/bin/rtk` exists, so
re-running the role never re-downloads an already-installed binary. To
upgrade, bump the pin (or run `perform-updates.yml`), remove the binary, and
re-run the role.

## Dependencies

None. See `meta/main.yml` for details.

## Example Playbook

```yaml
- hosts: desktops
  roles:
    - role: rtk
```

## What This Role Does

Skipped entirely once `/usr/local/bin/rtk` exists. On first install it:

1. Downloads the architecture-specific release archive for the pinned
   `rtk_version` and verifies it against the pinned per-triple sha256
   checksum using Ansible-native SHA256 checking, which fails atomically
   (leaving no partial file) on mismatch
2. Extracts the verified `rtk` binary to `/usr/local/bin/rtk`

## License

MIT-0
