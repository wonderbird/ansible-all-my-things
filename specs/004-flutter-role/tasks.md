---

description: "Task list for Flutter Ansible Role implementation"
---

# Tasks: Flutter Ansible Role

**Input**: Design documents from `/specs/004-flutter-role/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story. No test tasks are generated
(not requested in the feature specification).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4)

---

## Phase 1: Setup (Role Skeleton)

**Purpose**: Create the `roles/flutter/` directory structure before any
content tasks begin.

- [ ] T001 Create role directory tree `roles/flutter/` with subdirectories `defaults/`, `meta/`, `tasks/`

---

## Phase 2: Foundational (Role Variables and Metadata)

**Purpose**: Files that every subsequent task depends on — defaults and
meta must exist before tasks/main.yml can reference variables, and
README/DESIGN must exist before they can be edited.

**Note**: No user-story work can begin until this phase is complete.

- [ ] T002 [P] Write `roles/flutter/defaults/main.yml` with `flutter_version: "3.41.6"` and `flutter_sha256` per data-model.md
- [ ] T003 [P] Write `roles/flutter/meta/main.yml` with `dependencies: []` following the `android_studio` meta template
- [ ] T004 [P] Create stub `roles/flutter/README.md` documenting role purpose, variables (`flutter_version`, `flutter_sha256`, `desktop_user_names`), and both `android_studio` and `google_chrome` as prerequisite dependencies (FR-010, FR-014)
- [ ] T005 [P] Create stub `roles/flutter/DESIGN.md` documenting the version-file idempotency approach, tag placement, and other non-obvious decisions from research.md

**Checkpoint**: Defaults, metadata, and documentation stubs are in place.

---

## Phase 3: User Story 1 — Build a Flutter Web App After Provisioning (Priority: P1) — MVP

**Goal**: Provision an AMD64 machine so a developer can clone a Flutter
project and run `flutter build web` without any manual steps.

**Independent Test**: Provision a fresh AMD64 VM with the `flutter` role
applied, clone a known Flutter sample project, run `flutter build web`,
and confirm it completes without errors. Run `flutter doctor` and confirm
the Chrome/web target reports no errors.

### Implementation

- [ ] T006 [US1] Write `roles/flutter/tasks/main.yml` — apt task: install `clang`, `cmake`, `ninja-build`, `pkg-config`, `libgtk-3-dev`, `mesa-utils` using `ansible.builtin.apt`
- [ ] T007 [US1] Add `ansible.builtin.systemd` task with `daemon_reload: true` after the apt task in `roles/flutter/tasks/main.yml` (FR-018)
- [ ] T008 [US1] Add per-user `ansible.builtin.stat` task to check `/home/{{ item }}/flutter/version` in `roles/flutter/tasks/main.yml` (loop over `desktop_user_names`)
- [ ] T009 [US1] Add per-user `ansible.builtin.slurp` task to read the version file when it exists, and `ansible.builtin.set_fact` to derive `flutter_installed_version` in `roles/flutter/tasks/main.yml`
- [ ] T010 [US1] Add per-user `ansible.builtin.get_url` task to download `flutter_linux_{{ flutter_version }}-stable.tar.xz` to `/tmp` with `checksum: "sha256:{{ flutter_sha256 }}"`, conditioned on version mismatch, in `roles/flutter/tasks/main.yml`
- [ ] T011 [US1] Add per-user `ansible.builtin.file` task to remove `/home/{{ item }}/flutter` (state=absent) when version mismatch in `roles/flutter/tasks/main.yml`
- [ ] T012 [US1] Add per-user `ansible.builtin.unarchive` task to extract the archive to `/home/{{ item }}/` with `become_user: "{{ item }}"` when version mismatch in `roles/flutter/tasks/main.yml`
- [ ] T013 [US1] Add per-user `ansible.builtin.blockinfile` task to insert `export PATH="$HOME/flutter/bin:$PATH"` into `~/.bashrc` with marker `# {mark} ANSIBLE MANAGED BLOCK - Flutter PATH` in `roles/flutter/tasks/main.yml`
- [ ] T013a [US1] **Validate SC-001/SC-002**: Provision a fresh AMD64 VM with the role applied; run `flutter doctor` and confirm Chrome/web target reports no errors (SC-001); clone a Flutter sample project and run `flutter build web` to confirm it succeeds without manual steps (SC-002). Document the result before proceeding to Phase 4.

