# Tasks: Version Update Playbooks

**Input**: Design documents from `/specs/007-version-update-playbooks/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Create directory structure — no logic yet

- [ ] T001 Create directory `playbooks/update-versions/tasks/` and stub `playbooks/update-versions/query-versions.yml` + `perform-updates.yml` (empty placeholder files)
- [ ] T002 Ensure `docs/architecture/` exists (no new directory needed — concept doc is a flat file)

---

## Phase 2: Foundational — Shared Upstream Fetch Task Files

**Purpose**: Shared task files imported by both playbooks. MUST be complete before either playbook can be written.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T003 [P] Create `playbooks/update-versions/tasks/fetch-flutter-version.yml` — fetch `https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json` with `ansible.builtin.uri`; extract the latest stable release entry; set facts `fetched_flutter_version` and `fetched_flutter_sha256`; fail with explicit error naming Flutter manifest as source if no stable entry found or fields missing (FR-012)
- [ ] T004 [P] Create `playbooks/update-versions/tasks/fetch-github-release.yml` — parametrized task file (accepts `github_repo` variable, e.g. `arl/gitmux`); fetch `https://api.github.com/repos/{{ github_repo }}/releases/latest`; set fact `fetched_github_tag` from `tag_name` field; on HTTP 403 with `X-RateLimit-Remaining: 0`, fail with explicit error naming GitHub as source and the rate-limit reset window (FR-011); fail with explicit error naming GitHub as source if `tag_name` missing (FR-012)
- [ ] T005 [P] Create `playbooks/update-versions/tasks/fetch-java-version.yml` — fetch `https://api.sdkman.io/2/candidates/java/linuxx64/versions/all` as raw text with `ansible.builtin.uri` (`return_content: true`); split on `,`; filter with regex `^{{ java_sdkman_major }}\.\d+\.\d+-tem$`; sort with `community.general.version_sort`; take `last`; set fact `fetched_java_identifier`; fail with explicit error naming SDKMAN as source if filtered list is empty (no matching version found) (FR-012)
- [ ] T006 [P] Create `playbooks/update-versions/tasks/fetch-android-version.yml` — fetch `https://developer.android.com/studio` with `ansible.builtin.uri`; extract cmdline-tools build number and SHA-1 via regex from HTML body; set facts `fetched_android_build` and `fetched_android_sha1`; fail with explicit error naming the Android developer page as source if parsing fails (FR-012)

**Checkpoint**: All four fetch task files complete — playbook authoring can begin

---

## Phase 3: User Story 1 — Detect Stale Version Pins (Priority: P1) 🎯 MVP

**Goal**: Query all upstream sources, compare to current pinned values, report drift to stdout, exit non-zero if any version is stale.

**Independent Test**: Run `ansible-playbook playbooks/update-versions/query-versions.yml` against a repository where `flutter_version` is known to be one version behind upstream. Verify stdout names Flutter as stale and the playbook exits non-zero.

### Implementation

- [ ] T007 [US1] Write `playbooks/update-versions/query-versions.yml` — `hosts: localhost`, `gather_facts: false`; import each fetch task file with correct parameters; read current pinned values from `roles/*/defaults/main.yml` using `ansible.builtin.slurp` + `b64decode` + `regex_search`; compare fetched vs current per tracked tool as plain string equality (GitHub `tag_name` already includes the `v` prefix matching `tmux_gitmux_version` / `tmux_font_version` defaults; Flutter and Java values are pin-format identical to upstream — no normalization required); report results per tool via `ansible.builtin.debug`; use `ansible.builtin.fail` (or `any_errors_fatal`) to exit non-zero when any version is stale

**Checkpoint**: Running `query-versions.yml` reports accurate drift for all five tracked tools. Exits 0 when all current, non-zero when any stale.

---

## Phase 4: User Story 2 — Apply Version Updates (Priority: P2)

**Goal**: Fetch latest versions and checksums from all upstream sources and write them into role defaults files using `ansible.builtin.replace`. No commits created.

**Independent Test**: Manually set `flutter_version` in `roles/flutter/defaults/main.yml` to an old value. Run `ansible-playbook playbooks/update-versions/perform-updates.yml`. Verify `flutter_version` and `flutter_sha256` are both updated to current upstream values. Verify `git diff` shows only the two changed lines. Verify no git commit was created. Run `perform-updates.yml` again and verify no further changes (idempotency).

