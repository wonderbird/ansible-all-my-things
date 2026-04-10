<!-- SPDX-License-Identifier: MIT-0 -->

# Tasks: Java Ansible Role (sdkman + Temurin JDK)

**Input**: Design documents from `/specs/005-java-role/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story. No test tasks are generated
(not requested in the feature specification).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US3)

---

## Phase 1: Setup (Role Skeleton)

**Purpose**: Create the `roles/java/` directory structure before any
content tasks begin.

- [x] T001 Create role directory tree `roles/java/` with subdirectories
  `defaults/`, `meta/`, `tasks/`

---

## Phase 2: Foundational (Role Variables and Metadata)

**Purpose**: Files that every subsequent task depends on — defaults and
meta must exist before `tasks/main.yml` can reference variables, and
DESIGN.md must exist before it can be edited.

**Note**: No user-story work can begin until this phase is complete.

- [x] T002 [P] Write `roles/java/defaults/main.yml` with SPDX header and
  `java_sdkman_identifier: "21.0.7-tem"` per data-model.md
- [x] T003 [P] Write `roles/java/meta/main.yml` with SPDX header and
  `galaxy_info` block following the `android_studio` meta template (FR-011)
- [x] T004 [P] Create `roles/java/DESIGN.md` documenting non-obvious design
  decisions: version-specific idempotency guard path, sdkman init.sh inline
  sourcing, no PATH modification needed, no task-level `become`, ARM64
  compatibility (FR-012)

**Checkpoint**: Defaults, metadata, and DESIGN.md are in place.

---

## Phase 3: User Story 1 — Developer Workstation Has Java After Provisioning (P1) — MVP

**Goal**: Every user in `desktop_user_names` can run `java -version` and
see "Temurin" in the output after a single playbook run.

**Independent Test**: Provision a fresh Ubuntu VM (AMD64 or ARM64) with the
`java` role applied; log in as a provisioned user and run
`java -version 2>&1 | grep -i temurin` — expect exit code 0 with "Temurin"
in the output.

### Implementation — US1

- [x] T005 [US1] Write `roles/java/tasks/main.yml` with SPDX header and the
  download task: `ansible.builtin.get_url` fetching `https://get.sdkman.io`
  to `/tmp/sdkman-install.sh`. `get_url` is idempotent by default via
  `force: false` — if the destination file already exists the download is
  skipped; no `creates:` guard is needed or supported by this module.
  No `become_user` — writes to `/tmp` as root (play-level `become: true`
  is inherited); `/tmp` is world-readable so the script is accessible to
  `become_user` in the next task. Per research.md.
- [x] T006 [US1] Add per-user sdkman installer task to
  `roles/java/tasks/main.yml`: `ansible.builtin.shell` running
  `bash /tmp/sdkman-install.sh` with
  `creates: /home/{{ item }}/.sdkman/bin/sdkman-init.sh`,
  `become_user: "{{ item }}"`, and `loop: "{{ desktop_user_names }}"` (FR-010)
- [x] T007 [US1] Add per-user Temurin JDK install task to
  `roles/java/tasks/main.yml`: `ansible.builtin.shell` running
  `bash -c 'source /home/{{ item }}/.sdkman/bin/sdkman-init.sh`
  `&& sdk install java {{ java_sdkman_identifier }}'`
  with
  `creates: /home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}/bin/java`,
  `become_user: "{{ item }}"`, and `loop: "{{ desktop_user_names }}"` (FR-002, FR-005)
- [x] T008 [US1] **Validate SC-001**: Provision a fresh Ubuntu VM (AMD64) with
  only the `java` role active in `configure-linux-roles.yml`; log in as a
  provisioned user; run `java -version 2>&1 | grep -i temurin` and confirm
  exit code 0 and "Temurin" in output. Document the result before proceeding
  to Phase 4.

**Checkpoint**: The role installs sdkman and the Temurin JDK for every user
in `desktop_user_names`. A freshly provisioned user can run `java -version`
and see "Temurin".

---

## Phase 4: User Story 2 — sdkman Is Available for the User (Priority: P2)

