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
  strategy:
  - **GitHub Releases REST API**, for anything that tags releases on
    GitHub. This is the common case and the reason a single parametrized
    task file covers most tools.
  - **GitHub Commits REST API**, for a project that ships no releases at
    all, where the pin is a commit SHA.
  - **A vendor-published JSON document**, where the vendor maintains a
    machine-readable release feed of its own. Preferred over the GitHub
    API whenever the vendor's feed answers a question the GitHub API
    cannot.
  - **A third-party distribution REST API**, where the tool is consumed
    through a distributor rather than from its own releases.
  - **HTML scraping**, only where no machine-readable source exists at
    all. Deliberately isolated per FR-007, because it is the most
    fragile kind.

  Which tool uses which is not restated here; it is visible in the
  `tasks/fetch-*.yml` file each tool's query task includes.
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
| Single monolithic playbook | All fetch logic inline; harder to isolate Android fragility (violates FR-007) |
| Shared task files imported by two playbooks | Satisfies FR-006 and FR-007; follows project convention; chosen |
| Role wrapping fetch logic | Adds indirection with no reuse benefit; violates Principle IV (YAGNI) |

### Chosen Solution

See
[`checksum-verification-pattern.md`](concepts/checksum-verification-pattern.md)
for how a role verifies a checksum for a version this mechanism has
already pinned — this document covers resolving and writing the pin;
that one covers consuming it.

Two playbooks — `query-versions.yml` (detect drift, report, exit
non-zero if stale) and `perform-updates.yml` (apply updates in place,
create no commits) — share one directory of upstream-fetch task files:

```text
playbooks/update-versions/
├── query-versions.yml
├── perform-updates.yml
└── tasks/
    └── fetch-*.yml
```

Each task file in `tasks/` implements one fetch strategy and sets
`fetched_*` facts for its callers. A file is parametrized and shared
whenever more than one tool can use it — this is what satisfies FR-006 —
and tool-specific only where the upstream shape leaves no choice. The
directory listing is the authoritative catalogue; it is not restated
here.

The authoritative enumeration of **tracked tools** is the stale-check
`when:` list in `query-versions.yml`. It names, for each tool, the role,
the pinned variable and the upstream source it is compared against.
`scripts/version-update-order/check-version-update-order.py` derives its
own expected tool count from that same list rather than carrying a
second copy, and this document follows the same principle: read
`query-versions.yml` for the current set.

Two of those task files are worth describing by their selection rule,
because choosing wrongly is how a tool gets mis-pinned:

`fetch-github-release.yml` is parametrized by a `github_repo` variable
and resolves `GET /releases/latest`. That is the right oracle only for a
repository whose latest tag always carries the asset the caller needs. A
repository publishing more than one release line from one tag namespace
breaks that assumption, which is why Obsidian has its own task file
instead. Making the shared file take an optional required-asset guard —
it already fetches and discards the asset list — would turn a future
asset-less release into a named fetch-phase failure before any write, for
any GitHub-backed tool; that is tracked in `ansible-all-my-things-nton`.

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

Beyond that shared fetch step, `query-versions.yml`/`perform-updates.yml`
still use a per-tool copy-paste convention for the download+stat+replace
triples. This is retained deliberately at the current tool count: a
data-driven tool-registry loop was evaluated and not judged worth the
added indirection (tracked in `ansible-all-my-things-3ikt`).

`perform-updates.yml` uses `ansible.builtin.replace` for idempotent
in-place edits. A second run when all pins are already current makes
no modifications.

#### Apply-phase ordering contract

Within a tool's section of `perform-updates.yml`, no network or checksum
task may follow that tool's first `replace`, so a tool's version pin is
never written before the checksums that belong with it are in hand.
Further invariants protect the shared `fetched_checksum` fact and the
pairing of per-architecture values.

The full contract, why each invariant exists, and the checker that
enforces it in CI are documented in
[`scripts/version-update-order/README.md`](../../scripts/version-update-order/README.md).

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

### Running query-versions.yml

Detects which pinned versions are stale. Exits 0 if all are current;
exits non-zero if any are stale.

```bash
ansible-playbook playbooks/update-versions/query-versions.yml
```

Output example (stale pin):

```text
ok: [localhost] => {
    "msg": "Flutter SDK: current=3.29.0, upstream=3.41.6, status=STALE"
}
...
FAILED! => {"msg": "One or more version pins are stale. Run perform-updates.yml to apply updates."}
```

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

## Outlook

### Open Points

- **Android HTML scraping fragility** (TD-009):
  `fetch-android-version.yml` parses `developer.android.com/studio`
  via regex. If Google restructures the page, the regex will break.
  No structured API alternative exists at this time. The task file
  is isolated (FR-007) to contain the blast radius.
- **Unauthenticated GitHub API**: The 60 requests/hour limit is
  sufficient for manual runs. If CI integration is added, a GitHub
  token should be introduced to raise the limit to
  5,000 requests/hour.
- **Java major version strategy**: The playbooks derive the major
  version from the currently pinned `java_sdkman_identifier` and
  track only same-major patches. A major version upgrade (e.g.,
  Java 21 → Java 25) requires a manual update to the defaults file.

### Next Steps

- **GitHub Actions integration**: Run `query-versions.yml` on a
  schedule (e.g., weekly) and open a pull request automatically when
  stale pins are detected. This is the primary planned next step.
- **Per-role targeting**: Add optional role-filtering to update only
  a subset of tools in a single run.
- **Checksum algorithm expansion**: Flutter and Android currently use
  sha256 and sha1 respectively. If additional tools with sha512 or
  other algorithms are added, the replace pattern in
  `perform-updates.yml` can be extended without structural changes.
