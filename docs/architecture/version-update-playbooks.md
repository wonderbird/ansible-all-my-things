# Version Update Playbooks

## Problem Statement

### Problem Description

Role defaults files in this repository pin exact version strings and
checksums for tools installed by Ansible roles. Without a structured
process to detect and apply upstream updates, pins silently drift
behind current releases, exposing provisioned machines to known
security vulnerabilities and missing features.

Checking each tracked tool by hand is error-prone and often skipped:
the tools publish their releases through several different kinds of
upstream source, each with its own API shape and its own failure modes.

### Functional Requirements

- **FR-001**: Detect stale version pins for all tracked tools by
  comparing role defaults against upstream sources.
- **FR-002**: Exit non-zero when any pin is stale; exit zero when
  all are current.
- **FR-003**: Apply version and checksum updates to role defaults
  files in-place.
- **FR-004**: Update version and paired checksum together (Flutter
  sha256, Android sha1).
- **FR-005**: Create no git commits — the maintainer retains full
  control over committing.
- **FR-006**: Share upstream-fetch logic between both playbooks (no
  duplication).
- **FR-007**: Isolate Android scraping logic in a separate task file
  to contain HTML-scraping fragility.
- **FR-008**: Run entirely on the control node (localhost) — no
  managed hosts required.
- **FR-011**: Fail fast on GitHub API rate limit (HTTP 403) with an
  explicit error naming the reset window.
- **FR-012**: Fail with an explicit error naming the upstream source
  if any API response cannot be parsed.

### Architecture Goals

- Maintenance playbooks run on localhost — they do not configure
  managed hosts and do not require a managed-host connection.
- Upstream-fetch logic lives in shared task files imported by both
  playbooks, following the same `playbooks/<operation>/tasks/`
  convention as `playbooks/backup/` and `playbooks/restore/`.
- The operator reviews `git diff` after the update playbook runs and
  commits manually.

---

## Solution

### Context and Influencing Factors

- Tracked tools publish through several kinds of upstream source, and
  the kind — not the individual tool — is what determines the fetch
  strategy. Each kind has a `fetch-*.yml` file in
  `playbooks/update-versions/tasks/` that implements it, so the current
  set of kinds, and which tool uses which, is read from that directory
  rather than restated here.
- Obsidian is tracked through the vendor's desktop release feed rather
  than the shared GitHub Releases oracle, because its repository
  publishes two release lines from one tag namespace and the newest tag
  is regularly one with no `.deb` — see
  [`roles/obsidian/DESIGN.md`](../../roles/obsidian/DESIGN.md).
- GitHub API access is unauthenticated — the 60 requests/hour rate
  limit is sufficient for manual maintenance runs but must be handled
  explicitly.
- Google does not publish a machine-readable manifest for Android
  cmdline-tools; HTML scraping is the only available method.
- Java tracking follows a same-major patch strategy: the latest patch
  release of the currently pinned major version (Java 21). Major
  version upgrades remain a manual decision.
- Android SHA-1 is the only checksum published by Google for
  cmdline-tools. This is an accepted risk documented in
  `docs/architecture/technical-debt/technical-debt.md` as TD-009.
- `community.general.version_sort` is already present in
  `requirements.yml` — no new dependency.

### Options in Solution Space

| Option | Assessment |
| ------ | ---------- |
| Shell scripts per tool | No idempotency guarantees; duplicates logic; no Ansible integration |
| Single monolithic playbook | All fetch logic inline; cannot isolate the HTML-scraping fragility in its own task file |
| Shared task files imported by two playbooks | Both playbooks share one copy of the fetch logic, and the scraping stays isolated; follows project convention; chosen |
| Role wrapping fetch logic | Adds indirection with no reuse benefit; violates Principle IV (YAGNI) |

### Chosen Solution

See
[`checksum-verification-pattern.md`](concepts/checksum-verification-pattern.md)
for how a role verifies a checksum for a version this mechanism has
already pinned — this document covers resolving and writing the pin;
that one covers consuming it.

