<!-- SPDX-License-Identifier: MIT-0 -->
# direnv — Design

Non-obvious decisions for the `direnv` role.

## Integrity Model

direnv does not publish a separate checksums file for its release binaries,
but GitHub computes and exposes a SHA-256 `digest` for every release asset
via the Releases API. The two SHA-256 values in `defaults/main.yml` are
copied from that API response on first pin (cross-checked locally by
downloading each binary and hashing it) and re-derived the same way by
`playbooks/update-versions/perform-updates.yml` on every version bump.

HTTPS to `github.com` plus a locally pinned SHA-256 is the integrity chain.
The `get_url` task supplies the per-architecture pin in its `checksum:`
parameter, so a tampered or corrupted binary fails the checksum gate before
it is ever written to disk.

## Raw Binary, Not a Tarball

Unlike `opencode` or `nodejs`, direnv's GitHub release assets
(`direnv.linux-amd64`, `direnv.linux-arm64`, ...) are the executable itself,
not an archive. The install task therefore `get_url`s straight to
`direnv_install_path` with `mode: '0755'` — there is no download-to-`/tmp`,
extract, then copy step.

## Idempotency

The role considers the install complete when the binary at
`direnv_install_path` reports a `--version` string containing the pinned
version (after stripping the leading `v`) — same signal shape as `opencode`.
The `get_url` download is guarded by a single `_direnv_needs_install` fact
derived from that check, so a re-run on an already-pinned host skips the
network call entirely.

The per-user `blockinfile` hook task is not gated behind that fact: it must
run on every converge so that a user added after the binary was already
installed still gets the hook, and `blockinfile` is itself idempotent
(no-op, `changed: false`, on a second run with unchanged content).

## Why bash Only

This repository's login users use bash (`playbooks/setup-users.yml` sets
`shell: /bin/bash` for every login user);
direnv also supports zsh, fish, and other shells via different hook
invocations, but adding those hooks would configure a shell nothing in this
repository sets up, violating Principle IV (YAGNI). Add a shell-specific hook
task only when a role in this repository actually configures that shell for
login users.

## Version-Update Integration

The role registers with the project-wide version-update mechanism:

- `query-versions.yml` reads the pinned tag from `defaults/main.yml`,
  fetches the latest GitHub release tag via the shared
  `fetch-github-release.yml` task, and reports STALE if the two differ.
- `perform-updates.yml` writes the new tag and re-downloads both the
  `linux-amd64` and `linux-arm64` binaries to recompute their SHA-256
  values, then writes both pins back into `defaults/main.yml`. The three
  values are always updated together — partial bumps are not possible.

## Why Not a System Package

Ubuntu's `direnv` apt package tracks the distribution's release cadence, not
upstream's, so pinning a specific upstream version (Principle II) would still
require overriding the packaged binary. Installing the upstream release
binary directly, with a local SHA-256 pin, keeps the version pin authoritative
and avoids mixing package-manager and manual-pin ownership of the same file.
