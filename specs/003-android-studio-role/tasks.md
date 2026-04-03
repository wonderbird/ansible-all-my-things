# Tasks: Android Studio Ansible Role

**Input**: Design documents from `/specs/003-android-studio-role/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, quickstart.md ✓

**Tests**: No automated test tasks — spec does not request TDD. Manual
verification steps are documented in `quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create the role directory layout matching the `google_chrome`
two-file convention.

- [x] T001 Create role directory structure `roles/android_studio/meta/` and `roles/android_studio/tasks/`

---

## Phase 2: Foundational — N/A

No blocking prerequisites exist between Setup and User Story 1. This role
requires only the two files created in Phase 1 before implementation can
begin.

---

## Phase 3: User Story 1 — Install Android Studio (P1) 🎯 MVP

**Goal**: A developer adds the `android_studio` role to the playbook and
runs it; Android Studio is installed via snap and launchable on the VM.

**Independent Test**: Run `ansible-playbook configure-linux.yml --limit hobbiton`
against a fresh AMD64 Vagrant VM (roles-only) and verify `snap list android-studio`
returns a single active row. See `quickstart.md` — Isolated role test.

### Implementation for User Story 1

- [x] T002 [P] [US1] Create `roles/android_studio/meta/main.yml`
  with SPDX header and galaxy_info matching plan.md
- [x] T003 [P] [US1] Create `roles/android_studio/tasks/main.yml`
  with a single snap-install task using `community.general.snap`
  (`name: android-studio`, `classic: true`, `state: present`);
  do NOT add `become: true` (see research.md Decision 1)
- [x] T004 [US1] Add `android_studio` role entry to
  `configure-linux-roles.yml` with tag
  `not-supported-on-vagrant-arm64`

**Checkpoint**: US1 is complete when `snap list android-studio` exits
successfully on the target VM after the first playbook run.

---

## Phase 4: User Story 2 — Idempotent Re-runs (Priority: P2)

**Goal**: A second playbook run against a VM that already has Android Studio
installed reports zero `changed` tasks for the `android_studio` role.

**Independent Test**: Run `ansible-playbook configure-linux.yml` twice on
the same AMD64 VM. The second run must show `ok` or `skipped` for all
`android_studio` tasks — never `changed`. See `quickstart.md` — Idempotency
test.

### Implementation for User Story 2

No additional code changes are required. Idempotency is fully implemented
by `community.general.snap` natively in T003 (`tasks/main.yml`): the module
checks snap state before acting and reports `ok` when the snap is already
installed.

**Checkpoint**: US2 is verified when the second playbook run reports no
`changed` tasks for the `android_studio` role.

---

## Phase 5: User Story 3 — Graceful Skip on Non-AMD64 Machines (Priority: P3)

**Goal**: Running the playbook against an ARM64 machine skips all
`android_studio` role tasks without errors.

**Independent Test**: Run `ansible-playbook configure-linux.yml --limit hobbiton
--skip-tags not-supported-on-vagrant-arm64` against an ARM64 Vagrant VM.
All `android_studio` tasks must be skipped; the playbook must complete
without errors. See `quickstart.md` — ARM64 skip test.

### Implementation for User Story 3

No additional code changes are required. The `not-supported-on-vagrant-arm64`
tag applied to the role entry in T004 (`configure-linux-roles.yml`) skips the
entire role when the tag is excluded (consistent with the `google_chrome`
role and `playbooks/setup-homebrew.yml`).

Per FR-007: the tag is applied at the role entry level only — individual
tasks inside `tasks/main.yml` do NOT carry the tag.

**Checkpoint**: US3 is verified when the ARM64 playbook run reports
`skipped` for all `android_studio` role tasks.

---

## Phase 6: User Story 4 — SDK Pre-Provisioned at First Launch (Priority: P2)

**Goal**: After provisioning, the Android Studio first-launch wizard
completes within 30 seconds because all required SDK components are
already present.

**Independent Test**: Launch Android Studio on a freshly provisioned VM
and step through the Standard setup wizard. Measure time from wizard
start to completion. See `quickstart.md` — SDK validation test.

### Implementation for User Story 4

- [ ] T007 [US4] Create
  `roles/android_studio/defaults/main.yml` with SPDX header,
  `android_cmdlinetools_build: "11076708"` and
  `android_cmdlinetools_sha256: "2d2d50857e4eb553af5a6dc3ad507a17adf43d115264b1afc116f95c92e5e258"`
- [ ] T008 [US4] Add task to download cmdline-tools ZIP once
  to `/tmp/commandlinetools-linux-{{ android_cmdlinetools_build }}_latest.zip`
  using `ansible.builtin.get_url`
  with `checksum: "sha256:{{ android_cmdlinetools_sha256 }}"`;
  idempotent via `creates:` guard
- [ ] T009 [US4] Add task to create `~/Android/Sdk` directory
  per user in `desktop_user_names` using
  `ansible.builtin.file`