One playbook — `perform-updates.yml`, which resolves upstream versions and
rewrites the defaults files in place, creating no commits — reads a registry
of tracked tools and a directory of task files:

```text
playbooks/update-versions/
├── perform-updates.yml
├── vars/
│   └── tools.yml
├── tasks/
│   ├── preflight.yml
│   ├── read-current-pins*.yml
│   ├── fetch-tool.yml
│   ├── apply-tool.yml
│   ├── resolve-checksum.yml
│   ├── fetch-*.yml
│   ├── write-pins.yml
│   ├── record-tool-failure.yml
│   └── report-update-failures.yml
└── tests/
```

`tests/` holds the harnesses for the shared task files, with its own minimal
Ansible configuration, so they run without the vault secret the repository root
configuration expects. CI runs them, and `scripts/ci-local.sh` runs the same set
plus a syntax check of both playbooks and a network-free run of the real task
files over a fixture registry — the gate a change to this mechanism must pass
before it is committed, because CI never runs either playbook for real.

The authoritative enumeration of **tracked tools** is `vars/tools.yml`. Each
entry names the role whose defaults carry the pins, the task file that queries
the upstream source and its arguments, every output the tool consumes, the
digests it needs and the pins it writes. Neither playbook contains per-tool
tasks: both loop over the registry's keys and include the same shared task
files, so the two cannot disagree about which tools exist, and adding a tool is
one entry rather than an edit in each playbook.

The loop iterates tool **names**, never whole entries. A loop over entries
templates every expression of every entry before the first task runs, which
happens outside any block, where no rescue can catch the failure.

Each `fetch-*.yml` file implements one kind of upstream query and is
parametrized wherever more than one tool can use it. The directory listing is
the authoritative catalogue; it is not restated here.

`tasks/preflight.yml` runs first in both plays and validates the whole registry
before anything is queried: entry shape, unique pin names, per-architecture
agreement between a pin and the digest it is written from, an asset claim for
every GitHub release fetch, and that every role carrying a version or checksum
pin is registered at all. A rule checked inside the per-tool loop would never
run for a tool whose fetch failed, which is exactly when a malformed entry
matters.

Pre-flight reads the registry a second time through a lookup rather than
through the loaded variable, and validates that copy. A value loaded from
`vars_files` is a trusted template, so merely reading it renders it — and a
registry value renders to "`_fetched` is undefined" outside a tool's block,
which would end the play before it starts. A lookup copy is untrusted, so its
values stay as written and can be inspected as text.

Two of those task files are worth describing by their selection rule,
because choosing wrongly is how a tool gets mis-pinned:

`fetch-github-release.yml` is parametrized by a `github_repo` variable
and resolves `GET /releases/latest`. That is the right oracle only for a
repository whose latest tag always carries the asset the caller needs. A
repository publishing more than one release line from one tag namespace
breaks that assumption, which is why Obsidian has its own task file
instead. For every other GitHub-backed tool, the guard described next
keeps that assumption from failing silently.

`fetch-checksum-from-file.yml` is parametrized by `checksum_file_url` and
`checksum_target_filename`, and is used instead of a local
download-and-hash when, and only when, upstream publishes a checksums
file covering the exact asset this project consumes. Where a project
publishes both a combined checksums file and a per-archive
`<filename>.sha256` sidecar, the sidecar is the one to wire: a combined
file has been renamed across releases in at least one tracked project,
and one of those spellings carried hashes that did not match the
archives. A filename derived from the archive itself is the stable
choice. The task fails loudly (Principle XII) if the target filename has
no matching line. Tools whose upstream publishes no checksums file
covering the consumed asset keep the download-and-`ansible.builtin.stat`
pattern instead.

Every tool's download, digest and pin write runs through the same loop over
the registry, so a new tool adds an entry rather than a section.

#### Guarding release assets

`fetch-github-release.yml` takes an optional list of patterns in
`required_asset_regexes`. Each pattern must match the name of at least one
asset of the resolved release, or the include fails naming the repository,
the resolved tag, the failing pattern and how many assets the release has.
The asset list is already fetched and discarded by the API call the task
makes anyway, so the guard costs no additional request against the hourly
unauthenticated budget.