**Checkpoint**: The role installs Flutter and configures PATH. A fresh AMD64
VM provisioned with this role should pass `flutter doctor` for the Chrome/web
target and support `flutter build web`.

---

## Phase 4: User Story 2 — Idempotent Re-runs (Priority: P2)

**Goal**: Running the playbook a second time against the same machine
produces no `changed` tasks for the `flutter` role.

**Independent Test**: Run the playbook twice against the same AMD64 VM.
Confirm the second run shows `ok` or `skipped` for every `flutter` role
task — never `changed`.

### Implementation

- [ ] T014 [P] [US2] Verify idempotency of the `ansible.builtin.apt` task in `roles/flutter/tasks/main.yml` — confirm `state: present` is used (idempotent by module semantics)
- [ ] T015 [P] [US2] Verify idempotency of the `ansible.builtin.blockinfile` task in `roles/flutter/tasks/main.yml` — confirm the marker string is unique and consistent so re-runs do not re-insert the block
- [ ] T016 [P] [US2] Verify the version-guard `when:` conditions on the `get_url`, `file` (state=absent), and `unarchive` tasks in `roles/flutter/tasks/main.yml` so that matching versions cause those tasks to be skipped

**Checkpoint**: A second playbook run against a provisioned AMD64 VM
shows zero `changed` tasks for the `flutter` role.

---

## Phase 5: User Story 3 — Graceful Skip on ARM64 Machines (Priority: P2)

**Goal**: The `flutter` role is entirely skipped on ARM64 hosts without
errors, consistent with the `android_studio` role.

**Independent Test**: Run the playbook against an ARM64 Vagrant VM. Confirm
all `flutter` role tasks are skipped and the playbook completes
successfully.

### Implementation

- [ ] T017 [US3] Add the `flutter` role entry to `configure-linux-roles.yml` after the `android_studio` entry, with `tags: not-supported-on-vagrant-arm64`, following the existing pattern

**Checkpoint**: Running the playbook against an ARM64 VM skips all
`flutter` role tasks. The `not-supported-on-vagrant-arm64` tag applied at
the role entry level in `configure-linux-roles.yml` is the sole mechanism.

---

## Phase 6: User Story 4 — Role Integrates Without Extra Friction (Priority: P3)

**Goal**: A developer adds the `flutter` role to the provisioning run by
editing only `configure-linux-roles.yml`.

**Independent Test**: On a fresh checkout, add the `flutter` entry to
`configure-linux-roles.yml` only, run the playbook against a fresh VM,
and confirm Flutter is installed without editing any other file.

### Implementation

- [ ] T018 [US4] **Verification-only (no file change)**: Confirm that T017's addition to `configure-linux-roles.yml` is the only file change required to integrate the role — no edits to `configure-linux.yml` or any other playbook (FR-003). This task produces no artifact; it is a checklist step to be ticked off after T017.

**Checkpoint**: The role is fully integrated by the single `configure-linux-roles.yml`
entry added in T017.

---

## Phase 7: Polish and Cross-Cutting Concerns

**Purpose**: Documentation completeness, markdownlint compliance, and
spec traceability.

- [ ] T019 [P] Complete `roles/flutter/README.md` — add Variables table, Dependencies section listing both `android_studio` and `google_chrome` as prerequisites (FR-010, FR-014), and Usage notes per plan.md structure
- [ ] T020 [P] Complete `roles/flutter/DESIGN.md` — document version-file idempotency, tag-at-role-entry rationale, `meta/main.yml` dependency decision (Q5), and PATH via blockinfile decision (Q1)
- [ ] T021 Run markdownlint against all modified `.md` files (`roles/flutter/README.md`, `roles/flutter/DESIGN.md`, `specs/004-flutter-role/*.md`) and fix any violations per the Markdown Quality Standards constitution principle
- [ ] T022 Delete the stale `specs/005-flutter-role/` directory (artefact of the auto-incremented setup script run; documented in research.md). This MUST be done before the PR is merged.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — T002–T005 can all run
  in parallel once T001 is done