- [ ] T010 [US4] Add tasks to extract cmdline-tools per user:
  (a) `ansible.builtin.unarchive` extracts ZIP to
  `~/Android/Sdk/cmdline-tools/` (creates nested
  `cmdline-tools/cmdline-tools/`); (b) `ansible.builtin.command`
  renames `cmdline-tools/cmdline-tools/` to `cmdline-tools/latest/`
  with `creates: ~/Android/Sdk/cmdline-tools/latest/bin/sdkmanager`
- [ ] T010a [US4] Add task to detect latest Android API level
  and build-tools version by parsing `sdkmanager --list` output;
  `changed_when: false`; set `JAVA_HOME` to snap-bundled JBR
  (`/snap/android-studio/current/android-studio/jbr`)
- [ ] T011 [US4] Add task to install SDK components
  (`platform-tools`, `platforms;android-{{ latest_api }}`,
  `build-tools;{{ latest_buildtools }}`, `emulator`,
  `sources;android-{{ latest_api }}`) using
  `community.general.android_sdk` with
  `accept_licenses: true` and `sdk_root: ~/Android/Sdk`
  per user, using snap-bundled JBR for Java
- [ ] T012 [US4] Verify idempotency: second run reports `ok`
  for all SDK tasks (FR-012)

**Checkpoint**: US4 is complete when SC-005 passes (wizard ≤ 30 s).

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Update technical debt register to reflect `android_studio`
following the same unpinned-version pattern as existing roles.

- [x] T005 Update
  `docs/architecture/technical-debt/technical-debt.md` TD-003:
  add `roles/android_studio/tasks/main.yml` to affected files
  and note snap-based vs. apt-based idempotency difference
- [x] T006 Add inline comment to `android_studio` role entry
  in `configure-linux-roles.yml` noting FR-008:
  `include_role` callers MUST pass
  `apply: tags: [not-supported-on-vagrant-arm64]`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **User Story 1 (Phase 3)**: Depends on Phase 1 (directory structure must exist)
- **User Story 2 (Phase 4)**: No new implementation; verify after US1 is complete
- **User Story 3 (Phase 5)**: No new implementation; verify after US1 is complete
- **User Story 4 (Phase 6)**: Depends on Phase 3 (snap must be
  installed for JBR Java path)
- **Polish (Phase 7)**: Can proceed once US1 implementation tasks
  (T002–T004) are done

### User Story Dependencies

- **US1 (P1)**: Depends only on Phase 1 (setup)
- **US2 (P2)**: Implemented within US1 (module native idempotency
  in T003) — verification only
- **US3 (P3)**: Implemented within US1 (tag on role entry in T004)
  — verification only
- **US4 (P2)**: Depends on US1 (snap install provides JBR); T007
  must precede T008–T011; T008–T010 are sequential
  (directory → download → extract); T011 depends on T010
  (sdkmanager must exist)

### Within User Story 1

- T001 (directory structure) must complete before T002 and T003
- T002 (`meta/main.yml`) and T003 (`tasks/main.yml`) can run in parallel [P]
- T004 (`configure-linux-roles.yml`) depends on T003 (role must
  exist before being referenced)

### Within User Story 4

- T007 (`defaults/main.yml`) must complete first (variable definition)
- T008 (download cmdline-tools) runs once, no per-user dependency
- T009 (create ANDROID_HOME) → T010 (extract + rename) → T010a
  (detect latest API) → T011 (install SDK) — sequential per-user
  chain; T010 depends on T008; T010a depends on T010 (needs
  sdkmanager); T011 depends on T010a (needs version variables)
- T012 (idempotency verification) runs after T011

---

## Parallel Example: User Story 1

```bash
# After T001 completes, launch T002 and T003 in parallel:
Task T002: "Create roles/android_studio/meta/main.yml"
Task T003: "Create roles/android_studio/tasks/main.yml"

# After both complete, run T004:
Task T004: "Add android_studio entry to configure-linux-roles.yml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 3: User Story 1 (T002, T003, T004)
3. **STOP and VALIDATE**: Run isolated role test per `quickstart.md`
4. Verify `snap list android-studio` on the target VM

### Incremental Delivery

1. Phase 1 + Phase 3 → Role installs Android Studio (MVP)
2. Run idempotency test (Phase 4 verification) → Confirm second run is clean
3. Run ARM64 skip test (Phase 5 verification) → Confirm skip behaviour
4. Phase 6 → SDK pre-provisioning (T007–T012)
5. Phase 7 → Update technical debt register

---

## Notes

- [P] tasks = different files, no shared dependencies
- No automated tests — verification is manual via `quickstart.md`
- Do NOT add `become: true` to the snap install task in `tasks/main.yml`.
  The play in `configure-linux-roles.yml` already sets `become: true`; the
  task inherits privilege escalation from the play.
- All YAML files MUST begin with `#SPDX-License-Identifier: MIT-0`
- Match `google_chrome` role for header, galaxy_info shape, and
  tag placement
- `defaults/main.yml` added for cmdline-tools build number
  variable; no `vars/`, `handlers/`, or `templates/`
  directories (Constitution §IV; see Complexity Tracking)
