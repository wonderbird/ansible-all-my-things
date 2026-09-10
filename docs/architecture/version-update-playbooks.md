# Version Update Playbooks

## Problem Statement

### Problem Description

Role defaults files in this repository pin exact version strings and
checksums for tools installed by Ansible roles. Without a structured
process to detect and apply upstream updates, pins silently drift
behind current releases, exposing provisioned machines to known
security vulnerabilities and missing features.

Checking each tracked tool across five upstream source types by hand —
each with a different API shape — is error-prone and often skipped.

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

- The tracked tools use five distinct upstream source types:
  vendor-published JSON documents (the Flutter release manifest, the
  Node.js dist index, the Claude Code per-version manifest, and the
  Obsidian desktop release feed), GitHub Releases REST API (gitmux, Nerd
  Fonts, Dolt, OpenCode, GitHub CLI, rtk, bd, bv, br, specify-cli,
  direnv, and — for the release tag only — Claude Code), GitHub Commits
  REST API (skill-manager, which ships no releases), SDKMAN REST API
  (Java), and HTML scraping (Android cmdline-tools).
- `obsidianmd/obsidian-releases` publishes the Android and the desktop
  release lines from one repository, so its GitHub "latest release" is
  regularly an Android tag whose assets contain no `.deb`. Obsidian is
  therefore tracked through the vendor's own desktop feed rather than
  through the shared GitHub Releases oracle.
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

Two playbooks share these upstream-fetch task files:

```text
playbooks/update-versions/
├── query-versions.yml           # Detect drift; report; exit non-zero if stale
├── perform-updates.yml          # Apply updates to role defaults; no commits
└── tasks/
    ├── fetch-flutter-version.yml     # Flutter JSON manifest → version + sha256
    ├── fetch-github-release.yml      # GitHub /releases/latest → tag_name (parametrized)
    ├── fetch-java-version.yml        # SDKMAN REST API → latest same-major tem release
    ├── fetch-android-version.yml     # HTML scrape developer.android.com → build + sha1
    ├── fetch-claude-code-version.yml # Per-version manifest.json → version + checksums
    ├── fetch-obsidian-version.yml    # Obsidian desktop feed → v-prefixed release tag
    ├── fetch-nodejs-version.yml      # nodejs.org dist index → latest LTS version
    ├── fetch-checksum-from-file.yml  # Upstream checksums file → sha256 (parametrized)
    └── fetch-github-commit-sha.yml   # GitHub /commits/{ref} → HEAD commit SHA (parametrized)
```

Tracked tools and their upstream sources:

| Tool | Role | version\_key | checksum\_key | Upstream source |
| ---- | ---- | ------------ | ------------- | --------------- |
| Flutter SDK | `flutter` | `flutter_version` | `flutter_sha256` (sha256) | `storage.googleapis.com` Flutter JSON manifest |
| gitmux | `tmux` | `tmux_gitmux_version` | — | GitHub Releases API (`arl/gitmux`) |
| Nerd Fonts (Hack) | `nerd_font` | `nerd_font_version` | — | GitHub Releases API (`ryanoasis/nerd-fonts`) |
| Android cmdline-tools | `android_studio` | `android_cmdlinetools_build` | `android_cmdlinetools_sha1` (sha1) | HTML scrape `developer.android.com/studio` |
| Java (Temurin) | `java` | `java_sdkman_identifier` | — | SDKMAN REST API |
| Dolt | `dolt_sql_server` | `dolt_version` | `dolt_sha256_amd64` / `dolt_sha256_arm64` (sha256) | GitHub Releases API (`dolthub/dolt`) |
| OpenCode | `opencode` | `opencode_version` | `opencode_sha256_amd64` / `opencode_sha256_arm64` (sha256) | GitHub Releases API (`anomalyco/opencode`) |
| GitHub CLI | `github_cli` | `github_cli_version` | — | GitHub Releases API (`cli/cli`) |
| Obsidian | `obsidian` | `obsidian_version` | `obsidian_sha256_amd64` (sha256) | `desktop-releases.json` feed on `obsidianmd/obsidian-releases@master` |
| rtk | `rtk` | `rtk_version` | `rtk_sha256_x86_64_musl` / `rtk_sha256_aarch64_gnu` (sha256) | version: GitHub Releases API (`rtk-ai/rtk`); checksum: release's `checksums.txt` |
| beads (bd) | `beads_go` | `beads_go_version` | `beads_go_sha256_amd64` / `beads_go_sha256_arm64` (sha256) | version: GitHub Releases API (`gastownhall/beads`); checksum: release's `checksums.txt` |
| beads viewer (bv) | `beads_viewer` | `beads_viewer_version` | `beads_viewer_sha256_amd64` / `beads_viewer_sha256_arm64` (sha256) | version: GitHub Releases API (`Dicklesworthstone/beads_viewer`); checksum: release's `checksums.txt` |
| beads rust (br) | `beads_rust` | `beads_rust_version` | `beads_rust_sha256_amd64` / `beads_rust_sha256_arm64` (sha256) | version: GitHub Releases API (`Dicklesworthstone/beads_rust`); checksum: release's per-archive `<filename>.sha256` sidecars |
| Node.js | `nodejs` | `node_version` | `node_sha256_x64` / `node_sha256_arm64` (sha256) | version: `nodejs.org` dist release index; checksum: `nodejs.org` dist `SHASUMS256.txt` |
| specify-cli | `specify_cli` | `specify_cli_version` | — | GitHub Releases API (`github/spec-kit`) |
| Claude Code | `claude_code` | `claude_code_version` | `claude_code_sha256_linux_x64` / `claude_code_sha256_linux_arm64` (sha256) | Per-version `manifest.json` (`storage.googleapis.com`) |
| Skill Manager (sm) | `skill_manager` | `skill_manager_version` (commit SHA) | — (commit SHA is the pin) | GitHub Commits API (`omrikais/skill-manager`, `master` HEAD) |
| direnv | `direnv` | `direnv_version` | `direnv_sha256_amd64` / `direnv_sha256_arm64` (sha256) | GitHub Releases API (`direnv/direnv`) |

