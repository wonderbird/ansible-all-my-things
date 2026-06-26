<!-- SPDX-License-Identifier: MIT-0 -->
# opencode — Design

Non-obvious decisions for the `opencode` role.

## Integrity Model

OpenCode does not publish an upstream checksum file for its CLI tarballs.
The two SHA-256 values in `defaults/main.yml` are computed locally on first
pin and re-computed automatically by
`playbooks/update-versions/perform-updates.yml` on every version bump.

HTTPS to `github.com` plus a locally pinned SHA-256 is the integrity chain.
The `get_url` task supplies the per-architecture pin in its `checksum:`
parameter, so a tampered or corrupted tarball fails the checksum gate
before extraction and the binary is never written.

## Why Two Separate Per-Architecture Pins

The role supports both `x86_64` (mapped to upstream's `x64` tarball name) and
`aarch64` (mapped to `arm64`). A single combined "checksum file" pin would
require either:

- downloading a non-existent upstream manifest, or
- running both architectures' downloads to derive a single composite hash.

Pinning each architecture's tarball SHA-256 directly avoids that and keeps
the integrity check local to the one tarball that is actually fetched.

## Idempotency

The role considers the install complete when the binary at
`opencode_install_path` reports a `--version` string containing the pinned
version (after stripping the leading `v`). The expensive steps —
download, extract, copy — are guarded by a single `_opencode_needs_install`
fact derived from that check, so a re-run on an already-pinned host is a
no-op. Molecule's `idempotence` phase enforces this.

## Version-Update Integration

The role registers with the project-wide version-update mechanism:

- `query-versions.yml` reads the pinned tag from `defaults/main.yml`,
  fetches the latest GitHub release tag, and reports STALE if the two
  differ.
- `perform-updates.yml` writes the new tag and re-downloads both the
  `linux-x64` and `linux-arm64` tarballs to recompute their SHA-256 values,
  then writes both pins back into `defaults/main.yml`. The three values are
  always updated together — partial bumps are not possible.

## Why Not a System Package

OpenCode does not ship Debian/RPM packages for Linux. The release artefact
is a static binary tarball published per GitHub release. Wrapping it in a
local `.deb` would add packaging complexity without changing the integrity
story (still no upstream signing). A direct tarball install with a local
SHA-256 pin is the minimum viable trusted install.
