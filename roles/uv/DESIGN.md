<!-- SPDX-License-Identifier: MIT-0 -->
# uv — Design

Non-obvious decisions for the `uv` role.

## Integrity Model

Upstream publishes a `<archive>.sha256` sidecar next to every release archive,
in GNU `sha256sum` format. The role pins one SHA-256 per supported
architecture, taken from those sidecars. The version-update mechanism reads
the sidecars on every version bump, so no archive is downloaded and hashed
locally just to refresh a pin.

The per-archive sidecar is used rather than the release's combined checksum
file because the sidecar names exactly the archive the role installs.

HTTPS to `github.com` plus the pinned per-architecture SHA-256 is the integrity
chain. The download step verifies the archive against the pinned digest, so a
tampered or corrupted archive fails before extraction and no binary is
written. The checksum is never fetched at converge time, so a converge cannot
silently trust a newer release.

## Idempotency: Version Compare, Not File Presence

The role installs when `uv` or `uvx` is missing, or when `uv` reports a
version other than the pin. Checking file presence alone would make a re-run a
no-op too, but then a pin bump written by the version-update mechanism would
never reach a host that already has uv: only fresh hosts would get the new
version. Comparing the reported version makes a pin bump upgrade existing
hosts, and checking that both binaries exist repairs a host that lost one of
them.

Only `uv` is asked for its version. `uvx` is a thin launcher that hands over
to its sibling `uv`, so `uvx --version` reports the version of `uv`, not of
itself, and cannot tell a stale `uvx` from a current one. Both binaries come
from the same archive and are always installed together.

The version is compared exactly, as the second field of `uv --version`
(`uv <version> (<target triple>)`), not as a substring, so a pin can never match
a longer version that merely starts with it. Output that does not have this
shape stops the play with an error naming the output and how to recover.
Treating it as "not installed" instead would reinstall on every run without
ever saying why.

Once both binaries are present and `uv` carries the pinned version, every
expensive step is skipped, so a re-run is a no-op. Molecule's `idempotence`
phase enforces this.

## Why Extract to a Staging Directory and Copy

Each release archive holds a directory named after the target triple, with
`uv` and `uvx` inside. Its tar headers record the upstream build user as owner,
not root. Extracting straight into `/usr/local/bin` would carry that owner onto
system binaries on hosts where the numeric ID maps to a real account, which
could then replace them.

The role therefore downloads and extracts into a staging directory and copies
the binaries into `/usr/local/bin` with an explicit `root:root` owner and
mode `0755`. The copy also replaces each binary by rename, so a running `uv`
is never overwritten in place.

The staging directory is created fresh for each install: root-owned, mode
`0700`, with a random name. A
fixed path in world-writable `/tmp` could be created first by another local
user, who would then own it and could swap the binaries between extraction and
the copy into `/usr/local/bin`.

The staging directory is removed after every install attempt, successful or
not, so nothing accumulates in `/tmp` across runs or version bumps.

The install gate looks at presence and version, not ownership: a binary whose
owner was changed after installation is not repaired by a re-run.

## Why No Dependency on the `python` Role

uv is a self-contained binary. It neither needs a system Python to run nor
installs into one, and it downloads and manages its own Python versions when a
project asks for one. The profile orders it after `python` for readability
only, so the relationship is not declared in `meta/main.yml`.

## Version-Update Integration

The role registers with the project-wide version-update mechanism:

- The registry entry names the shared GitHub-release task, the repository it
  queries, and the archives and sidecars the release must carry.
- On a version bump the mechanism writes the new tag and the digest of every
  supported archive, read from that release's per-archive sidecars, together
  in one update.

## Why Not Upstream's Installer or a Package

Upstream's documented install is a script piped to a shell, which downloads the
same release archive and writes into the invoking user's home. It verifies
nothing the role does not, and it is not idempotent. uv publishes no Debian
package, and installing it with `pip` or `pipx` would tie it to a system Python
it does not need. A checksum-pinned release archive is the minimum trusted,
idempotent install.