The guard is what turns "the latest release happens to carry what we
install" from an assumption into a checked claim. Without it a release
published from a second release line — the Obsidian shape — is accepted,
and the failure surfaces later as a 404 on a download, after that tool's
section has begun. Patterns therefore describe what the consumer actually
downloads, including downloads performed by the role rather than by the
playbook: for those tools a rename upstream fails at fetch time instead of
at install time on a real machine.

In `perform-updates.yml` the declaration is mandatory. A tool that installs
from somewhere other than the release assets says so in
`release_carries_no_consumed_asset`, whose value is the reason, so the
exemption is visible at the call site rather than implied by silence.
Pre-flight rejects an entry that declares neither, over the whole registry
before anything runs, so a tool whose fetch later fails has still been
checked.

#### Writing pins

`perform-updates.yml` writes every pin through one shared task file,
`tasks/write-pins.yml`, included once per role defaults file with the list
of pins and their new values. A second run when all pins are already
current makes no modifications.

The task file exists because `ansible.builtin.replace` reports `ok` when
its regexp matches nothing. A role that renamed a pin variable used to
leave the matching write silently doing nothing: the pin stopped
following upstream while the run still reported `failed=0`.
`write-pins.yml` therefore validates before it writes. It rejects
malformed input, including values containing a quote, a backslash or a
newline, since values are substituted unescaped. It then reads the
defaults file once and requires each pin to match exactly one line of
the form `<pin>: "<value>"` at the start of a line. Only when every pin
of the file passes does it write them. A renamed, missing or duplicated
pin therefore fails the run with the file, the pin and the match count,
and leaves that defaults file untouched rather than half-updated. The
anchor at the start of a line stops a comment or a similarly named
variable from absorbing the write after a rename.

A failure in `write-pins.yml` is a configuration error in this
repository, never an upstream failure. Each of its tasks declares
`failure_source: configuration`, and the classifier reads that
declaration.

Alternatives considered for this guard:

- Keeping one `replace` per pin and adding an assert-only include per
  tool, enforced by a coverage rule. Rejected: the pin regexp would be
  defined twice and could drift, and the coverage rule would be a new
  semantic invariant.
- Registering each `replace` and asserting, or reading the file back
  after writing. Rejected: a per-site assertion relies on every future
  write remembering it, and a read-back detects a gap only after other
  pins of the same file were already written.
- Computing the new file content with `regex_replace` and writing it with
  one `copy`. Rejected: it still needs the same exactly-once check, is
  harder to read, and hides which pin changed.

The guard only protects writes that go through the task file. A task
that edits a defaults file directly would bypass it;
`scripts/version-update-order/check-write-pins-bypass.py` rejects that
statically in CI (see "Guarding the pin write"). A harness in `tests/`,
run by its own CI job, proves that the task file keeps failing on a
missing, duplicated or malformed pin.

#### Apply-phase ordering

A tool's version pin is never written before the digests that belong with it are
in hand. This is structural: `apply-tool.yml` resolves every digest the tool's
pins reference, asserts that each one resolved, and only then includes
`write-pins.yml` — there is one apply path, and it cannot be written in the
wrong order.

Which digest belongs to which tool is structural for the same reason: digests are
bound per tool inside that tool's own block, so a tool that resolves fewer than
its pins reference fails the assert instead of inheriting the value of the tool
that ran before.

### Sources for Further Information

- Flutter release manifest: <https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json>
- GitHub Releases API: <https://docs.github.com/en/rest/releases/releases#get-the-latest-release>
- Obsidian desktop release feed: <https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/desktop-releases.json>
- SDKMAN REST API: <https://api.sdkman.io/2/candidates/java/linuxx64/versions/all>
- Android developer page: <https://developer.android.com/studio#command-line-tools-only>
- Technical debt entry (TD-009):
  `docs/architecture/technical-debt/technical-debt.md`

