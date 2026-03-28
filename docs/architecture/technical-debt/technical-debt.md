# Technical Debt Register

This document collects known technical debt and accepted risks in the project.
Each entry records the context, the risk, and why it was accepted or deferred.

New entries are appended as they are identified, typically during code reviews.

## Entry format

Each entry uses the following fields:

- **ID** — sequential identifier, e.g. `TD-001`
- **Title** — short description
- **Category** — `Accepted Risk` or `Technical Debt`
- **Severity** — `Critical`, `High`, `Medium`, or `Low`
- **Affected file(s)** — file references
- **Description** — what the issue is and why it matters
- **Mitigation** — controls that reduce the risk today
- **Status** — `Open`, `Resolved`, or `Wont-fix`
- **Date added**

---

## TD-001 — No integrity check on the Claude Code installer script

- **Category:** Accepted Risk
- **Severity:** High
- **Affected file(s):** [roles/claude_code/tasks/main.yml](../../roles/claude_code/tasks/main.yml)
- **Date added:** 2026-02-27

### TD-001: Description

The Claude Code installer script is downloaded from `https://claude.ai/install.sh`
and executed directly via the `shell` module without any checksum verification.
A compromise of Anthropic's CDN or a supply-chain attack on the install script
endpoint could deliver a malicious script that runs under the target user's account.

The binary integrity verification that follows catches post-installation tampering
of the `claude` binary itself, but it does not protect against harm done by a
malicious installer before the binary is written to disk.

### TD-001: Mitigation

HTTPS transport provides the primary protection: the TLS connection to `claude.ai`
prevents in-transit modification and authenticates the server's identity.
This is the same trust model used by widely accepted installers such as Homebrew,
rustup, and the official Node.js installer.

Additionally, the subsequent binary checksum verification (comparing the installed
binary against the manifest published by Anthropic) limits the damage a compromised
installer could do to the binary itself.

### TD-001: Ideas for solution

Use VirusTotal:

