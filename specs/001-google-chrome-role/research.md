# Research: google_chrome Role

**Branch**: `001-google-chrome-role` | **Date**: 2026-03-13

## RQ-001 — Chrome apt source post-install behaviour on Ubuntu 24.04

**Question**: Does Chrome's installer rename or modify apt source files after
installation, similar to VS Code renaming `vscode.list` → `vscode.sources`?

### Decision

Chrome does **not** rename any apt source file. The behaviour is fundamentally
different from VS Code. Chrome's package installs a daily cron script at
`/etc/cron.daily/google-chrome` (sourced from
`/opt/google/chrome/cron/google-chrome`). That script:

- **Creates** `/etc/apt/sources.list.d/google-chrome.list` (legacy one-line format)
- **Removes** `/etc/apt/sources.list.d/google-chrome.list` and
  `/etc/apt/sources.list.d/google-chrome-stable.list` when cleaning

The script contains no code path that creates, reads, writes, or renames a
`.sources` file. The script uses this content for `google-chrome.list`:

```
### THIS FILE IS AUTOMATICALLY CONFIGURED ###
# You may comment out this entry, but any other modifications may be lost.
deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main
```

Note the absence of a `signed-by` reference and the use of `http://` rather
than `https://`.

### Key implication for this role

If the Ansible role writes `google-chrome.list` using `apt_repository`
(legacy format with a `signed-by` reference), Chrome's daily cron script will
subsequently **overwrite** that file with its own content, removing the
`signed-by` reference. On the next playbook run, `apt_repository` would detect
the content change and report a "changed" task, **breaking idempotency
(SC-002)**.

If the role writes `google-chrome.sources` (DEB822 format) instead, Chrome's
cron script will never touch it (the cron only manages `google-chrome.list`).
The `.sources` file is therefore a stable, role-owned file.

However, Chrome's daily cron will still create `google-chrome.list` (alongside
the role's `google-chrome.sources`), resulting in a **duplicate apt source
definition** that produces apt warnings. The role must include a cleanup task
that removes `google-chrome.list` on every run.

### Rationale for chosen approach

1. Create `google-chrome.sources` (DEB822 format) as the role-managed source
   file using the `deb822_repository` Ansible module (available since 2.15;
   project minimum is 2.19).
2. Use `google-chrome.sources` existence as the idempotency guard (stat check),
   paralleling the VS Code pattern that guards on `vscode.sources`.
3. Include an always-running cleanup task that ensures `google-chrome.list` is
   absent. This task is a no-op (`state: absent`) when the file does not exist,
   so it reports "ok" on consecutive runs (satisfying SC-002). It removes the
   file if Chrome's cron has recreated it between runs.

### Alternatives considered

- **Guard on GPG keyring file** (`/etc/apt/keyrings/google-chrome.gpg`): Also
  a stable sentinel since Chrome's cron does not touch the keyring. Rejected
  because using the `.sources` file as the guard is consistent with the VS Code
  reference pattern and keeps the intent self-documenting.
- **Use `google-chrome.list` (legacy format) as role-owned file**: Rejected
  because Chrome's daily cron overwrites this file, removing the `signed-by`
  reference and breaking idempotency.
- **Configure `/etc/default/google-chrome` with `repo_add_once="false"`**:
  Would prevent Chrome's cron from recreating `google-chrome.list`. Rejected as
  unnecessary complexity (YAGNI); the cleanup task is simpler.
- **Guard everything on `google-chrome.list` absence**: Rejected because
  Chrome's cron recreates `google-chrome.list`, which would trigger the setup
  tasks on every subsequent run.

### Confidence: High

Primary source: actual Chrome cron script source code at
`/opt/google/chrome/cron/google-chrome`. Corroborated by Ubuntu Community Hub
thread on Chrome apt sources after Ubuntu 22.04→24.04 upgrade, which confirms
the `.sources` file is created by Ubuntu's own `ubuntu-release-upgrader`
tooling, not by Chrome.

---

## RQ-002 — Ansible tag inheritance in roles

**Question**: Do Ansible roles support `tags` the same way playbooks do?
Specifically, does tagging a role entry in the `roles:` section of a playbook
propagate the tag to all tasks inside the role?

### Decision

Yes, with a static-vs-dynamic caveat:

- **`roles:` section** (used by `configure-linux-roles.yml`): role loading is
  static (equivalent to `import_role`). A tag applied to the role entry is
  inherited by all tasks in the role. Running
  `--skip-tags not-supported-on-vagrant-arm64` skips every task in the role.
- **`include_role`** (dynamic): tag inheritance does NOT work. Tasks would run
  regardless of the role-level tag.

### Chosen approach

Tag every individual task inside `tasks/main.yml` with
`tags: [not-supported-on-vagrant-arm64]` AND tag the role entry in
`configure-linux-roles.yml` with the same tag. The individual task tags satisfy
FR-004 literally and remain correct if the role is later invoked via
`include_role`. The role-level tag in the playbook matches the `setup-homebrew.yml`
pattern and provides a single point of control at the playbook level.

### Relationship to `claude_code` pattern

The `claude_code` role uses a hard `assert` task as its architecture guard.
`google_chrome` uses only the tag-based skip mechanism. These are intentionally
different:

- `claude_code` supports AMD64 and ARM64; any other architecture is an operator
  error → hard assert is correct.
- `google_chrome` is AMD64-only; ARM64 Vagrant VMs on Apple Silicon are a normal,
  expected condition → graceful skip is correct.

No technical debt; no consolidation needed.

---

## RQ-003 — Ansible module for DEB822 apt sources

**Question**: Which Ansible module creates DEB822 (`.sources`) format apt
source files on Ubuntu 24.04?

### Decision

`ansible.builtin.deb822_repository` (added in Ansible 2.15, project minimum is
2.19). This module creates and manages `.sources` files natively, handles
idempotency, and is the correct tool for Ubuntu 24.04 targets where DEB822 is
the preferred format.

The `apt_repository` module creates legacy `.list` format files only. It is
used by the VS Code reference pattern (which pre-dates Ubuntu 24.04 best
practice), but should not be used for new roles targeting Ubuntu 24.04.

### Rationale

Using `deb822_repository` for `google-chrome.sources` is idiomatic for the
target Ubuntu version, produces a `signed-by` reference that Chrome's cron
cannot strip (because the cron only manages `google-chrome.list`), and enables
the guard pattern that parallels VS Code.
