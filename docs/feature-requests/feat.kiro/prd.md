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

