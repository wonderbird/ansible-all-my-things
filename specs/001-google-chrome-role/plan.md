# Implementation Plan: Ansible Role — Install Google Chrome (Stable)

**Branch**: `001-google-chrome-role` | **Date**: 2026-03-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-google-chrome-role/spec.md`

## Summary

Create the `google_chrome` Ansible role at `roles/google_chrome/` to install
`google-chrome-stable` on Ubuntu 24.04 AMD64 developer workstations. The role
follows the VS Code reference pattern (stat-based idempotency guard) adapted for
Chrome's specific apt source behaviour: Chrome's daily cron script manages
`google-chrome.list` and will overwrite any Ansible-managed `.list` file, so the
role creates `google-chrome.sources` (DEB822 format, never touched by Chrome's cron)
as its idempotency sentinel. All tasks carry the `not-supported-on-vagrant-arm64` tag.

## Technical Context

**Language/Version**: Ansible 2.19+ (YAML)
**Primary Dependencies**: `ansible.builtin.stat`, `ansible.builtin.get_url`,
`ansible.builtin.shell`, `ansible.builtin.copy`, `ansible.builtin.file`,
`ansible.builtin.apt`, `ansible.builtin.deb822_repository`
**Storage**: N/A
**Testing**: Manual playbook run on Ubuntu 24.04 AMD64 Vagrant/Docker VM per
`CONTRIBUTING.md`; role isolated as the only active role in
`configure-linux-roles.yml` during testing
**Target Platform**: Ubuntu 24.04 AMD64
**Project Type**: Ansible role
**Performance Goals**: N/A
**Constraints**: Fully idempotent (zero changes on consecutive runs);
all tasks tagged `not-supported-on-vagrant-arm64`
**Scale/Scope**: Single role, ~11 tasks

## Constitution Check

*GATE: Must pass before implementation. Re-check after implementation.*

| Principle | Status | Notes |
|---|---|---|
| I — Idempotency | PASS | Stat guard + `state: absent` cleanup task; `apt` module is inherently idempotent |
| II — Role-First Organisation | PASS | Standalone role in `roles/`; no playbook-level tasks |
| III — Test Locally Before Cloud | PASS | Role isolated in `configure-linux-roles.yml` during local VM testing |
| IV — Simplicity (YAGNI) | PASS | Minimal tasks; no per-user config; no speculative features |
| V — Conventional Commits | PASS | `feat:` for role creation; `docs:` for tech-debt entry |
| VI — Markdown Quality | PASS | Applies to docs only; plan.md complies |
| VII — Structured Problem Solving | PASS | Chrome apt source behaviour researched and documented in `research.md` |

## Project Structure

### Documentation (this feature)

```text
specs/001-google-chrome-role/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── spec.md              # Feature specification
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code

```text
roles/google_chrome/
├── defaults/
│   └── main.yml         # (empty defaults; no role variables needed)
├── meta/
│   └── main.yml         # Galaxy metadata, min_ansible_version: 2.19
└── tasks/
    └── main.yml         # All installation tasks

configure-linux-roles.yml   # Add google_chrome role entry with tag
docs/architecture/technical-debt/technical-debt.md  # New TD entry
```

## Complexity Tracking

No constitution violations requiring justification.

---

## Phase 0: Research

**Status**: Complete — see [research.md](research.md)

Key findings:

- Chrome's daily cron script (`/etc/cron.daily/google-chrome`) creates and owns
  `google-chrome.list`. It does NOT create or rename `.sources` files.
- Using `google-chrome.sources` (DEB822 format) as the role-managed file avoids
  all conflicts with Chrome's cron.
- `ansible.builtin.deb822_repository` (Ansible 2.15+) is the correct module.
- The `not-supported-on-vagrant-arm64` tag works via static role inheritance in
  `configure-linux-roles.yml`; individual task tags are added for robustness.

---

## Phase 1: Design

### Idempotency strategy

The role uses the same guard pattern as `playbooks/tasks/setup-vscode.yml`:

1. **Stat** `/etc/apt/sources.list.d/google-chrome.sources` at the start.
2. All apt source setup tasks run only when that file does **not** exist.
3. `google-chrome.sources` is created by `deb822_repository` (idempotent module,
   DEB822 format). Chrome's cron never touches this file.
4. A separate cleanup task (`state: absent` on `google-chrome.list`) runs on
   every playbook execution. This is a no-op when the file is absent (reports
   "ok"), so consecutive runs satisfy SC-002. It removes the file if Chrome's
   daily cron has recreated it between runs.

### Signing key handling

Follows VS Code pattern exactly:

