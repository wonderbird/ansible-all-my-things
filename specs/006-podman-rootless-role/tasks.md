# Tasks: Rootless Podman Ansible Role

**Input**: Design documents from `/specs/006-podman-rootless-role/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths are included in all descriptions

---

## Phase 1: Setup (Role Skeleton)

**Purpose**: Create the `roles/podman/` directory structure that all subsequent
tasks depend on. No implementation logic yet.

- [X] T001 Create role directory skeleton: `roles/podman/defaults/`,
  `roles/podman/meta/`, `roles/podman/tasks/`
- [X] T002 [P] Create stub `roles/podman/defaults/main.yml` with SPDX header only
- [X] T003 [P] Create stub `roles/podman/meta/main.yml` with SPDX header only
- [X] T004 [P] Create stub `roles/podman/tasks/main.yml` with SPDX header only

**Checkpoint**: All role directories and stub files exist; playbook can reference
the role without errors.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Populate role metadata and defaults — required before any task
logic can reference role variables.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Implement `roles/podman/defaults/main.yml` — declare
  `podman_subuid_start: 100000`, `podman_subuid_count: 65536`,
  `podman_subgid_start: 100000`, `podman_subgid_count: 65536`
- [X] T006 [P] Implement `roles/podman/meta/main.yml` — set `galaxy_info`
  with author, description (`Install and configure rootless Podman on Ubuntu`),
  license (`MIT-0`), and platforms (`Ubuntu 22.04+`)

**Checkpoint**: Role variables are declared with sensible defaults; meta is
complete. User story implementation can now begin.

---

## Phase 3: User Story 1 — Install and Run Podman (P1 — MVP)

**Goal**: Every desktop user listed in `desktop_user_names` can invoke `podman`
from their own login shell after one playbook run.

**Independent Test**: Run the playbook against a fresh Ubuntu VM, then log in
as one of the target users and run `podman --version`. A version string proves
the tool is present and accessible. Follow
`specs/006-podman-rootless-role/quickstart.md` steps 1–2.

### Implementation for User Story 1

- [X] T007 [US1] Add Podman install task to `roles/podman/tasks/main.yml` —
  `ansible.builtin.apt: name=podman state=present` with `become: true`
  inherited from play level
- [X] T008 [US1] Verify `roles/podman/tasks/main.yml` uses fully-qualified
  `ansible.builtin.apt` module name per FR-005
  *(human review checkpoint — no file changes produced)*

**Checkpoint**: After running the playbook, `podman --version` succeeds for
every user in `desktop_user_names`.

---

## Phase 4: User Story 2 — Rootless Configuration Per User (Priority: P2)

**Goal**: Every listed desktop user has valid `/etc/subuid` and `/etc/subgid`
range entries, enabling rootless container operation.

**Independent Test**: After the role runs, inspect `/etc/subuid` and
`/etc/subgid` — each user in `desktop_user_names` must have a valid
`username:100000:65536` entry. Run `podman run --rm hello-world` as one of
those users to confirm rootless operation works end-to-end.

### Implementation for User Story 2

- [X] T009 [US2] Add subuid loop task to `roles/podman/tasks/main.yml` —
  `ansible.builtin.lineinfile` on `/etc/subuid` with
  `regexp: '^{{ item }}:'`,
  `line: '{{ item }}:{{ podman_subuid_start }}:{{ podman_subuid_count }}'`,
  looping over `desktop_user_names`
- [X] T010 [P] [US2] Add subgid loop task to `roles/podman/tasks/main.yml` —
  `ansible.builtin.lineinfile` on `/etc/subgid` with
  `regexp: '^{{ item }}:'`,
  `line: '{{ item }}:{{ podman_subgid_start }}:{{ podman_subgid_count }}'`,
  looping over `desktop_user_names`
- [X] T011 [US2] Add `podman system migrate` task to
  `roles/podman/tasks/main.yml` —
  `ansible.builtin.command: podman system migrate` with
  `become_user: "{{ item }}"`, `loop: "{{ desktop_user_names }}"`,
  and `changed_when: false`

**Checkpoint**: After running the playbook, `/etc/subuid` and `/etc/subgid`
contain valid entries for every listed user, and `podman run --rm hello-world`
succeeds rootlessly.

---

## Phase 5: User Story 3 — Idempotent Re-Runs (Priority: P3)

**Goal**: A second consecutive playbook run on a fully-configured host reports
zero changed tasks.

**Independent Test**: Run the playbook twice in sequence. The second run must
report zero changed tasks (all tasks report `ok` or `skipped`). Follow
`specs/006-podman-rootless-role/quickstart.md` step 3.

### Implementation for User Story 3

- [X] T012 [US3] Verify `ansible.builtin.apt` task in
  `roles/podman/tasks/main.yml` uses `state: present` (not `state: latest`)
  to avoid spurious changes
- [X] T013 [US3] Verify `ansible.builtin.lineinfile` tasks in
  `roles/podman/tasks/main.yml` have start-anchored `regexp: '^{{ item }}:'`
  to prevent duplicates
  *(human review checkpoint — no file changes produced)*
- [X] T014 [US3] Verify `podman system migrate` task in
  `roles/podman/tasks/main.yml` has `changed_when: false` per FR-006
  *(human review checkpoint — no file changes produced)*

**Checkpoint**: All three verification tasks confirm the idempotency mechanisms
are in place. A second playbook run reports zero changed tasks.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Documentation and integration — affects all user stories.

- [X] T015 [P] Create `roles/podman/README.md` — document role purpose,
  variables table (`podman_subuid_start`, `podman_subuid_count`,
  `podman_subgid_start`, `podman_subgid_count`), example playbook snippet,
  and MIT-0 licence notice
- [X] T016 [P] Create `roles/podman/DESIGN.md` — document non-obvious design
  decisions: lineinfile idempotency strategy (Decision 2),
  `podman system migrate` `changed_when: false` guard (Decision 3),
  play-level `become` convention (Decision 5)
- [X] T017 Add `podman` to the `roles:` list in `configure-linux-roles.yml`
  following `specs/006-podman-rootless-role/quickstart.md` "Adding the Role"
  section. After inserting the role, run the playbook with only `podman`
  active against a local VM and confirm it completes without errors.
- [X] T018 [P] Apply the `format-markdown` skill to all new Markdown files in
  `roles/podman/` (README.md and DESIGN.md) to verify Markdown quality
  (Principle VI)
- [ ] T020 Run full acceptance test checklist from
  `specs/006-podman-rootless-role/quickstart.md` against the local VM
- [X] T021 Verify that `roles/podman/tasks/main.yml` contains no reference to
  `podman-docker` — covers FR-011
  *(human review checkpoint — no file changes produced)*

---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2
- **Phase 4 (US2)**: Depends on Phase 3 — subuid/subgid tasks reference Podman
  which must already be installed
- **Phase 5 (US3)**: Depends on Phases 3 and 4 — idempotency verification
  requires all task implementations to be complete
- **Phase 6 (Polish)**: Depends on Phases 3, 4, and 5

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2. No dependency on US2 or US3.
- **User Story 2 (P2)**: Starts after US1 is complete (Podman must be installed
  before `podman system migrate` can run).
- **User Story 3 (P3)**: Starts after US1 and US2 are complete (all task
  implementations must exist before idempotency can be verified).

### Within Each User Story

- T009 (subuid) and T010 (subgid) are independently parallelisable — different
  files, no mutual dependency.
- T011 (migrate) depends on T009 and T010.

### Parallel Opportunities

- T002, T003, T004 (Phase 1 stubs) can run in parallel.
- T005 and T006 (Phase 2) can run in parallel.
- T009 and T010 (Phase 4 lineinfile tasks) can run in parallel.
- T015, T016, T018 (Phase 6 documentation) can run in parallel.

---

## Parallel Example: Phase 4

```text
# Run these two tasks in parallel (different target files):
T009 [US2] lineinfile on /etc/subuid
T010 [P] [US2] lineinfile on /etc/subgid