- [VirusTotal: URL Scan of https://claude.ai/install.sh](https://www.virustotal.com/gui/url/128ceb81537736671e63bc2d1c028b5cd6cf1749c4a940fcc0646e41be7e0aec/details)

### TD-001: Status

Open — accepted risk. Revisit if Anthropic publishes installer checksums.

---

## TD-002 — Playbooks contain direct tasks instead of only orchestrating roles

- **Category:** Technical Debt
- **Severity:** High
- **Affected file(s):**
  - [playbooks/reboot-if-required.yml](../../playbooks/reboot-if-required.yml)
  - [playbooks/setup-basics.yml](../../playbooks/setup-basics.yml)
  - [playbooks/setup-desktop-apps.yml](../../playbooks/setup-desktop-apps.yml)
  - [playbooks/setup-desktop.yml](../../playbooks/setup-desktop.yml)
  - [playbooks/setup-homebrew.yml](../../playbooks/setup-homebrew.yml)
  - [playbooks/setup-keyring.yml](../../playbooks/setup-keyring.yml)
  - [playbooks/setup-nodejs.yml](../../playbooks/setup-nodejs.yml)
  - [playbooks/setup-users.yml](../../playbooks/setup-users.yml)
- **Date added:** 2026-03-12

### TD-002: Description

Constitution Principle II (Role-First Organisation) requires that playbooks only
orchestrate roles and must not contain implementation logic (tasks, handlers, or
templates) directly. All eight playbooks listed above pre-date the ratification
of the constitution (2026-03-11) and contain direct task lists.

When the constitution was ratified, no refactoring migration was performed. New
work continued to follow the pre-existing pattern: commit `85acad9` added the
`.bash_profile must exist` task directly to `playbooks/setup-users.yml` — the
first post-ratification addition that violates Principle II. Every subsequent
task added directly to a playbook will compound this debt.

### TD-002: Mitigation

The playbooks are functional and tested. The debt does not affect correctness
today; it affects modularity, reusability, and independent testability of
capabilities. No new playbook-level tasks should be added until the affected
playbook is refactored into a role.

### TD-002: Status

Open — to be addressed as part of a dedicated refactoring effort. Each playbook
should be migrated to a corresponding role in `roles/` one at a time, following
the testing procedure in `CONTRIBUTING.md`.

---

## TD-003 — Unpinned package versions across installation roles

- **Category:** Accepted Risk
- **Severity:** Low
- **Affected file(s):**
  - [roles/google_chrome/tasks/main.yml](../../roles/google_chrome/tasks/main.yml)
  - [roles/cursor_ide/tasks/main.yml](../../roles/cursor_ide/tasks/main.yml)
  - [roles/claude_code/tasks/main.yml](../../roles/claude_code/tasks/main.yml)
- **Date added:** 2026-03-13

### TD-003: Description

All three installation roles install the latest available version of their
respective package (`google-chrome-stable`, Cursor IDE, Claude Code) rather
than a pinned, reproducible version. A package update that introduces a
breaking change or regression will be silently applied on the next playbook
run, and a re-run on the same machine will install a different version than
the original run.

This violates strict package-level idempotency: running the playbook twice
against the same machine at different points in time may produce different
installed versions.

### TD-003: Mitigation

Developer workstation tooling is expected to track the latest stable release.
The risk of a breaking update is low and recovery is fast (re-run with the
previous version pinned or wait for a patch release). Pinning would require
a maintenance process to update pinned versions regularly, which is not
justified for this use case.

### TD-003: Status

Open — accepted risk for developer workstation tooling.

---

## TD-004 — setup-vscode.yml uses outdated apt source and shell patterns

- **Category:** Technical Debt
- **Severity:** Medium
- **Affected file(s):**
  - [playbooks/tasks/setup-vscode.yml](../../playbooks/tasks/setup-vscode.yml)
- **Date added:** 2026-03-14

### TD-004: Description

`setup-vscode.yml` predates the patterns established in `roles/google_chrome`
and has several issues:

- Uses `apt_repository` (writes a deprecated one-liner `.list` file) instead
  of `ansible.builtin.deb822_repository`. The VS Code installer then renames
  the file to `.sources` — the role relies on this installer side-effect rather
  than managing the format directly.
- The `shell` task that converts the GPG key has no `changed_when: false`,
  causing it to report "changed" on every run where the guard condition is true.
- A standalone `apt: update_cache: yes` task always reports "changed",
  violating idempotency on consecutive runs.
- Uses bare module names (`stat`, `get_url`, `shell`, `copy`, `apt`) instead
  of FQCN (`ansible.builtin.*`), which is required by current Ansible best
  practices and linting.
- Installs `apt-transport-https`, a legacy transitional package that has been
  a no-op since Ubuntu 18.04 (apt has built-in HTTPS support). The
  `roles/google_chrome` role does not install this package; `setup-vscode.yml`
  should follow the same approach when migrated to a role.

### TD-004: Mitigation

The playbook is functional. The idempotency issues only manifest before VS Code
is installed (first run). Subsequent runs are unaffected by the `update_cache`
issue because the stat guard skips the problematic tasks.

### TD-004: Status

Open — to be addressed when `setup-vscode.yml` is migrated to a role (see TD-002).

---

## TD-005 — cursor_ide role uses bare module names and downloads on every run

- **Category:** Technical Debt
- **Severity:** Medium
- **Affected file(s):**
  - [roles/cursor_ide/tasks/main.yml](../../roles/cursor_ide/tasks/main.yml)
- **Date added:** 2026-03-14

### TD-005: Description

The `cursor_ide` role has two issues:

- Uses bare module names (`get_url`, `apt`, `file`, `copy`, `debug`,
  `set_fact`, `blockinfile`) instead of FQCN (`ansible.builtin.*`).
- `get_url` downloads `cursor.deb` on every playbook run with no idempotency
  guard. The subsequent `apt: deb:` install is idempotent, but the network
  download is not — it hits the Cursor API endpoint unnecessarily on every run.

### TD-005: Mitigation

The role is functional. The redundant download is a minor inefficiency rather
than a correctness issue. FQCN is a style concern with no runtime impact.

### TD-005: Status

Open — address FQCN and download guard in a dedicated refactor.

---

## TD-006 — No ansible-lint configured

- **Category:** Technical Debt
- **Severity:** Medium
- **Affected file(s):** entire repository
- **Date added:** 2026-03-14

### TD-006: Description

The project has no `ansible-lint` setup. Several issues found during manual
review of `setup-vscode.yml` and `roles/cursor_ide` (bare module names,
missing `changed_when`, deprecated modules, spurious "changed" on idempotent
runs) would have been caught automatically by `ansible-lint` at commit time.

Without linting, code quality regressions in new roles and playbooks are only
caught during manual review or test runs.

### TD-006: Mitigation

None currently. Issues are caught through manual review only.

### TD-006: Ideas for solution

- Add `ansible-lint` to the Python `requirements.txt`.
- Add a `.ansible-lint` config file with a suitable profile (`basic` to start,
  tightening over time).
- Wire it into a pre-commit hook or a CI step so it runs automatically on
  every commit.

### TD-006: Status

Open — introducing ansible-lint will initially produce findings against existing
playbooks. Recommended approach: start with the `basic` profile and suppress
existing violations with `# noqa` annotations or profile relaxation until they
are fixed as part of TD-002, TD-004, and TD-005.

---

## TD-007 — No integrity check on the Google signing key download

- **Category:** Accepted Risk
- **Severity:** Medium
- **Affected file(s):** [roles/google_chrome/tasks/main.yml](../../roles/google_chrome/tasks/main.yml)
- **Date added:** 2026-03-14

### TD-007: Description

The Google apt signing key is fetched from
`https://dl-ssl.google.com/linux/linux_signing_key.pub`
via `ansible.builtin.get_url` without a `checksum:` parameter. This key is
installed into the system-wide apt keyring and subsequently authenticates all
packages delivered from the Google apt repository. A compromise of Google's CDN
or a TLS bypass could deliver a tampered key, enabling installation of malicious
packages on every future `apt` run.

This is the same class of risk as TD-001 (Claude Code installer script without
checksum), but the artifact differs: TD-001 concerns an executable script that
runs under the user's account; this entry concerns a GPG public key that controls
apt package trust. The blast radius and resolution path are independent.

### TD-007: Mitigation

HTTPS transport provides the primary protection: the TLS connection to
`dl-ssl.google.com` prevents in-transit modification and authenticates the
server's identity. This is the same trust model used by the official Chrome
installation instructions published by Google.

Additionally, the key is only downloaded once — the `.sources` file footprint
guard (`when: not google_chrome_sources_file.stat.exists`) prevents
re-downloading on subsequent runs.

### TD-007: Ideas for solution

- Add a `checksum:` parameter to the `get_url` task once Google publishes a
  stable checksum for the signing key file.
- Alternatively, verify the GPG key fingerprint after import using
  `gpg --fingerprint` and fail the play if it does not match the expected value.

### TD-007: Status

Open — accepted risk. Revisit if Google publishes a checksum for the signing
key, or if a key fingerprint verification step is added to the role.

---

## TD-008 — Chromium backup has no guard for a missing profile directory

- **Category:** Technical Debt
- **Severity:** Low
- **Affected file(s):** [playbooks/backup/chromium-settings.yml](../../playbooks/backup/chromium-settings.yml)
- **Date added:** 2026-03-27

### TD-008: Description

`playbooks/backup/chromium-settings.yml` passes the Chromium profile path
directly to `include_tasks: backup.yml` without first checking whether the
directory exists. If Chromium is not installed (or its snap profile directory
is absent), the `archive` module receives a non-existent path and the play
fails instead of skipping gracefully.

This gap was discovered during the implementation of the Google Chrome backup
(`playbooks/backup/google-chrome-settings.yml`), which adds a `stat` guard and
a `debug` notification as the correct pattern. The Chromium playbook was not
fixed in the same change to keep the changeset focused.

### TD-008: Mitigation

Chromium is always installed on the target desktop host (`hobbiton`), so the
missing directory condition does not arise in practice today. The risk is
limited to hypothetical runs against a host where Chromium has been removed.

### TD-008: Ideas for solution

Apply the same `stat` + `when:` + `debug` pattern used in
`google-chrome-settings.yml`:

```yaml
- name: Check if Chromium profile exists
  stat:
    path: "/home/{{ backup_user }}/snap/chromium/common/chromium/Default"
  register: chromium_profile

- name: Notify that no Chromium profile was found
  debug:
    msg: "No Chromium profile found — skipping backup."
  when: not chromium_profile.stat.exists

- include_tasks: backup.yml
  when: chromium_profile.stat.exists
  vars:
    ...
```

### TD-008: Status

Open — to be fixed in a dedicated commit or as part of a future backup
hardening pass.
