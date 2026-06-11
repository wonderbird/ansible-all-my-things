---

description: "Task list for Configure Basic Profile for Tart VMs"
---

# Tasks: Configure Basic Profile for Tart VMs

**Input**: Design documents from `/specs/010-configure-basic-profile/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/configure-basic-profile.md, quickstart.md

**Tests**: No automated test tasks are generated. Per `research.md`'s "End-to-end
validation strategy" decision, the five composed roles already have passing
`molecule/default/` scenarios (no new Molecule work in scope), and this
feature's two new playbooks contain zero implementation logic — there is
nothing role-shaped to unit-test. End-to-end validation is the manual
quickstart procedure (Phase 5).

**Organization**: This feature is a pure composition of existing,
already-tested building blocks (3 new files, ~25 lines total, 0 new roles).
Both user stories from `spec.md` are validated against the same 3 artifacts:
User Story 1 (P1) creates them; User Story 2 (P2) re-runs the same playbook to
confirm idempotency. There is no separate Setup or Foundational phase — the
three file-creation tasks below ARE the foundational and only implementation
work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

Repo-root playbook layout, mirroring `configure-linux.yml` /
`configure-linux-roles.yml`. All paths below are relative to the repository
root.

---

## Phase 1: User Story 1 - Bring a fresh tart VM to a baseline (Priority: P1) 🎯 MVP

**Goal**: A single playbook, `configure-profile.yml`, run with no
extra-vars against the `tart` inventory group, brings a freshly-created tart
VM (from `create-vm.yml`) to a development-ready baseline: configured users
with SSH/sudo access, OS packages and timezone baseline, Node.js toolchain for
desktop users, the five standard development tool roles (podman, ruby, python,
dolt_sql_server, claude_code), and a conditional reboot.

**Independent Test**: Run `create-vm.yml` to create a new tart VM, then run
`ansible-playbook playbooks/configure-profile.yml` against the `tart` group with
no extra-vars. Verify the operator can SSH in as `my_ansible_user` and as each
configured desktop user using their SSH key (no password), and that podman,
ruby, python, the Dolt SQL server, and the Claude Code CLI are all available.

### Implementation for User Story 1

- [x] T001 [US1] Create `inventories/group_vars/tart/vars.yml` defining
  `admin_user_on_fresh_system: "admin"`, mirroring
  `inventories/group_vars/vagrant_tart/vars.yml` exactly (same key/value, with
  a `# Tart (Linux) specific overrides` comment per `research.md`'s
  "tart group_vars for the bootstrap account" decision). This file is consumed
  by `playbooks/setup-users.yml` as the initial `ansible_user` for hosts in
  the `tart` group (FR-002, data-model.md "Default Bootstrap Account").

