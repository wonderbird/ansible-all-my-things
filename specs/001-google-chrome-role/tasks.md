# Tasks: Ansible Role — Install Google Chrome (Stable)

**Input**: Design documents from `specs/001-google-chrome-role/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story. No tests are requested; validation
tasks use manual playbook runs per Constitution §III.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup — Role Scaffolding

**Purpose**: Create the standard Ansible role directory structure.

- [x] T001 [P] Create `roles/google_chrome/meta/main.yml` with SPDX header and galaxy_info (author, description, license MIT, min_ansible_version 2.19, empty dependencies)
- [x] T002 [P] Create `roles/google_chrome/defaults/main.yml` with SPDX header and `---` only (no role variables needed)
- [x] T003 [P] Create `roles/google_chrome/tasks/main.yml` with SPDX header and `---` only (empty task skeleton)

**Checkpoint**: Role directory structure exists at `roles/google_chrome/` with `meta/`, `defaults/`, `tasks/`

---

## Phase 2: User Story 1 — Fresh Chrome Installation on AMD64 Workstation (Priority: P1) 🎯 MVP

**Goal**: Install `google-chrome-stable` on a clean Ubuntu 24.04 AMD64 machine
via Google's official apt repository, with the signing key correctly registered.

**Independent Test**: Run the playbook against a clean Ubuntu 24.04 AMD64 VM
(Vagrant/Docker). Verify that `google-chrome-stable` is installed, `google-chrome`
is launchable from the command line, and `/etc/apt/keyrings/google-chrome.gpg`
plus `/etc/apt/sources.list.d/google-chrome.sources` both exist.

### Implementation for User Story 1

- [x] T004 [US1] Add stat task to `roles/google_chrome/tasks/main.yml`: check existence of `/etc/apt/sources.list.d/google-chrome.sources`, register result as `google_chrome_sources_file`
- [x] T005 [US1] Add get_url task to `roles/google_chrome/tasks/main.yml`: download `https://dl-ssl.google.com/linux/linux_signing_key.pub` to `/tmp/google-linux-signing-key.pub` (mode 0644); guard with `when: not google_chrome_sources_file.stat.exists`
- [x] T006 [US1] Add shell task to `roles/google_chrome/tasks/main.yml`: convert ASCII-armored key via `cat /tmp/google-linux-signing-key.pub | gpg --dearmor > /tmp/google-chrome.gpg`; guard with `when: not google_chrome_sources_file.stat.exists`
- [x] T007 [US1] Add copy task to `roles/google_chrome/tasks/main.yml`: install binary keyring to `/etc/apt/keyrings/google-chrome.gpg` (owner root, group root, mode 0644, remote_src yes); guard with `when: not google_chrome_sources_file.stat.exists`
- [x] T008 [US1] Add deb822_repository task to `roles/google_chrome/tasks/main.yml`: create `google-chrome.sources` (types: deb, uris: `https://dl-ssl.google.com/linux/chrome/deb/`, suites: stable, components: main, architectures: amd64, signed_by: `/etc/apt/keyrings/google-chrome.gpg`, state: present); guard with `when: not google_chrome_sources_file.stat.exists`
- [x] T009 [US1] Add file loop task to `roles/google_chrome/tasks/main.yml`: remove `/tmp/google-linux-signing-key.pub` and `/tmp/google-chrome.gpg` (state: absent); guard with `when: not google_chrome_sources_file.stat.exists`
- [x] T010 [US1] Add apt task to `roles/google_chrome/tasks/main.yml`: ensure `apt-transport-https` is present (state: present); no guard — always runs
- [x] T011+T012 [US1] Add apt task to `roles/google_chrome/tasks/main.yml`: install `google-chrome-stable` (state: present, update_cache: true); no guard — always runs. Note: T011 (standalone update_cache) was merged into T012 during validation — standalone `update_cache: true` always reports `changed`, breaking SC-002.

**Checkpoint**: Run playbook against a clean AMD64 VM. `google-chrome-stable` must
be installed, launchable, and SC-001 satisfied.

---

## Phase 3: User Story 2 — Idempotent Re-Run Without Errors (Priority: P2)

**Goal**: Ensure a consecutive second playbook run reports zero changed tasks
and zero failures, even after Chrome's daily cron job has recreated
`google-chrome.list`.

