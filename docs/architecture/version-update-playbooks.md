# Version Update Playbooks

## Problem Statement

### Problem Description

Role defaults files in this repository pin exact version strings and
checksums for tools installed by Ansible roles. Without a structured
process to detect and apply upstream updates, pins silently drift
behind current releases, exposing provisioned machines to known
security vulnerabilities and missing features.

Checking five tools across four upstream sources by hand — each with
a different API shape — is error-prone and often skipped.

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

- The five tracked tools use four distinct upstream source types:
  structured JSON (Flutter), GitHub Releases REST API (gitmux, Nerd
  Fonts), SDKMAN REST API (Java), and HTML scraping (Android
  cmdline-tools).
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

Two playbooks share four upstream-fetch task files:

```text
playbooks/update-versions/
├── query-versions.yml           # Detect drift; report; exit non-zero if stale
├── perform-updates.yml          # Apply updates to role defaults; no commits
└── tasks/
    ├── fetch-flutter-version.yml     # Flutter JSON manifest → version + sha256
    ├── fetch-github-release.yml      # GitHub /releases/latest → tag_name (parametrized)
    ├── fetch-java-version.yml        # SDKMAN REST API → latest same-major tem release
    └── fetch-android-version.yml     # HTML scrape developer.android.com → build + sha1
```

Tracked tools and their upstream sources:

| Tool | Role | version\_key | checksum\_key | Upstream source |
| ---- | ---- | ------------ | ------------- | --------------- |
| Flutter SDK | `flutter` | `flutter_version` | `flutter_sha256` (sha256) | `storage.googleapis.com` Flutter JSON manifest |
| gitmux | `tmux` | `tmux_gitmux_version` | — | GitHub Releases API (`arl/gitmux`) |
| Nerd Fonts (Hack) | `tmux` | `tmux_font_version` | — | GitHub Releases API (`ryanoasis/nerd-fonts`) |
| Android cmdline-tools | `android_studio` | `android_cmdlinetools_build` | `android_cmdlinetools_sha1` (sha1) | HTML scrape `developer.android.com/studio` |
| Java (Temurin) | `java` | `java_sdkman_identifier` | — | SDKMAN REST API |

`fetch-github-release.yml` is parametrized via a `github_repo`
variable and called twice (once for gitmux, once for Nerd Fonts),
covering both tools with a single task file.

`perform-updates.yml` uses `ansible.builtin.replace` for idempotent
in-place edits. A second run when all pins are already current makes
no modifications.

### Sources for Further Information

- Flutter release manifest: <https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json>
- GitHub Releases API: <https://docs.github.com/en/rest/releases/releases#get-the-latest-release>
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
- Network access to all five upstream sources from the control node
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
