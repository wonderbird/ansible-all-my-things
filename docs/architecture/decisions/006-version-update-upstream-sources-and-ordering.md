# ADR-006: Version-Update Upstream Sources and Apply-Phase Ordering

Date: 2026-09-10
Status: Accepted
Deciders: Stefan (Product Owner)

## Context and Problem Statement

`playbooks/update-versions/perform-updates.yml` stopped updating
`roles/claude_code/defaults/main.yml`. The `claude_code` logic was correct; the
play aborted earlier, at the Obsidian step, so every apply task after it never
ran — `rtk`, `beads_go`, `beads_viewer`, `beads_rust`, `nodejs`, `specify_cli`,
`claude_code`, `skill_manager` and `direnv`.

Two independent defects met in that one failure.

**The upstream source was wrong for Obsidian.** `obsidianmd/obsidian-releases`
publishes the Android and the desktop release lines from a single repository.
`GET /repos/obsidianmd/obsidian-releases/releases/latest` returned the
Android-only tag `v1.13.8`, whose asset list is exactly
`["Obsidian-1.13.8.apk"]`. The `.deb` download for that tag 404'd.
`tasks/fetch-github-release.yml` resolves "the latest release" and has no
notion of "the latest release that actually carries the asset we need", so it
handed the Android tag downstream. This is a recurring condition, not a
one-off: the two release lines interleave continuously.

**The apply phase wrote pins before it had the values they belong with.** Nine
tools — `dolt_sql_server`, `opencode`, `obsidian`, `rtk`, `beads_go`,
`beads_viewer`, `beads_rust`, `nodejs`, `direnv` — wrote their version pin and
only then fetched that same tool's checksums. When the Obsidian download 404'd,
`obsidian_version` had already been bumped to the new tag while
`obsidian_sha256_amd64` still held the previous version's digest. Every role
defaults file in this repository carries a comment requiring its version and
checksums to be updated together; that contract was breakable by any upstream
outage.

## Decision

### 1. Source the Obsidian desktop version from the vendor's desktop feed

`tasks/fetch-obsidian-version.yml` reads
`https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/desktop-releases.json`,
which tracks the desktop line alone.

The GitHub tag is **derived from the feed's own `downloadUrl`**, not
reconstructed by prefixing `latestVersion` with `v`. `downloadUrl` already
carries the exact tag, and `roles/obsidian/tasks/main.yml` hard-asserts
`obsidian_version is match('^v[0-9]+\.[0-9]+\.[0-9]+')` — the `v` prefix is a
role contract, so deriving it from a real URL is safer than composing it.

The `regex_search` is scoped to the `downloadUrl` field rather than run over
the response body, so a future `beta.downloadUrl` on a GitHub releases path
cannot match. The task fails loud (Principle XII), naming both the variable and
the feed URL, when the match is empty and when `downloadUrl` and
`latestVersion` disagree.

This routes Obsidian around the shared oracle's blind spot rather than fixing
the oracle. The general fix — an optional required-asset guard on
`fetch-github-release.yml`, which already fetches and discards the asset list —
is tracked as a follow-up and would convert a future asset-less release, for
any GitHub-backed tool, into a named fetch-phase failure before any write.

### 2. Establish a per-tool apply-phase ordering invariant, enforced by CI

Within a tool's section in `perform-updates.yml`, no network or checksum task
may follow that tool's first `replace`. Each of the nine affected sections was
reordered; no task body changed.

This is deliberately **not** full atomicity. Ansible has no transaction, so a
local abort mid-phase can still leave a prefix of the tools updated. Partial
progress across tools is in fact wanted: an outage in tool *N* should still
leave tools 1..*N*-1 correctly updated. What the invariant guarantees is that
each individual tool's pin and checksums are consistent with one another, which
is exactly what the defaults files' own contract asks for.

Two further invariants ride along, and both exist because a plausible
"improvement" would silently break correctness:

- **`fetched_checksum` adjacency.** `tasks/fetch-checksum-from-file.yml` sets a
  single play-scoped `fetched_checksum` fact that every include overwrites. Ten
  apply-phase aliases read it immediately after their own include. Hoisting the
  includes without their aliases, or batching them, makes all ten resolve to
  the last include's value: five roles receive the same wrong digest with no
  task failing, `failed=0` holds, and a second run is stably wrong so any
  diff-based idempotency probe passes. The rule binds *any* task that reads the
  fact, not only a `set_fact` alias — deleting an alias and interpolating the
  raw fact straight into a `replace` looks like a tidy-up and produces exactly
  the same corruption.
- **Pairing.** A per-arch pin must be written from a value whose own name
  carries the same platform token, *and* a checksum pin fed from a `fetched_*`
  alias must be fed from its own alias. The platform half catches a reorder
  that transposes `_dolt_amd64_stat` and `_dolt_arm64_stat`, or two
  `fetched_checksum` aliases. The alias half catches a cross-tool swap, where
  the platform tokens agree and only the tool is wrong — bd's amd64 digest
  written into bv's amd64 pin. Both pass every positional check and every
  distinctness check, and fail only at role install time.

`scripts/check-apply-order.py` enforces all three, fails closed on an
apply-phase fetch it cannot attribute to a role, and asserts its analysis
scope. `.github/workflows/playbook-order-lint.yml` runs it, and its own test
suite, on every change to `playbooks/**`.

## Consequences

- Obsidian tracking no longer follows the Android release line.
- `claude_code` and the eight other downstream tools resume updating.
- The write-before-network window closes for all nine affected tools and cannot
  reopen without CI failing.
