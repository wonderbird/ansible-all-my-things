<!-- SPDX-License-Identifier: MIT-0 -->
# bun — Design

Non-obvious decisions for the `bun` role.

## Integrity Model

Upstream publishes a combined `SHASUMS256.txt` with every Bun release, covering
each release archive by name. The two SHA-256 values in `defaults/main.yml` are
the digests that file lists for `bun-linux-x64.zip` and
`bun-linux-aarch64.zip`; `playbooks/update-versions/perform-updates.yml` reads
them straight from that file on every version bump, so no archive is downloaded
and hashed locally just to refresh a pin.

HTTPS to `github.com` plus the pinned per-architecture SHA-256 is the integrity
chain. The `get_url` task supplies the matching pin in its `checksum:`
parameter, so a tampered or corrupted archive fails the gate before extraction
and the binary is never written.

Upstream also publishes `SHASUMS256.txt.asc`, a detached PGP signature. The
role does not verify it: doing so would require provisioning and trusting
upstream's signing key on every target host, and the digest already covers the
one archive the role fetches.

## Why the Version Pin Carries the `bun-v` Prefix

Upstream tags releases `bun-v<semver>`, not `v<semver>`. The pin holds the tag
verbatim because that is what the download URL needs and what the shared
GitHub-release fetch task returns. The role strips the prefix only where it
compares against `bun --version`, which reports a bare semver.

## Why `bunx` Is a Symlink

The release archive contains a single executable, `bun`. Upstream's own install
script creates `bunx` as a link to it, and the binary dispatches on the name it
was invoked under — `bunx --version` reports the same version as `bun
--version`. Installing a second copy would double the on-disk size and let the
two entry points drift apart across a partial upgrade. The link is written
unconditionally rather than inside the install guard, so a host whose `bunx`
was removed is repaired on the next run.

## Why the Role Installs `unzip`

Upstream ships the Linux builds as `.zip` only, and `ansible.builtin.unarchive`
shells out to `unzip` for that format. The project's container base image
deliberately bakes in no tool prerequisites
(`playbooks/files/docker/Dockerfile`), so each role installs its own, as
`roles/java` does. The package install sits inside the install guard: a host
that already carries the pinned version needs neither the archive nor the tool
that unpacks it.

## Idempotency

The role considers the install complete when the binary at `bun_install_path`
reports a `--version` string containing the pinned version (after stripping the
`bun-v` prefix). The expensive steps — package install, download, extract, copy
— are guarded by a single `_bun_needs_install` fact derived from that check, so
a re-run on an already-pinned host is a no-op. Molecule's `idempotence` phase
enforces this.

## Why Not a System Package

Bun publishes no Debian or RPM package for Linux; the release artefact is a
static binary archive per GitHub release. Wrapping it in a local `.deb` would
add packaging complexity without improving the integrity story. A direct
archive install gated on the upstream-published SHA-256 is the minimum viable
trusted install.

## Why a Role of Its Own

Bun is a general-purpose JavaScript runtime with uses beyond any single
consumer, so it is its own single-purpose role alongside `nodejs`, `rtk` and
`opencode`, rather than an install step hidden inside the role that first
needed it.
