# Research: Version Update Playbooks

## SDKMAN REST API

**Decision**: Use `GET
https://api.sdkman.io/2/candidates/java/linuxx64/versions/all`, split the
response on commas, filter with regex `^<major>\.\d+\.\d+-tem$`, where
`<major>` is the major version of the currently pinned identifier, sort with
`community.general.version_sort`, take `last`.

**Rationale**: The endpoint is public, unauthenticated, and returns all
available identifiers for a platform. No other public endpoint provides a
filtered or vendor-specific response — all filtering must be done client-side.
Regex match on major version + distribution suffix is the correct approach.
`community.general.version_sort` handles semantic version ordering reliably.

**Alternatives considered**:

- SDKMAN `/versions/list` endpoint — returns an ASCII table for human display,
  not machine-parseable.
- `sdk list java` CLI — requires SDKMAN installed on control node; not available
  in CI/minimal environments.
- Internal `sdkman-state` JSON API — not publicly routed at `api.sdkman.io`.

**Response format**: Plain text, single line, comma-delimited (NOT JSON).
Example excerpt:

```text
11.0.30-tem,11.0.31-tem,17.0.19-tem,21.0.11-tem,25.0.3-tem,...
```

**Version string format**: `{major}.{minor}.{patch}-tem` for stable releases.
Edge case: major-only EA releases appear as `26-tem` (no minor/patch). The
filter regex correctly excludes these.

**Collection dependency**: `community.general.version_sort` — already present in
`requirements.yml` (no new dependency).

---

## Flutter Manifest JSON

**Decision**: Fetch
`https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json`,
extract the entry from `releases` array where `channel == "stable"` and sort by
`release_date` descending; read `version` and `sha256` from the latest entry.

**Rationale**: URL and approach documented in `roles/flutter/defaults/main.yml`
comments. Structured JSON, no scraping required.

**Alternatives considered**: None — Flutter does not expose a `/releases/latest`
API; the manifest JSON is the canonical source.

---

## GitHub Releases API

**Decision**: Use `GET
https://api.github.com/repos/{owner}/{repo}/releases/latest`. Extract `tag_name`
for version. The release endpoint carries no digest; a tool that pins one
declares a checksum source in its registry entry.

**Rationale**: Standard GitHub REST API. No authentication required for public
repos at 60 req/hr. `tag_name` contains the version string including the `v`
prefix (e.g. `v0.11.5`). This matches the existing pin format in
`defaults/main.yml`.

**Reuse**: A single parametrized task file (`fetch-github-release.yml`) serves
every GitHub-release tool whose latest release carries the consumed asset —
same API shape.

---

## Android SDK Command-Line Tools

**Decision**: Scrape `https://developer.android.com/studio`. Isolate in
`fetch-android-version.yml` (separate file, named by the android registry
entry) per FR-007.

**Rationale**: HTML scraping of the download page was chosen; isolation limits
blast radius if Google restructures the page.

**Alternatives**: Google's XML repository manifest lists the same archives and
digests; it is recorded as an open point in
`docs/architecture/version-update-playbooks.md`.

**Known risk**: SHA-1 checksum only (SHA-256 not published). Accepted risk per
TD-009.

---

## Principle II Justification (Role-First)

**Decision**: Maintenance playbooks contain inline task logic (not orchestrating
roles). This is a justified exception.

**Rationale**: Procedural operator tools that query external APIs and modify
local files do not fit the role abstraction. The `playbooks/backup/` and
`playbooks/restore/` directories establish an identical precedent in this
project. Wrapping the logic in a role would add indirection with no reuse
benefit, violating Principle IV (YAGNI).

**Documented in**: Complexity Tracking table in `plan.md`.