**Goal**: Each provisioned user can source `~/.sdkman/bin/sdkman-init.sh`
and run `sdk version` interactively.

**Independent Test**: Log in as a provisioned user; run
`source ~/.sdkman/bin/sdkman-init.sh && sdk version` — expect output
showing the sdkman version without errors.

### Implementation — US2

- [x] T009 [P] [US2] **Verification-only**: Confirm that T006's
  `ansible.builtin.shell` task in `roles/java/tasks/main.yml` targets the
  correct installer path (`bash /tmp/sdkman-install.sh`) and that the
  `creates:` guard correctly points to
  `/home/{{ item }}/.sdkman/bin/sdkman-init.sh` (FR-001, FR-005). Tick this
  off after inspecting the file — no code change expected.
- [x] T010 [P] [US2] **Idempotency verification — sdkman**: Re-run the
  playbook against a host where sdkman is already installed; confirm the
  sdkman installer task shows `ok` (skipped via `creates:`) and not `changed`
  (SC-002). No file change — checklist confirmation only.

**Note — empty `desktop_user_names`**: An empty list is valid. The loop in
T006 and T007 produces zero iterations; Ansible emits no changed or failed
tasks. Validate by inspection of the task structure; no additional test run
is required.

**Checkpoint**: The sdkman installation task is correctly guarded so
a second playbook run does not re-download or re-execute the installer.

---

## Phase 5: User Story 3 — Pinned JDK Version Is Configurable (Priority: P3)

**Goal**: An operator can change the installed Temurin JDK version by
updating only `java_sdkman_identifier` in `defaults/main.yml`.

**Independent Test**: Override `java_sdkman_identifier` in inventory (e.g.
`21.0.6-tem`), run the playbook on a host with the default version already
installed, and verify the new version appears under
`~/.sdkman/candidates/java/21.0.6-tem/bin/java`.

### Implementation — US3

- [x] T011 [P] [US3] **Verification-only**: Confirm that T007's `creates:`
  guard in `roles/java/tasks/main.yml` references the version-specific path
  `/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}/bin/java`
  and NOT the `current/` symlink path (FR-005, spec Key Entities). Tick this
  off after inspecting the file — no code change expected if T007 was written
  correctly.
- [x] T012 [P] [US3] **Verify override**: Temporarily set
  `java_sdkman_identifier: "21.0.6-tem"` in inventory, re-run the playbook
  against a provisioned host, confirm the JDK task shows `changed` and the
  new version is installed under
  `~/.sdkman/candidates/java/21.0.6-tem/bin/java` (SC-004). Revert the
  override afterwards.

**Checkpoint**: Changing `java_sdkman_identifier` causes the new version to
be installed. The old version's `creates:` guard still protects it; only the
new version's task runs.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Playbook integration, documentation completeness, full
idempotency confirmation, and ARM64 validation.

- [x] T013 [P] Add the `java` role entry to `configure-linux-roles.yml`
  before `android_studio` in the Flutter Development group — no `tags:` needed
  (ARM64 is supported); follow the existing role-entry format (FR-007,
  research.md ARM64 decision)
- [x] T014 [P] **Idempotency — full second run (SC-002)**: Run the playbook
  twice against the same provisioned host with the `java` role active; confirm
  the second run shows zero `changed` tasks for the `java` role (FR-006).
  No file change — checklist confirmation only.
- [x] T015 [P] **ARM64 validation (SC-003)**: Provision a fresh ARM64 Ubuntu
  VM with the `java` role applied; confirm `java -version` succeeds and shows
  "Temurin". No role-file change expected — confirms the role needs no
  architecture-specific branching (research.md ARM64 decision).
- [x] T016 Run markdownlint against all modified `.md` files
  (`roles/java/DESIGN.md`, `specs/005-java-role/*.md`) and fix any violations
  per the Markdown Quality Standards constitution principle

---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — T002, T003, T004 can all
  run in parallel once T001 is done
- **Phase 3 (US1)**: Depends on Phase 2 completion — T005 → T006 → T007
  must run in order (each adds the next task to `tasks/main.yml`); T008
  follows after T007
