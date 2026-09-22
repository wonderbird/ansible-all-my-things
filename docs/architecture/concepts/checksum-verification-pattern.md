<!-- SPDX-License-Identifier: MIT-0 -->

# Checksum-verification pattern for web-hosted installer scripts

Several roles in this repo install a binary tool distributed as a
GitHub release (or an equivalent versioned upstream) rather than a
distro package: `claude_code` (the Claude Code binary), `rtk`,
`beads_go` (`bd`), `beads_viewer` (`bv`), and `nodejs`. This document is
the authoritative source of
truth for the shared verification pattern they follow, so a future tool
doesn't have to rediscover it from scratch.

See [`version-update-playbooks.md`](../version-update-playbooks.md) for
the centralized mechanism (`playbooks/update-versions/`) that keeps each
tool's pin current; this document explains how a role verifies a
checksum for a version that mechanism has already pinned.

## The pattern

This pattern spans two phases, run by two different playbooks:

- **Resolve** (`playbooks/update-versions/perform-updates.yml`, run
  manually/periodically per
  [`version-update-playbooks.md`](../version-update-playbooks.md)):
  determines the current upstream version and its checksum, then writes
  both as static, literal values into the role's `defaults/main.yml`.
  This is the only place a live upstream query happens.
- **Consume** (the role itself, at converge time): reads the
  already-pinned version and checksum literals — never queries upstream
  — and verifies-before-placement.

1. **Assert supported architecture** up front — fail loud (Constitution
   Principle XII) before attempting any download if
   `ansible_facts['architecture']` isn't a key in the role's
   `*_platform_map` (defined in `defaults/main.yml`).
2. **Read the pinned version** from `defaults/main.yml` (e.g.
   `rtk_version`, `beads_go_version`, `node_version`,
   `claude_code_version`) — never resolved live at converge time.
3. **Read the pinned checksum** — see the shapes below; resolved once,
   at maintenance time, by `perform-updates.yml`.
4. **Download and verify**, then only extract/place the artefact after
   verification succeeds.
5. **Gate the whole download block behind a `stat` check** on the
   already-installed artefact (see "Idempotency semantics"
   below) — this avoids redundant re-download/re-extract of the same
   pinned archive on every converge; it is not optional.

## Checksum-source shapes seen in this repo

Different upstreams publish release checksums differently, which
affects how `perform-updates.yml` resolves the pinned literal (see
`ansible-all-my-things-9hzb.6` for an open question on whether
`perform-updates.yml` should fetch+parse a published checksums file
instead of downloading the full archive to self-compute the hash):

| Shape | Example | How `perform-updates.yml` resolves it |
| --- | --- | --- |
| Aggregate `checksums.txt` (sha256sum format, `<hash>  <filename>`) | `rtk-ai/rtk`, `gastownhall/beads`, `Dicklesworthstone/beads_viewer` | Downloads the release archive and self-computes its sha256 via `ansible.builtin.stat`, rather than fetching and parsing the published `checksums.txt` (open question tracked in `ansible-all-my-things-9hzb.6`). |
| `SHASUMS256.txt` | `nodejs.org` | Same self-compute-via-`stat` approach as above. |
| Release manifest JSON (`artifacts[].name`/`.sha256` or `.platforms[].checksum`) | `claude_code`'s own `manifest.json` | Fetched via `uri`, the matching platform's hash extracted with a Jinja expression, asserted present (Constitution Principle XII), and written as a literal into `defaults/main.yml`. |

For the manifest-JSON shape, the Jinja expression
`playbooks/update-versions/tasks/fetch-claude-code-version.yml` uses to
extract the matching platform's hash is:

```jinja
{{ _claude_code_manifest.json.platforms['linux-x64'].checksum }}
```

Regardless of which shape resolved it, every role consumes the result
identically at converge time: a literal `checksum: "sha256:{{
pinned_var }}"` passed to `get_url`. No role passes a live
checksums-file URL to `get_url`'s own URL-lookup form.

## Idempotency semantics: static pin is the rule, not a live-resolve freeze

**The static-pin model is the rule for every tool following this
pattern** (`rtk`, `beads_go` `bd`, `beads_viewer` `bv`, `nodejs`,
`claude_code`): the version *and* its checksum are both explicit literals
in the role's
`defaults/main.yml`, refreshed only by
`playbooks/update-versions/perform-updates.yml` (Constitution
Principle II). The source of truth for what to install is always the
pinned default variable — never a live upstream query made at converge
time. `flutter` and `obsidian`, the reference tools of the
version-update mechanism, follow the same static-pin shape.

A `stat` check on the resulting binary path still gates the whole
download block in every role (`/usr/local/bin/rtk`, `/usr/local/bin/bd`,
`/usr/local/bin/bv`, `/usr/local/bin/node`, or the per-user
`~/.local/bin/claude`). This gate is load-bearing for one narrow
reason: because the pin is already static, the gate carries no
version-drift risk either way — its only job is avoiding a
redundant re-download/re-extract of the same pinned archive on every
converge (`unarchive`/binary placement has no `creates:`-based
idempotency of its own).

Refreshing any tool's pin to a newer upstream release is exclusively
the job of `perform-updates.yml` — see
[`version-update-playbooks.md`](../version-update-playbooks.md) for how
that mechanism resolves and writes each pin. A role never resolves or
upgrades its own pin at converge time.

Separately, the claude_code binary itself ships a background
auto-updater; that risk (drift outside this Ansible-managed pin
entirely) and its mitigation are documented in
`roles/claude_code/DESIGN.md`, not here — this document is scoped to
how the Ansible-managed pin is verified, not to the binary's own
runtime behavior.

## Reference implementations

System-wide install (a single scalar `stat` gate on a version-agnostic
path, no per-user placement) is the preferred default for any new tool
following this pattern, unless a tool has genuine per-user state that
requires otherwise. Every tool in this document follows the same
static-pin, verify-before-placement shape:

- `roles/flutter/tasks/main.yml`, `roles/obsidian/tasks/main.yml` — the
  static-pin reference implementations; version and checksum both
  explicit literals in `defaults/main.yml`.
- `roles/rtk/tasks/main.yml` — `rtk_version` and a per-architecture
  `rtk_sha256_*` literal, stat-gated, single system-wide artefact.
- `roles/beads_go/tasks/main.yml` — `bd` uses a static `beads_go_version`
  pin and per-architecture literal checksums, gated on a single scalar
  `stat` check, installed system-wide to `/usr/local/bin`.
- `roles/beads_viewer/tasks/main.yml` — `bv` uses a static
  `beads_viewer_version` pin and per-architecture literal checksums, gated on
  a single scalar `stat` check, installed system-wide to `/usr/local/bin`.
- `roles/nodejs/tasks/main.yml` — static `node_version` pin and
  per-architecture literal checksums, stat-gated on the
  version-agnostic `/usr/local/bin/node`.
- `roles/claude_code/tasks/install-claude-code.yml` — static
  `claude_code_version` pin and per-architecture literal checksums
  (resolved from the upstream manifest once, at maintenance time, by
  `playbooks/update-versions/tasks/fetch-claude-code-version.yml`), on
  the same stat-gated, verify-before-placement shape as every role
  above.