---

## Usage

### Prerequisites

- Ansible-core >= 2.19.0 installed on the control node
- `community.general` collection installed:
  `ansible-galaxy collection install -r requirements.yml`
- Network access to all tracked tools' upstream sources from the control node
- Run from the repository root

### Running perform-updates.yml

Fetches current upstream versions and writes them into role defaults
files. No git commit is created.

```bash
ansible-playbook playbooks/update-versions/perform-updates.yml
```

After the playbook completes, review the diff and commit manually:

```bash
git diff roles/
git add roles/
git commit  # using the commit skill for conventional commit format
```

Running `perform-updates.yml` a second time when all pins are already
current produces no changes (idempotent).

---

### Diagnosing a stuck version pin

`perform-updates.yml` isolates the tools from one another: each runs inside a
fetch block and an apply block, and a failure of either is recorded against
that tool instead of ending the play. A third-party failure therefore no longer
hides the tools after it, and the run reports every failure it collected.

When a pin looks stuck, run
`ansible-playbook playbooks/update-versions/perform-updates.yml` and read the
report at the end. It lists, for every failed tool, the phase, the class, the
task that failed and every message that task produced, then the tools that were
updated and the tools that were skipped. A skipped tool is one whose own fetch
failed: it wrote none of its pins, which is deliberate, since a version pin
written without the checksums that belong with it is worse than no update.

The class says whose problem it is:

- `upstream` — a third party failed: a network error, an HTTP status, a release
  without the asset this project installs, a checksums file without the line
  this project needs. Re-run later, or wire the tool to a different source.
- `configuration` — this repository is wrong: a renamed or duplicated pin, an
  undefined variable, a call-site argument of the wrong shape. The run stops at
  the first one of these, because every later tool would be running against a
  broken playbook. Its report still lists the third-party failures collected
  before it.

A 404 is reported as `upstream` and carries a hint, because a mistyped
repository name and a withdrawn release are the same response. Check the
call-site argument as well as the upstream before concluding it is an outage.

Typical third-party breakages are a vendor publishing releases for several
products from one repository, so the latest release carries no artefact for the
platform this repository installs, and a vendor renaming its release archives,
so a checksum lookup or a download URL no longer resolves.

### Classifying a failure

Whether a failure is `upstream` or `configuration` is decided in
`tasks/record-tool-failure.yml` by four ordered rules, first match winning:

1. any message of the failure, including the per-item messages of a looped
   task, reports an undefined variable or a templating error;
2. the failed task declared `failure_source` in its own `vars:`;
3. the failed task's module is `uri` or `get_url`;
4. anything else.

Rules 1 and 4 mean `configuration`, rule 3 means `upstream`, and rule 2 means
whatever the task declared. The order carries the weight. The veto sits above
the declaration, so a task that blames a vendor is still reported as this
repository's defect when it failed on an undefined variable; and the default is
`configuration`, so an unrecognised failure stops the run rather than being
reported as somebody else's problem. A wrong label is worse than a stopped run,
because it is invisible. A `failure_source` value that is neither `upstream`
nor `configuration` — a typo — counts as no declaration at all, so a misspelling
cannot relabel our own defect as an outage.

The declaration is a task property rather than a registry field on purpose. One
shared task file contains third-party tasks and this repository's own input
asserts, and it runs for many tools; a per-tool field could not tell the two
apart, and a tool has no single failure source anyway — its fetch can fail
upstream while its pin write fails on our own defect in the same run.

The rescue passes one extracted value, never the whole `vars` dict: rendering
that dict inside a rescue raises a *sibling* variable's undefined error there
and ends the play past the isolation, and a `default({})` does not protect,
because the dict itself renders.

Rule 3 covers downloads without depending on anyone remembering a convention,
and it is a deliberate blind spot: it reports **every** non-templating
`uri`/`get_url` failure as upstream, including an unwritable destination, a bad
mode, a `status_code` list that does not match reality and a checksum mismatch,
which are all this repository's own errors. The alternative — treating them as
configuration errors — would stop the run every time a download is added
without a declaration, which is the cascade this isolation exists to remove.