# Then run sequentially:
T011 [US2] podman system migrate (depends on T009 + T010)
```

---

## Implementation Strategy

### MVP Scope (User Story 1 Only)

1. Complete Phase 1: Setup (role skeleton)
2. Complete Phase 2: Foundational (defaults + meta)
3. Complete Phase 3: User Story 1 (install Podman)
4. **STOP and VALIDATE**: `podman --version` succeeds for every listed user
5. Proceed to Phase 4 once US1 is confirmed

### Incremental Delivery

1. Phase 1 + Phase 2 → role skeleton with defaults and meta
2. Phase 3 (US1) → Podman installed; `podman --version` works
3. Phase 4 (US2) → rootless configuration; `podman run --rm hello-world` works
4. Phase 5 (US3) → idempotency verified; second run is clean
5. Phase 6 (Polish) → documentation complete; role integrated into playbook

---

## Notes

- All YAML files in `roles/podman/` MUST carry `# SPDX-License-Identifier: MIT-0`
  as their first line (FR-009).
- All module references MUST use fully-qualified `ansible.builtin.*` names
  (FR-005).
- No `handlers/`, `templates/`, or `files/` directories are needed per plan.md.
- `desktop_user_names` has no role-level default; the calling playbook must
  supply it. An empty list is valid — per-user loop tasks are skipped.
- The `podman system migrate` task runs with `become_user: "{{ item }}"` and
  inherits `become: true` from the play level (Decision 5 in research.md).