- **Phase 3 (US1)**: Depends on Phase 2 completion — T006 through T013
  must run in order within the phase (each task adds to tasks/main.yml)
- **Phase 4 (US2)**: Depends on Phase 3 completion — verifies idempotency
  properties of tasks written in Phase 3
- **Phase 5 (US3)**: Depends on Phase 3 completion — can start in parallel
  with Phase 4 (different file: configure-linux-roles.yml)
- **Phase 6 (US4)**: Depends on Phase 5 completion (T017 must exist first)
- **Phase 7 (Polish)**: Depends on all implementation phases being complete; T022 (cleanup) MUST run before the PR is merged but has no code dependency

### User Story Dependencies

- **US1 (P1)**: Depends only on Foundational phase — no dependency on other stories
- **US2 (P2)**: Depends on US1 tasks existing — is a verification phase over US1 work
- **US3 (P2)**: Depends on US1 (tasks/main.yml must exist) — independent of US2
- **US4 (P3)**: Depends on US3 (T017 must exist) — single-task confirmation

### Within Each Phase

- Tasks that append to `roles/flutter/tasks/main.yml` (T006–T013) are
  sequential — each adds the next task in the documented sequence
- Documentation tasks (T019, T020, T021) are independent of each other
  and of the implementation phases (different files)

### Parallel Opportunities

- T002, T003, T004, T005 — all Phase 2 tasks can run in parallel (distinct files)
- T014, T015, T016 — all Phase 4 tasks can run in parallel (read-only verification of the same file; no write conflicts)
- T019, T020 — can run in parallel (distinct files)
- Phase 4 (US2) and Phase 5 (US3) can proceed in parallel after Phase 3 completes

---

## Parallel Example: Phase 2 (Foundational)

```text
After T001 completes:

  T002  roles/flutter/defaults/main.yml
  T003  roles/flutter/meta/main.yml
  T004  roles/flutter/README.md (stub)
  T005  roles/flutter/DESIGN.md (stub)

All four tasks write distinct files — launch together.
```

## Parallel Example: Phase 4 and Phase 5 (after Phase 3)

```text
After Phase 3 completes:

  T014 + T015 + T016  (Phase 4: idempotency verification — same file, read-only)
  T017               (Phase 5: configure-linux-roles.yml — different file)

Phase 4 and Phase 5 touch different files — both can start immediately.
```

---

## Implementation Strategy

### MVP (User Story 1 only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (parallel — 4 tasks)
3. Complete Phase 3: User Story 1 (T006–T013 in sequence)
4. **Stop and validate**: Provision a fresh AMD64 VM; run `flutter doctor`
   and `flutter build web`
5. If validation passes, continue to Phase 4+

### Incremental Delivery

1. Setup + Foundational → role skeleton ready
2. US1 → Flutter installed, PATH configured, web target works
3. US2 → Idempotency confirmed (second-run validation)
4. US3 + US4 → ARM64 skip and clean integration confirmed
5. Polish → Documentation complete, markdownlint passing

### Single-Developer Sequence

```text
T001 → T002/T003/T004/T005 (parallel) →
T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T013a →
T014/T015/T016 (parallel) + T017 (parallel) →
T018 → T019/T020 (parallel) → T021 → T022
```

---

## Notes

- No test tasks are generated — the spec does not request TDD or automated
  tests.
- The `not-supported-on-vagrant-arm64` tag is applied **only** at the role
  entry level in `configure-linux-roles.yml`; individual tasks inside the
  role carry no tags (FR-007).
- All per-user tasks use `loop: "{{ desktop_user_names }}"` and
  `become_user: "{{ item }}"` where file ownership matters.
- Upgrade procedure: bump `flutter_version` and `flutter_sha256` in
  `roles/flutter/defaults/main.yml`; re-run the playbook.
- T022 covers deletion of the stale `specs/005-flutter-role/` directory
  before merging; it is now a tracked task rather than an informal note.
- FR-008 (comment about `apply: tags:` for `include_role`) is already
  satisfied: the required comment exists in `configure-linux-roles.yml`
  at the `android_studio` role entry. No implementation task is needed
  for FR-008.