One rule therefore binds anyone adding to these playbooks. **A task that can
fail because of a third party declares `failure_source: upstream` in its own
`vars:`**, unless it is a `uri` or `get_url` task, which rule 3 already covers.
An input assert declares nothing, because a bad argument is this repository's
fault and the default already says so. A forgotten declaration therefore stops
the run loudly; it can never mask an outage as success or a defect as an
outage.

### Guarding the pin write

Every pin write goes through `tasks/write-pins.yml`, which checks that the pin
it is about to change exists exactly once. A task that edits a defaults file
directly skips that check, so a renamed pin would silently stop being updated.

That ban cannot be enforced at runtime — a task that never calls
`write-pins.yml` never runs anything that could object — so it is checked
statically by `scripts/version-update-order/check-write-pins-bypass.py` in CI,
over everything under `playbooks/update-versions/` except `write-pins.yml`
itself and the test harnesses. **The ban MUST survive any simplification or
removal of that script**; the minimum replacement is a CI step that fails when a
file-editing module appears outside `write-pins.yml`.

### What guards what

Each guarantee below is enforced at exactly one point. The table names that
point, so a reader can see what would have to change for a guarantee to be
lost.

| Guarantee | Where it lives now |
| --- | --- |
| No network task after a tool's first pin write | Structural: one apply path resolves every digest before the single `write-pins.yml` include |
| A fetch must be attributable to a tool | Structural: the loop variable is the tool |
| The two playbooks track the same tools | Structural: one registry serves both |
| A tool cannot be dropped unnoticed | Pre-flight: every role carrying a pin must be registered |
| A release fetch states what the release must carry | Pre-flight, over the registry |
| A per-architecture pin is fed from its own architecture | Pre-flight, plus per-tool digest binding |
| No file edit outside `write-pins.yml` | `check-write-pins-bypass.py` in CI |

A registered role whose entry names the *wrong* pin names still passes
pre-flight and fails later as a configuration abort: loud, but late. Pin-by-pin
reconciliation between the registry and the role defaults is not done here.

### Check mode is not supported

Both playbooks refuse `--check`, in the first task of the shared pre-flight.
Under check mode `ansible.builtin.uri` skips while `ansible.builtin.get_url`
still performs its request, so a check run of `perform-updates.yml` mixes real
downloads with skipped fetches: `ansible.builtin.uri` skips under check mode
while `ansible.builtin.get_url` still performs its request. The refusal is code
rather than a comment, so the rule cannot be read and ignored.

---

## Outlook

### Open Points

- **Android HTML scraping fragility** (TD-009):
  `fetch-android-version.yml` parses `developer.android.com/studio`
  via regex. If Google restructures the page, the regex will break.
  No structured API alternative exists at this time. The scraping lives
  in its own task file to contain the blast radius.
- **Unauthenticated GitHub API**: The 60 requests/hour limit is
  sufficient for manual runs. If CI integration is added, a GitHub
  token should be introduced to raise the limit to
  5,000 requests/hour.
- **Java major version strategy**: The playbooks derive the major
  version from the currently pinned `java_sdkman_identifier` and
  track only same-major patches. A major version upgrade (e.g.,
  Java 21 → Java 25) requires a manual update to the defaults file.

### Next Steps

- **GitHub Actions integration**: Run `perform-updates.yml` on a
  schedule (e.g., weekly) and open a pull request automatically with the
  pins it moved. This is the primary planned next step, and it would need
  an authenticated GitHub token: the run costs twelve requests against the
  sixty an hour an unauthenticated caller is allowed.
- **Per-role targeting**: Add optional role-filtering to update only
  a subset of tools in a single run.
- **Checksum algorithm expansion**: Flutter and Android currently use
  sha256 and sha1 respectively. If additional tools with sha512 or
  other algorithms are added, the pin-write pattern in
  `perform-updates.yml` can be extended without structural changes.