`fetch-github-release.yml` is parametrized via a `github_repo`
variable and called once per GitHub-Releases-backed tool — gitmux, Nerd
Fonts, Dolt, OpenCode, GitHub CLI, rtk, bd, bv, br, specify-cli and
direnv directly, plus Claude Code through
`fetch-claude-code-version.yml`, which nests it for the release tag and
then reads that version's `manifest.json` for the checksums — covering
all twelve with a single shared task file.

It resolves `GET /releases/latest`, which is the wrong oracle for a
repository publishing two release lines from one tag namespace. That is
why Obsidian is not on the list above.

`fetch-checksum-from-file.yml` is likewise parametrized (`checksum_file_url`,
`checksum_target_filename`) and used instead of a local
download-and-hash when, and only when, upstream publishes a checksums
file that covers the exact consumed asset: rtk, bd, and bv each ship a
`checksums.txt` in their GitHub release; br ships one
`<filename>.sha256` sidecar per archive, and those per-archive sidecars
are what is wired here, because br's *combined* checksum file has been
renamed across releases (`checksums.sha256`, then
`SHA256SUMS`/`SHA256SUMS.txt`) and one of those spellings carried hashes
that did not match the actual archives — a filename derived from the
archive itself is the stable choice; Node.js publishes `SHASUMS256.txt`
alongside its dist tarballs.
It fails loudly (Principle XII) if the target filename has no matching
line. Dolt and OpenCode keep the download-and-`ansible.builtin.stat`
pattern because neither publishes a checksums file covering the Linux
CLI tarball this repo installs (OpenCode's `latest-linux.yml` only
carries sha512 hashes for its Electron Desktop installers, not the CLI
archive).

Beyond that shared fetch step, `query-versions.yml`/`perform-updates.yml`
still use a per-tool copy-paste convention for the download+stat+replace
triples (Dolt/OpenCode-style). This is retained deliberately at the
tool count tracked in the table above: a data-driven tool-registry loop
was evaluated and not judged worth the added indirection (tracked in
`ansible-all-my-things-3ikt`).

`perform-updates.yml` uses `ansible.builtin.replace` for idempotent
in-place edits. A second run when all pins are already current makes
no modifications.

#### Apply-phase ordering contract

The apply phase holds three invariants, enforced by
`scripts/check-apply-order.py` and the Playbook Order Lint workflow:

1. **Per-tool ordering.** Within a tool's section, no network or checksum
   task may follow that tool's first `replace`. Ansible has no
   transaction, so an upstream failure part-way through the phase leaves
   a prefix of the tools updated; this invariant keeps each individual
   tool's pin and checksums consistent with one another, which is what
   every role defaults file's "update these together" contract requires.
2. **`fetched_checksum` adjacency.** `fetch-checksum-from-file.yml` sets
   one play-scoped `fetched_checksum` fact that every include overwrites,
   so each `Save … fetched checksum` alias must be the task immediately
   after its own include. Batching the includes would make every alias
   resolve to the last include's value and write the same wrong digest to
   five roles without a single task failing.
3. **Platform-token pairing.** A per-arch pin must be written from a value
   whose own name carries the same platform token, so a transposed
   register or alias pair cannot pass every positional check.

The checker additionally fails closed on an apply-phase fetch it cannot
attribute to a role, and asserts that the number of roles it analysed
equals the number of stale-check clauses in `query-versions.yml`. That
derived count makes it a Constitution II registration check too: a tool
wired into `perform-updates.yml` but not into `query-versions.yml` is
reported by name.

Run it directly with:

```bash
python3 scripts/check-apply-order.py playbooks/update-versions/perform-updates.yml
python3 scripts/test_check_apply_order.py
```

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
