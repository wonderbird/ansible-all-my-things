# Tasks: Create and Destroy VM Playbooks

**Input**: Design documents from `specs/009-create-destroy-vm/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Grouped by user story for independent implementation and testing.
No test tasks — not requested in the specification.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependency)
- **[Story]**: User story this task belongs to (US1 = Create VM, US2 = Destroy VM)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initial files and state that both playbooks depend on.

- [ ] T001 Reset `inventories/vagrant_tart.yml` to empty-hosts state: keep groups
  `all`, `linux`, `vagrant_tart` each with `hosts: {}` — removes stale `lorien`
  entry so the pool is a clean slate per spec Assumptions
- [ ] T002 Create `playbooks/vars/hostname_pool.yml` with the ordered list of ten
  Star Trek TNG planet names: `vulcan`, `romulus`, `betazed`, `qonos`, `risa`,
  `cardassia`, `bajor`, `veridian`, `remus`, `baku` (FR-011)

---

## Phase 2: Foundational (Blocking Prerequisite for US1)

**Purpose**: Vagrantfile template is required before any create-VM task can run.

**⚠️ CRITICAL**: US1 cannot begin until this phase is complete.

- [ ] T003 Create `playbooks/templates/Vagrantfile.j2` — Jinja2 template for per-VM
  Vagrantfiles; variables: `hostname`, `vm_cpus`, `vm_memory_mb`, `vm_disk_gb`;
  modelled on `test/tart/Vagrantfile`; image `ghcr.io/cirruslabs/ubuntu:latest`;
  SSH user `admin`/`admin`

**Checkpoint**: Template ready — US1 implementation can begin.

---

## Phase 3: User Story 1 — Create VM (Priority: P1) 🎯 MVP

**Goal**: Single command creates a Tart VM, assigns the next unused TNG hostname,
registers it in inventory, and prints the hostname on completion.

**Independent Test**: Run `ansible-playbook playbooks/create-vm.yml` with no
extra-vars; verify a VM is created, a hostname is printed, and `inventories/vagrant_tart.yml`
contains the new host entry in all three groups.

- [ ] T004 [US1] Create `playbooks/tasks/create/tart.yml` — pool-check block:
  load `playbooks/vars/hostname_pool.yml` (include\_vars), load
  `inventories/vagrant_tart.yml` (include\_vars), compute `used_hostnames` from
  `all.hosts.keys()`, assert pool not exhausted (`fail` task with message naming
  `playbooks/vars/hostname_pool.yml`) **before any VM or infra action** (FR-007,
  Principle XII), set `hostname` to first unused pool entry
- [ ] T005 [US1] Extend `playbooks/tasks/create/tart.yml` — VM creation block:
  create `~/.local/share/ansible-vms/{{ hostname }}/` via `file` module, render
  `Vagrantfile.j2` into that directory via `template` module; run `vagrant up`
  via `shell` with `creates: ~/.local/share/ansible-vms/{{ hostname }}/.vagrant`
  guard (Principle I); `chdir` to vm\_dir
- [ ] T006 [US1] Extend `playbooks/tasks/create/tart.yml` — IP retrieval: run
  `vagrant ssh-config {{ hostname }} | grep HostName | awk '{print $2}'` via
  `shell`, `chdir` vm\_dir, `changed_when: false`; assert result non-empty
  (Principle XII); register as `vm_ip`
- [ ] T007 [US1] Extend `playbooks/tasks/create/tart.yml` — inventory update: load
  current `inventories/vagrant_tart.yml` (include\_vars), build updated dict using
  `combine(recursive=true)` adding new host to `all.hosts`, `linux.hosts`, and
  `vagrant_tart.hosts` with `ansible_host`, `ansible_port: 22`, `ansible_user:
  admin`, `ansible_ssh_private_key_file`; write back via `copy` with
  `content: "{{ updated | to_nice_yaml(indent=2) }}"` (idempotent); emit `debug`
  message printing assigned hostname (FR-006)
- [ ] T008 [US1] Create `playbooks/create-vm.yml` — hosts: localhost; vars:
  `vm_cpus: 4`, `vm_memory_mb: 8192`, `vm_disk_gb: 45` (FR-012); single task
  block that includes `tasks/create/tart.yml` via `ansible.builtin.include_tasks`

**Checkpoint**: US1 complete — `create-vm.yml` functional and manually testable.

---

## Phase 4: User Story 2 — Destroy VM (Priority: P2)

**Goal**: Single command (requiring `hostname`) destroys the Tart VM and removes
all inventory references, leaving no dangling entries.

**Independent Test**: Given a running VM `vulcan` (created via US1), run
`ansible-playbook playbooks/destroy-vm.yml -e hostname=vulcan`; verify VM is gone
and `vulcan` is absent from all groups in `inventories/vagrant_tart.yml`.

- [ ] T009 [US2] Create `playbooks/tasks/destroy/tart.yml` — inventory check block:
  load `inventories/vagrant_tart.yml` (include\_vars); assert `hostname` is
  defined (Principle XII — fail loud if not provided); assert `hostname` is present
  in `all.hosts` with actionable error message (FR-010, Principle XII) **before
  any VM or infra action**
- [ ] T010 [US2] Extend `playbooks/tasks/destroy/tart.yml` — VM destruction block:
  set `vm_dir` to `~/.local/share/ansible-vms/{{ hostname }}`; run `vagrant
  destroy -f` via `shell`, `chdir` vm\_dir, `when: vm_dir stat exists`; emit
  `warn` if vm\_dir absent (VM already gone — stale inventory entry; spec edge
  case)
- [ ] T011 [US2] Extend `playbooks/tasks/destroy/tart.yml` — inventory cleanup:
  load `inventories/vagrant_tart.yml` (include\_vars), rebuild each group's
  `hosts` dict via `dict2items | selectattr('key','!=',hostname) | items2dict`;
  write back via `copy` with `content: "{{ cleaned | to_nice_yaml(indent=2) }}"`;
  assert hostname absent from result (Principle XII)
- [ ] T012 [US2] Create `playbooks/destroy-vm.yml` — hosts: localhost; assert
  `hostname` is defined at playbook level (fail loud if missing — FR-008,
  Principle XII); includes `tasks/destroy/tart.yml` via
  `ansible.builtin.include_tasks`

**Checkpoint**: US2 complete — `destroy-vm.yml` functional and manually testable
independently of US1.

---

## Phase 5: Polish & Edge Case Validation

**Purpose**: Verify failure-mode contracts defined in spec.md.

- [ ] T013 [P] Manually validate FR-007 (pool exhaustion): populate
  `inventories/vagrant_tart.yml` with all 10 TNG names as dummy hosts; run
  `ansible-playbook playbooks/create-vm.yml`; confirm playbook fails with pool
  exhaustion error **before** any VM directory is created; restore inventory
- [ ] T014 [P] Manually validate FR-010 (unknown hostname): run
  `ansible-playbook playbooks/destroy-vm.yml -e hostname=nonexistent`; confirm
  immediate failure with actionable error; confirm no VM or filesystem action
  was taken

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — blocks US1
- **US1 (Phase 3)**: Depends on Phase 2 (template); Phase 1 (pool vars)
- **US2 (Phase 4)**: Depends on Phase 1 (inventory reset only); independent of US1
- **Polish (Phase 5)**: Depends on Phase 3 and Phase 4 being complete

### User Story Dependencies

- **US1 (P1)**: Requires Phase 1 + Phase 2 complete
- **US2 (P2)**: Requires Phase 1 complete only; can proceed in parallel with
  Phase 2 and US1

### Within Each User Story

- T004 → T005 → T006 → T007 → T008 (sequential, same file)
- T009 → T010 → T011 → T012 (sequential, same file)

### Parallel Opportunities

- T001 and T002 (Phase 1) can run in parallel — different files
- T003 (Phase 2) and Phase 4 (T009–T012) can run in parallel after Phase 1
- T013 and T014 (Phase 5) can run in parallel — independent validations

---

## Parallel Example: After Phase 1 Complete

```text
Stream A: T003 (Vagrantfile template) → T004 → T005 → T006 → T007 → T008
Stream B: T009 → T010 → T011 → T012
```

Both streams unblock after T001 and T002 complete.

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1 (T001, T002)
2. Complete Phase 2 (T003)
3. Complete Phase 3: US1 (T004–T008)
4. **STOP and VALIDATE**: `ansible-playbook playbooks/create-vm.yml`

### Full Delivery

1. Complete Phase 1 → Phase 2 → Phase 3 (US1)
2. Complete Phase 4 (US2) — can overlap with Phase 3 after Phase 1
3. Complete Phase 5 validations
4. Run quickstart.md end-to-end

### Parallelism Note

Phase 4 (US2: destroy-vm) is independent of Phase 2 and US1. After Phase 1
completes, a second implementer can begin T009 immediately while the first
works on T003–T008.