- The abort cascade itself remains: a fetch failure still aborts the run at that
  point, masking every tool after it. Per-tool failure isolation, which would
  accumulate failures and report them together, is tracked as a follow-up.
- The scope assertion doubles as a Constitution II registration check. Adding a
  nineteenth tool to `perform-updates.yml` without registering it in
  `query-versions.yml` fails the gate with a message naming Constitution II.

## Complexity Exceptions

Two Core Principle exceptions are recorded here, as
`.specify/memory/constitution.md` Governance requires.

### Principle IV (Simplicity/YAGNI): a checker and a CI workflow

Shipping a static analyser and a dedicated workflow is more machinery than the
observed defect strictly demands — the Obsidian source fix alone resolves the
reported symptom.

Justified because the alternative is a nine-section ordering rule maintained by
hand, and the planning of this very change enumerated the affected sections
incorrectly on its first attempt. The two silent-corruption modes above are
invisible to a test run, to `failed=0`, and to an idempotency diff; a human
reviewer reading a 200-line reorder is not a reliable detector for either. The
gate is static, needs no network, no Podman and no pip, and runs in about a
second.

The complexity is also reducible. Parameterizing
`tasks/fetch-checksum-from-file.yml` with a result-variable name would remove
the shared-fact aliasing at its root and let the adjacency check be deleted
outright; it is tracked as a follow-up rather than bundled here, because it
touches six call sites.

### Technology Stack: Python in `scripts/`

The Technology Stack section names Bash for `scripts/`. The checker is Python.

Precedent exists — `scripts/backup/resolve_rtk_db_path.py` and its `test_`
sibling — and the task is structural analysis of YAML task lists, which a Bash
implementation would do worse and less readably. The test file follows the same
naming precedent.

## Known Limitation of the Checker

Attribution of a fetch task to a role works two ways: the `fetched_*` facts the
task interpolates, and, failing that, the stem of an included
`tasks/fetch-<role>-version.yml`. The secondary path requires the file stem to
match the **role directory**, while this repository names such files after the
*tool*: `fetch-android-version.yml` feeds the `android_studio` role.

A future tool following that convention therefore lands in "cannot attribute".
That is noisy rather than dangerous — the checker fails closed, so the gate goes
red and asks for a `fetched_<role>_*` fact or a role-named file, instead of
passing the task over.

One diagnosability quirk rides along. Roles are learned from write tasks, and
the first role a `fetched_*` fact is seen with wins. If a write task
interpolates a foreign tool's fact, that fact stays bound to the wrong role for
the rest of the run, so the ordering check can report a real defect against the
wrong section. The pairing rule above reports the same defect correctly, so the
gate still goes red for the right reason — but a reader following only the
ordering line will be sent to the wrong place.

Both hazards the two enforcement rules above describe would become
unrepresentable if `tasks/fetch-checksum-from-file.yml` took a result-variable
parameter, which is the tracked follow-up that would let the adjacency and
pairing checks be deleted outright.

## Alternatives Considered

**Keep `releases/latest` for Obsidian and page `GET /releases?per_page=N`,
selecting the newest release that contains an `obsidian_*_amd64.deb`.**
Rejected on one ground: "newest" is ambiguous when two release lines interleave
(`published_at` order versus list order). Paging *replaces* the
`releases/latest` call rather than adding to it, so it costs nothing extra, and
its selection rule is better-defined than a vendor file on a branch. Retained as
the recovery path if the feed is ever moved or renamed.

**Pin Obsidian by hand and drop it from the mechanism.** Rejected: Constitution
II requires every version-pinning role to be registered in the version-update
mechanism.

**Hoist every network task out of the apply phase, leaving only `replace`
calls (a global fetch-then-write split).** Rejected. Its one advantage is that
the invariant becomes greppable in a single line. Against that, it *creates*
the `fetched_checksum` aliasing hazard described above, which per-tool
reordering cannot produce; it makes a run all-or-nothing across all tracked
upstreams, discarding the wanted partial-progress behaviour; and it splits each
tool into two halves roughly two hundred lines apart. The greppable-invariant
advantage was obtained for the per-tool reorder instead, by making the
invariant machine-checked rather than greppable.

**Bundle per-tool failure isolation (`block`/`rescue` per tool, accumulating
failures) into this change.** Rejected on diff size and on the risk that a
broad `rescue` masks genuine logic errors such as a typo'd variable name.
Tracked as a follow-up.

**Add a `failed_when` guard to the Obsidian `get_url` naming Obsidian in the
error.** Rejected. On an Ansible module, `failed_when` *replaces* the module's
own failure test, so a guard that did not itself re-assert the 404 would
convert the loud failure that is this decision's whole evidence base into `ok`
— a Principle XII regression in the exact task that exposed the bug. The
existing failure already prints `HTTP Error 404`, the status code and the full
URL, which itself names `obsidianmd/obsidian-releases`. Under the reorder that
`get_url` now runs before Obsidian's first write, which is the property that
actually mattered.

## References

- [`version-update-playbooks.md`](../version-update-playbooks.md) — the
  mechanism's structure, tracked tools, and the apply-phase ordering contract
- [`checksum-verification-pattern.md`](../concepts/checksum-verification-pattern.md)
  — how a role consumes a pin this mechanism writes
- [ADR-002](002-github-actions-pinning-policy.md) — the two-tier action pinning
  policy the new workflow follows