### Implementation

- [ ] T008 [US2] Write `playbooks/update-versions/perform-updates.yml` — `hosts: localhost`, `gather_facts: false`; import each fetch task file with correct parameters; for every tracked tool, apply `ansible.builtin.replace` to update `version_key` value in the role defaults file; for tools with a paired checksum, apply a second `ansible.builtin.replace` for `checksum_key`; version + checksum replace tasks for the same tool MUST run sequentially and be grouped together

**Checkpoint**: Running `perform-updates.yml` updates all stale version pins and paired checksums. Second run makes no changes (idempotent). No git commit created.

---

## Phase 5: User Story 3 — Concept Documentation (Priority: P3)

**Goal**: Create `docs/architecture/version-update-playbooks.md` using the agreed section structure.

**Independent Test**: A maintainer unfamiliar with the feature can read the document and successfully run both playbooks without additional guidance.

### Implementation

- [ ] T009 [US3] Create `docs/architecture/version-update-playbooks.md` using the following section structure:
  - **Problem Statement** (Problem Description / Functional Requirements / Architecture Goals)
  - **Solution** (Context and Influencing Factors / Options in Solution Space / Chosen Solution / Sources for Further Information)
  - **Usage** (Prerequisites / Running query-versions.yml / Running perform-updates.yml)
  - **Outlook** (Open Points / Next Steps)
  - Content must cover: per-tool upstream sources, unauthenticated GitHub API constraint, Android HTML scraping risk (reference TD-009), Java same-major patch tracking policy, planned GitHub Actions integration as next step

**Checkpoint**: Document created. Covers all tracked tools and all known constraints.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T010 Run `review-documentation-here` skill on `docs/architecture/version-update-playbooks.md` per constitution Documentation Standards — complete before format-markdown
- [ ] T011 [P] Run `format-markdown` skill on `docs/architecture/version-update-playbooks.md` per Principle VI
- [ ] T012 [P] Close beads task `9kv` (original tracking issue: "Establish update mechanism for pinned version numbers in role defaults")
- [ ] T013 Verify quickstart.md workflow end-to-end: run `query-versions.yml`, confirm output, run `perform-updates.yml`, confirm `git diff` shows only version/checksum lines changed, run `perform-updates.yml` again, confirm no changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — can start after all fetch task files are complete
- **US2 (Phase 4)**: Depends on Phase 2 — can start after US1 (fetch files already proven by US1)
- **US3 (Phase 5)**: Depends on Phase 2 (needs complete picture of all sources) — can run in parallel with US1/US2
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2. Independent.
- **US2 (P2)**: Depends on Phase 2. Logically sequenced after US1 (US1 proves fetch files work).
- **US3 (P3)**: Depends on Phase 2 context. Independent of US1/US2 implementation.

### Parallel Opportunities

- T003, T004, T005, T006 — all Phase 2 fetch task files: fully parallel (different files)
- T009 (concept doc) — can start once Phase 2 complete, parallel with T007/T008
- T010, T011, T012 — Polish: T011 and T012 parallel after T010 completes

---

## Parallel Example: Phase 2 Fetch Task Files

```bash
# All four can launch simultaneously:
Task: "Create playbooks/update-versions/tasks/fetch-flutter-version.yml"
Task: "Create playbooks/update-versions/tasks/fetch-github-release.yml"
Task: "Create playbooks/update-versions/tasks/fetch-java-version.yml"
Task: "Create playbooks/update-versions/tasks/fetch-android-version.yml"
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational fetch task files
3. Complete Phase 3: `query-versions.yml`
4. **STOP and VALIDATE**: Run against known stale pin; verify report and exit code
5. Merge if query-only capability is sufficient

### Full Increment 1

1. Setup → Foundational → US1 (`query-versions.yml`)
2. US2 (`perform-updates.yml`) — builds on proven fetch files
3. US3 (concept documentation) — parallel with US2
4. Polish

---

## Notes

- [P] tasks have no file conflicts and can run simultaneously
- `community.general.version_sort` is available — `community.general` already in `requirements.yml`
- Fetch task files set named facts; playbooks reference those facts — this is the shared-logic contract
- `ansible.builtin.replace` is idempotent: no match = no change; run twice = no second change
- Android HTML scraping is the only fragile task — if T006 proves intractable, defer Android to a subsequent increment and document the gap
- Commit after each phase using the `commit` skill per Principle V