- **Phase 4 (US2)**: Depends on Phase 3 completion — verifies idempotency
  properties of work done in Phase 3
- **Phase 5 (US3)**: Depends on Phase 3 completion — verifies version-guard
  behaviour of T007; can run in parallel with Phase 4 (different concern,
  same file read-only)
- **Phase 6 (Polish)**: Depends on all implementation phases — T013
  (playbook integration) and T014/T015 (validation) require tasks/main.yml
  to be complete

### User Story Dependencies

- **US1 (P1)**: Depends only on Phase 2 completion — no dependency on other
  stories; this is the sole delivery that makes Java available
- **US2 (P2)**: Depends on US1 (sdkman task must exist) — verification phase
  over US1 work
- **US3 (P3)**: Depends on US1 (JDK install task must exist) — verification
  of the version-guard condition in T007

### Within Phase 3 (US1)

- T005 → T006 → T007: sequential — each appends to `roles/java/tasks/main.yml`
- T008: follows T007 — manual acceptance test after tasks are written

### Parallel Opportunities

- T002, T003, T004 — all Phase 2 tasks can run in parallel (distinct files)
- T009, T010 — can run in parallel (both read-only verification)
- T011, T012 — can run in parallel (distinct verification scenarios)
- T013, T014, T015, T016 — can run in parallel (distinct files or read-only
  validation)
- Phase 4 and Phase 5 can proceed in parallel after Phase 3 completes

---

## Parallel Example: Phase 2 (Foundational)

```text
After T001 completes:

  T002  roles/java/defaults/main.yml
  T003  roles/java/meta/main.yml
  T004  roles/java/DESIGN.md

All three tasks write distinct files — launch together.
```

## Parallel Example: Phase 6 (Polish)

```text
After all implementation phases complete:

  T013  configure-linux-roles.yml   (add java role entry)
  T014  second-run idempotency check (read-only validation)
  T015  ARM64 validation             (external VM test)
  T016  markdownlint                 (docs only)

All four are independent — launch together.
```

---

## Implementation Strategy

### MVP (User Story 1 only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002, T003, T004 in parallel)
3. Complete Phase 3: User Story 1 (T005 → T006 → T007 in sequence)
4. **Stop and validate**: Run the playbook against a fresh VM; run
   `java -version 2>&1 | grep -i temurin` (SC-001)
5. If validation passes, continue to Phase 4+

### Incremental Delivery

1. Setup + Foundational → role skeleton ready
2. US1 → sdkman and Temurin JDK installed for all users (MVP)
3. US2 → sdkman idempotency confirmed
4. US3 → version-override behaviour confirmed
5. Polish → playbook integration, ARM64 validation, docs

---

## Notes

- No test tasks are generated — the spec does not request TDD or automated
  tests; SC-005 is satisfied by a manual Vagrant run per `CONTRIBUTING.md`.
- All per-user tasks use `loop: "{{ desktop_user_names }}"` and
  `become_user: "{{ item }}"`. The download task (T005) does NOT use
  `become_user` because it writes to `/tmp` as root (play-level
  `become: true` is inherited); `/tmp` is world-readable so the script
  is accessible to `become_user` in the next task
  (research.md `become_user` pattern decision).
- The `java` role requires NO `tags:` in `configure-linux-roles.yml`; it
  supports both AMD64 and ARM64 natively (research.md ARM64 decision).
- All YAML files MUST begin with `#SPDX-License-Identifier: MIT-0` (FR-008).
- All Ansible module references MUST use FQCN (`ansible.builtin.*`) (FR-009).
- The sdkman installer appends the `source ~/.sdkman/bin/sdkman-init.sh`
  snippet to `.bashrc` and `.profile` automatically — no `blockinfile` task
  is needed (research.md PATH decision).
- Upgrade procedure: bump `java_sdkman_identifier` in
  `roles/java/defaults/main.yml`; re-run the playbook. The `creates:` guard
  for the old path is still satisfied; only the new version's task runs.