- [x] T002 [US1] Create `playbooks/configure-profile-roles.yml`:
  a single play with `name: Configure basic profile linux roles`,
  `hosts: tart`, `become: true`, `vars: { ansible_user: "{{ my_ansible_user }}",
  desktop_user_names: "{{ desktop_users | map(attribute='name') | list }}" }`,
  and `roles: [podman, ruby, python, dolt_sql_server, claude_code]` — mirroring
  `configure-linux-roles.yml`'s structure but scoped to `hosts: tart` and
  omitting `tmux` and `google_chrome` per FR-018 (research.md "Roles-application
  playbook scoped to tart group"; data-model.md "Development Tool Role").
  Depends on: T001 (admin_user_on_fresh_system must resolve for the `tart`
  group before any play in the chain runs).

- [x] T003 [US1] Create `playbooks/configure-profile.yml`: a flat
  `import_playbook` chain, in order —
  `playbooks/setup-users.yml`, `playbooks/setup-basics.yml`,
  `playbooks/setup-nodejs.yml`, `configure-profile-roles.yml`,
  `playbooks/reboot-if-required.yml` — mirroring `configure-linux.yml`'s
  pattern minus the desktop-only steps excluded by FR-018
  (research.md "Orchestrator playbook structure"). Depends on: T002 (the
  orchestrator imports `configure-profile-roles.yml`).

**Checkpoint**: User Story 1 is fully implemented. `configure-profile.yml`
can be run end-to-end against a freshly-created tart VM (validated manually in
Phase 3, since this is a macOS ARM64 host requirement per AGENTS.md).

---

## Phase 2: User Story 2 - Re-running the playbook is a no-op (Priority: P2)

**Goal**: A second run of `configure-profile.yml` against an
already-configured tart VM, with no extra-vars, reports zero changed tasks
(FR-020, SC-006).

**Independent Test**: After completing User Story 1's independent test, run
`ansible-playbook playbooks/configure-profile.yml` again against the same VM with
no extra-vars and verify the run reports `changed=0` across all plays.

### Implementation for User Story 2

This story requires no new or modified files beyond those created in User
Story 1 (T001–T003). It is a verification-only activity confirming the
already-idempotent composed playbooks/roles (per `contracts/
configure-basic-profile.md`'s "Idempotency" section) behave idempotently when
chained together by this feature's new orchestrator. The verification itself
is performed in Phase 3 (T004, second invocation).

**Checkpoint**: Both user stories are validated together in Phase 3 — User
Story 1 by the first playbook run, User Story 2 by the second.

---

## Phase 3: End-to-End Validation & Polish

**Purpose**: Manual validation against a real tart VM (Constitution
Principle III; this feature has no Molecule scenario per research.md), plus
repository documentation/quality gates.

**⚠️ Requires a macOS ARM64 host with `tart` and `sshpass` installed** (per
`quickstart.md` Prerequisites and AGENTS.md "Test environment host
architecture" — check `uname -m` if running on an unfamiliar host).

- [x] T004 [US1] [US2] Run the quickstart end-to-end validation from
  `specs/010-configure-basic-profile/quickstart.md` on a macOS ARM64 host:
  (1) `ansible-playbook playbooks/create-vm.yml` to create a fresh tart VM;
  (2) run `ansible-playbook playbooks/configure-profile.yml` with no extra-vars
  (User Story 1) — verify it completes successfully, `my_ansible_user` and all
  `desktop_users` can SSH in via key with sudo, password SSH auth is rejected,
  apt cache/timezone (`Europe/Berlin`) are correct, NVM/Node LTS/global npm
  tools (`eslint`, `markdownlint-cli`, `prettier`, `typescript`) are present
  for each desktop user, and `podman`, `ruby`, `python3`, `claude` are all
  installed; (3) run `ansible-playbook playbooks/configure-profile.yml` again with
  no extra-vars (User Story 2) — verify the run reports `changed=0` across all
  plays (FR-020/SC-006). Depends on: T001, T002, T003.

- [x] T005 [P] Invoke the `review-documentation-here` skill to confirm no
  documentation updates (e.g. `README.md`, `docs/architecture/`) are required
  for the new `configure-profile.yml` /
  `configure-profile-roles.yml` playbooks and
  `inventories/group_vars/tart/vars.yml`, per Constitution "Documentation
  Standards" (invoked at task close, before `format-markdown`).

- [x] T006 Invoke the `format-markdown` skill once, after T005, to lint-check
  any Markdown files touched while completing this feature (Constitution
  Principle VI). Depends on: T005.

**Checkpoint**: Feature complete — both user stories validated end-to-end on a
real tart VM, idempotency confirmed (FR-020/SC-006), documentation and
Markdown quality gates passed.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (US1)**: No dependencies — can start immediately. T001 → T002 → T003
  (strict order: group_vars before roles playbook before orchestrator, since
  each later file references the variables/playbooks defined earlier).
- **Phase 2 (US2)**: Depends on Phase 1 (T001–T003) producing the artifacts to
  re-run. Contains no implementation tasks of its own.
- **Phase 3 (Validation & Polish)**: Depends on Phase 1 completion (T001–T003).
  T004 validates both US1 and US2 in a single two-run procedure. T005 and T006
  run after T004 (documentation/formatting reflect the final state of the
  feature).

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories. Fully self-contained
  (T001–T003).
- **User Story 2 (P2)**: Depends on User Story 1's artifacts existing
  (T001–T003) — it re-runs the same playbook a second time. No new files.

### Within Phase 1

- T001 before T002 before T003 (each file is consumed by the next in the
  chain: `vars.yml` → `configure-profile-roles.yml` →
  `configure-profile.yml`). No `[P]` markers — all three touch the
  dependency chain in sequence and are small enough that sequential execution
  is simplest (Principle IV).

### Parallel Opportunities

- T001, T002, T003 are NOT parallelizable — strict file-dependency order (see
  above).
- T005 is marked `[P]` relative to T006 only in the sense that it is a
  read-only review step; T006 still depends on T005 completing first per the
  skill-invocation order mandated by the constitution ("Skill index": review
  documentation before format-markdown).
- No parallel execution opportunities exist across user stories — US2 reuses
  US1's artifacts entirely.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 → T002 → T003 (the entire implementation: 3 files,
   ~25 lines total).
2. **STOP and VALIDATE**: Run T004's first invocation
   (`create-vm.yml` + `configure-profile.yml`) on a macOS ARM64 host to
   confirm User Story 1's acceptance scenarios.
3. This already delivers the full feature — User Story 2 requires no
   additional code.

### Incremental Delivery

1. T001–T003 → User Story 1 implemented (MVP).
2. T004 (first run) → User Story 1 validated end-to-end.
3. T004 (second run) → User Story 2 validated (idempotency, FR-020/SC-006).
4. T005–T006 → documentation and Markdown quality gates.
5. Commit (per the `commit` skill, Constitution Principle V) and request user
   review (Constitution "Development Workflow" step 5).

---

## Notes

- `[P]` tasks = different files, no dependencies. This feature has very few
  `[P]` opportunities because its three files form a strict reference chain
  and the manual validation/documentation steps are inherently sequential.
- `[Story]` label maps task to specific user story for traceability.
- T004 (manual end-to-end validation) requires a macOS ARM64 host with `tart`
  and `sshpass` (quickstart.md Prerequisites); verify host architecture with
  `uname -m` before attempting it (AGENTS.md "Test environment host
  architecture").
- No automated tests are added — see "Tests" note above.
- Commit after T003 (implementation complete) and again after T004–T006
  (validation + polish), per Constitution Principle V (small, coherent
  commits) and the `commit` skill.
