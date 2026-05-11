# PRD: Kiro IDE — Install and Branch Hygiene

## Section 1: Install Kiro IDE Role

### Problem

Kiro IDE is currently installed manually on development VMs. There is no
automated, reproducible way to ensure Kiro IDE is present on `rivendell`
(AWS Linux, Ubuntu) and `hobbiton` (Hetzner Cloud Linux, Ubuntu). Manual
installation creates environment drift and blocks consistent tooling across
hosts.

### Goal

Automate Kiro IDE installation on `rivendell` and `hobbiton` via a new
dedicated Ansible role (`roles/setup-kiro-ide/`) so that applying the role
idempotently yields a working Kiro IDE installation on both hosts.

### Scope

- Target hosts: `rivendell` (AWS Linux Ubuntu) and `hobbiton` (Hetzner Cloud
  Linux Ubuntu).
- OS: Ubuntu Linux only.
- SSH user: `galadriel`.
- Deliverable: a new role `roles/setup-kiro-ide/` wired into the existing
  playbook(s) that target the `linux` host group.

### Out of scope

- Kiro IDE extensions or per-user settings.
- Non-Ubuntu operating systems (Windows, macOS).
- Test VMs (`dagorlad`, `lorien`).

### Acceptance Criteria

1. Running the role against `rivendell` or `hobbiton` produces a working Kiro
   IDE installation accessible to user `galadriel`.
2. Re-running the role (idempotency check) produces no changes and no errors.
3. The role follows Constitution Principle II: logic lives in
   `roles/setup-kiro-ide/`, not as ad-hoc tasks in a playbook.
4. The role includes a Molecule scenario covering the full
   create → converge → idempotence → verify → destroy lifecycle.

---

## Section 2: Port `kiro` Branch Enhancements to `main`

### Problem

The `kiro` feature branch contains both Kiro-specific code and unrelated
general improvements (refactoring, bug fixes, dependency updates). Mixing
them in a single branch blocks a clean merge, increases merge complexity,
and prevents the general improvements from being shared on `main` while
Kiro-specific work is still in progress.

### Goal

Extract all non-Kiro general enhancements from the `kiro` branch and merge
them into `main` cleanly, so that:

- `main` benefits from the general improvements immediately.
- The `kiro` branch carries only Kiro-specific content.
- Future merge of `kiro` into `main` is straightforward.

### Scope

- Changes already present on the `kiro` branch (no new development).
- Porting strategy: atomic `git cherry-pick` for self-contained commits;
  manual re-implementation for commits that mix Kiro and non-Kiro logic.

### Out of scope

- New feature development on either branch.
- Merging the Kiro-specific feature itself (that is a separate future step
  once the install role is complete).

### Acceptance Criteria

1. All non-Kiro general enhancements from `kiro` are present on `main` via
   atomic commits.
2. `git diff main..kiro` shows only Kiro-specific content after porting.
3. The `kiro` branch rebases cleanly onto the updated `main` with no
   unresolved conflicts.
4. Each ported commit follows the conventional-commit format (Constitution
   Principle V).
