# Tasks: Desktop Profile for Create and Destroy VM Playbooks

**Input**: Design documents from `/specs/014-desktop-profile/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in spec.md. Validation is via the spec's
"Independent Test" sections (real VM/cloud runs per Constitution Principle
III) — no Molecule scenario applies (these are orchestration playbooks /
task files, not roles).

**Organization**: Tasks are grouped by user story (US1/US2/US3 from
spec.md) to enable independent implementation and testing of each.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3)
- File paths are repository-relative

## Phase 1: Setup

Not applicable — this feature modifies existing playbooks/task files in an
already-initialized project. No new project scaffolding, dependencies, or
tooling configuration is introduced.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Introduce the `profile` mechanism itself (extra-var,
group-key plumbing, `basic` group scoping) — none of this exists today
(research.md). MUST complete before any user story, since US1/US2/US3 all
build on it.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T001 Add `profile` extra-var (values `basic` default, `desktop`) to
      `playbooks/create-vm.yml`, passed through to
      `tasks/create/{{ provider }}.yml`
- [ ] T002 [P] Add `basic`/`desktop` inventory-group-key registration
      (selected by `profile`) to `playbooks/tasks/create/tart.yml`'s
      `updated_inventory` build, alongside the existing `all`/`linux`/`tart`
      keys (depends on T001)
- [ ] T003 [P] Same group-key registration in
      `playbooks/tasks/create/docker.yml` (depends on T001)
- [ ] T004 [P] Same group-key registration in
      `playbooks/tasks/create/hcloud.yml` (depends on T001)
- [ ] T005 [P] Same group-key registration in
      `playbooks/tasks/create/aws.yml` (depends on T001)
- [ ] T006 [P] Add `basic`/`desktop` group-key removal to
      `playbooks/tasks/destroy/tart.yml`'s `cleaned_inventory` build,
      alongside the existing `all`/`linux`/`tart` keys
- [ ] T007 [P] Same group-key removal in
      `playbooks/tasks/destroy/docker.yml`
- [ ] T008 [P] Same group-key removal in
      `playbooks/tasks/destroy/hcloud.yml`
- [ ] T009 [P] Same group-key removal in `playbooks/tasks/destroy/aws.yml`
- [ ] T010 Add `profile` value validation (`basic`|`desktop`) to
      `playbooks/tasks/assert-provider.yml`, run in `create-vm.yml`'s
      `pre_tasks` before `tasks/create/{{ provider }}.yml` is included
      (depends on T001)
- [ ] T011 [P] Re-scope `playbooks/configure-profile-roles.yml`'s existing
      play from `hosts: linux` to `hosts: basic` (behavior-preserving —
      confirm every current target is already a `linux`-group member before
      this lands)

**Checkpoint**: `profile` extra-var works end-to-end for `profile=basic`
(the default), with hosts landing in the new `basic` inventory group
exactly as they did under `linux` before. User story implementation can now
begin.

---

## Phase 3: User Story 1 - Create a desktop-profile VM (Priority: P1) 🎯 MVP

**Goal**: An engineer provisions a working desktop VM (any provider except
`docker`) through `create-vm.yml -e profile=desktop` +
`configure-profile.yml`, landing in the `desktop` inventory group with the
full legacy desktop role/playbook set applied.

**Independent Test**: Run
`create-vm.yml -e provider=tart -e profile=desktop`, then
`configure-profile.yml --limit <name>`. Verify the host is in the `desktop`
group (not `basic`) and ends up with the desktop environment, keyring, and
desktop apps installed.

### Implementation for User Story 1

- [ ] T012 [US1] Add a `hosts: desktop` play to
      `playbooks/configure-profile-roles.yml` that imports the legacy
      `configure-linux-roles.yml` role list verbatim (depends on T011)
- [ ] T013 [US1] Add a `desktop` branch to `playbooks/configure-profile.yml`
      that imports `playbooks/setup-desktop.yml`,
      `playbooks/setup-keyring.yml`, `playbooks/setup-desktop-apps.yml`
      verbatim
- [ ] T014 [US1] Validate end-to-end on a real tart VM (Constitution
      Principle III): `create-vm.yml -e provider=tart -e profile=desktop`,
      then `configure-profile.yml --limit <name>`; confirm desktop
      environment (XFCE/XRDP), GNOME keyring, desktop apps, and the full
      legacy role list are installed (depends on T001-T012, T013)

**Checkpoint**: User Story 1 is fully functional and independently
testable — desktop VMs are reachable through the unified commands for the
first time.

---

## Phase 4: User Story 2 - Block an unsupported provider/profile combination loudly (Priority: P2)

**Goal**: `create-vm.yml -e provider=docker -e profile=desktop` fails
immediately, before any container is created.

**Independent Test**: Run
`create-vm.yml -e provider=docker -e profile=desktop`. Verify immediate
failure naming both values, with no container created.

### Implementation for User Story 2

- [ ] T015 [US2] Add a `provider == 'docker' and profile == 'desktop'`
      rejection assertion to `playbooks/tasks/assert-provider.yml`, run in
      `create-vm.yml`'s `pre_tasks` (depends on T010)
- [ ] T016 [US2] Validate: `create-vm.yml -e provider=docker -e
      profile=desktop` fails immediately with an explicit error naming both
      values, before any container is created; `create-vm.yml -e
      provider=tart -e profile=desktop` (and `hcloud`, `aws`) still succeed
      (depends on T015)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Desktop VMs on AWS get RDP access without exposing it on basic VMs (Priority: P3)

**Goal**: AWS desktop-profile VMs get inbound TCP 3389; AWS basic-profile
VMs never do, even though both share the `ansible-sg` security group.

**Independent Test**: Create one `basic`-profile and one `desktop`-profile
VM on AWS. Verify the desktop VM's security group allows 3389; verify the
basic VM's does not.

### Implementation for User Story 3

- [ ] T017 [US3] Condition the TCP 3389 rule in the
      `amazon.aws.ec2_security_group` task of
      `playbooks/tasks/create/aws.yml` on `profile == 'desktop'` (depends on
      T005)
- [ ] T018 [US3] Validate on real AWS (Constitution Principle III — no
      local substitute for an AWS security group): `create-vm.yml -e
      provider=aws -e profile=desktop` opens inbound 3389 on `ansible-sg`;
      a subsequent `create-vm.yml -e provider=aws -e profile=basic` leaves
      the 22-only exposure for that VM's use and does not remove the 3389
      rule the desktop VM added (depends on T017)

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T019 [P] Invoke the `review-documentation-here` skill (Documentation
      Standards close-out) — expected: no new doc tier needed, this feature
      touches only playbooks/task files
- [ ] T020 [P] Invoke the `format-markdown` skill once on all touched
      Markdown in `specs/014-desktop-profile/` and
      `docs/feature-requests/feat.create-destroy-vm/roadmap.md`
- [ ] T021 Run the full `quickstart.md` validation pass (tart desktop,
      docker+desktop rejection, AWS RDP scoping) end-to-end as a final
      cross-cutting smoke check

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A
- **Foundational (Phase 2)**: No dependencies beyond the existing
  codebase — BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational completion;
  US1/US2/US3 are otherwise independent of each other and may proceed in
  any order or in parallel
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational only
- **User Story 2 (P2)**: Depends on Foundational only (specifically T010);
  independent of US1/US3
- **User Story 3 (P3)**: Depends on Foundational only (specifically T005);
  independent of US1/US2

### Parallel Opportunities

- T002-T009 (the 8 per-provider create/destroy group-key tasks) can all run
  in parallel — 8 distinct files, no shared state
- T011 can run in parallel with T002-T009 (distinct file)
- Once Foundational (Phase 2) completes, US1, US2, and US3 can proceed in
  parallel — they touch disjoint files (`configure-profile*.yml` for US1;
  `assert-provider.yml` for US2; `tasks/create/aws.yml` for US3, already
  touched once in T005 but the US3 edit is additive)
- T019 and T020 (Polish) can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational
2. Complete Phase 3: User Story 1
3. **STOP and VALIDATE**: T014 confirms a desktop VM works end-to-end on
   tart
4. This alone delivers the feature's core value — every other story is a
   safety/security refinement

### Incremental Delivery

1. Foundational → `profile=basic` (default) behaves exactly as `linux`
   does today, now under an explicit `basic` group
2. + US1 → desktop VMs reachable through `create-vm.yml`/
   `configure-profile.yml` for the first time (MVP)
3. + US2 → docker+desktop guarded loudly
4. + US3 → AWS RDP exposure correctly scoped