**Independent Test**: Run the playbook twice consecutively against the same
AMD64 VM used in Phase 2. The second run must report `changed=0 failed=0` for
all `google_chrome` role tasks.

### Implementation for User Story 2

- [x] T013 [US2] Add file task to `roles/google_chrome/tasks/main.yml`: ensure `/etc/apt/sources.list.d/google-chrome.list` is absent (state: absent); no guard — always runs (no-op when file does not exist; removes file created by Chrome's daily cron when it does exist)

**Checkpoint**: Run playbook twice consecutively. Second run must report
`changed=0 failed=0`, satisfying SC-002.

---

## Phase 4: User Story 3 — Graceful Skip on Non-AMD64 Machines (Priority: P3)

**Goal**: All role tasks are skipped without errors when the playbook runs
on an ARM64 machine with `--skip-tags not-supported-on-vagrant-arm64`.

**Independent Test**: Run `ansible-playbook configure-linux-roles.yml
--skip-tags not-supported-on-vagrant-arm64` against an ARM64 Vagrant VM.
All `google_chrome` tasks must be skipped and the playbook must complete
with no failures, satisfying SC-003.

### Implementation for User Story 3

- [x] T014 [US3] Add `tags: [not-supported-on-vagrant-arm64]` to every task in `roles/google_chrome/tasks/main.yml` (all 10 tasks: T004 through T013)
- [x] T015 [P] [US3] Add `google_chrome` role entry to `configure-linux-roles.yml` after `claude_code`, with `tags: not-supported-on-vagrant-arm64`

**Checkpoint**: Run playbook with `--skip-tags not-supported-on-vagrant-arm64`
on ARM64 VM. All `google_chrome` tasks must show as skipped, satisfying SC-003.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates that apply across the whole codebase.

- [x] T016 [P] Add `TD-003` entry to `docs/architecture/technical-debt/technical-debt.md`: unpinned package versions across all installation roles (`google_chrome`, `cursor_ide`, `claude_code`) — latest-available version installs violate package-level idempotency; accepted risk for developer workstation tooling

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — T001, T002, T003 can all start immediately and run in parallel
- **US1 (Phase 2)**: Depends on Phase 1 complete — T004 through T012 are sequential (all write to `tasks/main.yml`)
- **US2 (Phase 3)**: Depends on Phase 2 complete — T013 adds a task to `tasks/main.yml`
- **US3 (Phase 4)**: Depends on Phase 3 complete — T014 modifies `tasks/main.yml`; T015 is independent (different file, [P])
- **Polish (Phase 5)**: Independent — T016 can run at any time (different file, [P])

### Within Each Phase

- T004–T013: Sequential — each appends a task to `roles/google_chrome/tasks/main.yml`
- T014 and T015: T014 modifies `tasks/main.yml`; T015 modifies `configure-linux-roles.yml` — can run in parallel with each other

---

## Parallel Execution Example: Phase 1

```bash
# All three setup tasks write different files — launch together:
Task T001: roles/google_chrome/meta/main.yml
Task T002: roles/google_chrome/defaults/main.yml
Task T003: roles/google_chrome/tasks/main.yml
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup — create role structure
2. Complete Phase 2: User Story 1 — full installation logic
3. **STOP and VALIDATE**: Run playbook on clean AMD64 VM, verify Chrome installs
4. Proceed to Phase 3 (US2) only after SC-001 is satisfied

### Incremental Delivery

1. Phase 1 → role structure ready
2. Phase 2 → Chrome installs on clean AMD64 machine (MVP, SC-001)
3. Phase 3 → consecutive runs are clean (SC-002)
4. Phase 4 → ARM64 machines skip gracefully (SC-003)
5. Phase 5 → tech debt documented

---

## Notes

- [P] tasks write to different files and have no interdependencies
- All tasks in `tasks/main.yml` are sequential (same file, order matters)
- The `deb822_repository` module requires Ansible 2.15+; project minimum is 2.19 ✓
- The `shell: gpg --dearmor` task needs `changed_when: false` or a `creates:` guard to avoid reporting "changed" on every run — but it is already guarded by the stat check (`when: not google_chrome_sources_file.stat.exists`), so it only runs once
- Validate Constitution §III: test on local Vagrant/Docker VM before any cloud apply
- Each commit should follow Constitution §V conventional commit format (`feat:` for role tasks, `docs:` for tech-debt entry)