1. Download ASCII-armored key to `/tmp/google-linux-signing-key.pub`.
2. Convert via `shell: cat ... | gpg --dearmor > /tmp/google-chrome.gpg`.
3. Copy binary keyring to `/etc/apt/keyrings/google-chrome.gpg` (root-owned,
   mode 0644).
4. Remove both temp files.

All four tasks are guarded by the stat check (step 1 of idempotency strategy).

### Apt source configuration

```yaml
deb822_repository:
  name: google-chrome
  types: [deb]
  uris: https://dl-ssl.google.com/linux/chrome/deb/
  suites: [stable]
  components: [main]
  architectures: [amd64]
  signed_by: /etc/apt/keyrings/google-chrome.gpg
  state: present
```

This creates `/etc/apt/sources.list.d/google-chrome.sources`. Guarded by stat
check.

### Package installation

```yaml
apt:
  name: google-chrome-stable
  state: present
```

Not guarded — `apt` with `state: present` is inherently idempotent (no-op if
already installed).

### `google-chrome.list` cleanup

```yaml
file:
  path: /etc/apt/sources.list.d/google-chrome.list
  state: absent
```

Runs on every execution. Reports "ok" if file is absent; removes it if present.
Prevents Chrome's cron-created `.list` from duplicating the `.sources` entry.

### Architecture tag application

Every task in `tasks/main.yml` carries `tags: [not-supported-on-vagrant-arm64]`.

The role entry in `configure-linux-roles.yml` also carries the tag:

```yaml
- role: google_chrome
  tags: not-supported-on-vagrant-arm64
```

This matches the play-level tag pattern used in `playbooks/setup-homebrew.yml`.

### Complete task sequence

```text
1.  stat: google-chrome.sources          → register google_chrome_sources_file
2.  get_url: signing key                 → when: not sources_file.exists
3.  shell: gpg --dearmor                 → when: not sources_file.exists
4.  copy: install keyring to keyrings/   → when: not sources_file.exists
5.  deb822_repository: add apt source   → when: not sources_file.exists
6.  file: remove temp key files (loop)  → when: not sources_file.exists
7.  apt: ensure apt-transport-https     → always
8.  apt: update_cache                   → always
9.  apt: install google-chrome-stable   → always
10. file: ensure google-chrome.list absent → always
```

All 10 tasks tagged `not-supported-on-vagrant-arm64`.

### Role file contents

#### `roles/google_chrome/meta/main.yml`

```yaml
#SPDX-License-Identifier: MIT-0
galaxy_info:
  author: Stefan Boos
  description: Install Google Chrome (stable) on Ubuntu AMD64
  company: n.a.
  issue_tracker_url: http://github.com/wonderbird/ansible-all-my-things/issues
  license: MIT
  min_ansible_version: 2.19
  galaxy_tags: []

dependencies: []
```

#### `roles/google_chrome/defaults/main.yml`

Empty (no role variables needed). Include file with SPDX header only.

### `configure-linux-roles.yml` change

Add after `claude_code`:

```yaml
- role: google_chrome
  tags: not-supported-on-vagrant-arm64
```

### Technical debt entry

Add `TD-003` to `docs/architecture/technical-debt/technical-debt.md`:

**TD-003a — Unpinned package versions across all installation roles**

Affects: `roles/google_chrome/tasks/main.yml`, `roles/cursor_ide/tasks/main.yml`,
`roles/claude_code/tasks/main.yml`.

All roles install the latest available package version rather than a pinned
version. Re-running after an upstream release installs a different version,
technically violating the idempotency principle at the package-version level.
Risk accepted for developer workstation tooling; revisit if fleet-wide version
consistency is required.

---

## Phase 1: Contracts

Not applicable — this is a purely internal Ansible role with no external interface.

---

## Architecture decision: two guard patterns are intentional

The `google_chrome` role (tag-based skip) and the `claude_code` role (hard assert)
use different architecture guard mechanisms deliberately:

- `claude_code` supports both AMD64 and ARM64. An unsupported architecture is a
  genuine operator error → hard assert is appropriate.
- `google_chrome` is AMD64-only. ARM64 Vagrant VMs on Apple Silicon are a normal,
  expected operating condition — graceful skip is correct, not a failure.

These patterns are not inconsistent. They encode different operational semantics.
No consolidation is needed. **TD-003b is not a valid technical debt item.**

---

## Deferred / Out of Scope

- Per-user Chrome configuration (extensions, policies, preferences).
- Handling pre-existing apt source entries from a manual `.deb` installation
  (out of scope per spec clarification Q2).
- Pinned Chrome version (technical debt; accepted risk).
