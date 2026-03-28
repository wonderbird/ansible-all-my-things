# Research: Backup Google Chrome Browser Configuration

## Findings

### Decision 1: Source path for Chrome configuration

**Decision**: `~/.config/google-chrome/Default`

**Rationale**: This is the standard profile path for a system-installed
(non-snap) Google Chrome on Ubuntu Linux. Confirmed by the user. The
`google_chrome` role installs `google-chrome-stable` via the official Google
apt repository (DEB822 format), not as a snap — consistent with the
`.config/` path.

**Alternatives considered**: `/home/user/snap/google-chrome/…` (snap
installation) — not applicable; Chrome is installed via apt in this repo.

---

### Decision 2: Exclusion patterns

**Decision**: Reuse identical exclusion patterns from `playbooks/backup/chromium-settings.yml`:

- `*Cache*`, `*cache*`
- `*History*`
- `*Local Storage*`, `*Session Storage*`, `*SharedStorage*`, `*WebStorage*`
- `*blob_storage*`
- `*Favicons*`

**Rationale**: Google Chrome and Chromium share the same profile directory
structure (Chrome is built on Chromium). The same file categories are ephemeral
or large in both browsers. No additional exclusions are needed. Saved passwords
(`Login Data`) are intentionally retained — same behaviour as Chromium.

**Alternatives considered**: Adding `*Login Data*` to exclude saved passwords —
rejected; the user intent is a full profile restore, including credentials.

---

### Decision 3: Tag set

**Decision**: Apply both `not-supported-on-vagrant-docker` and
`not-supported-on-vagrant-arm64` as a YAML list on the play's `tags` field.

**Rationale**: `not-supported-on-vagrant-docker` is applied to desktop
application playbooks because Docker-based Vagrant boxes do not include a
desktop environment (kept small and simple). All other desktop app backup/restore
playbooks in this repo carry it; Chrome is a desktop application and requires it.
`not-supported-on-vagrant-arm64` is additionally required because the Google
Chrome apt repository provides only AMD64 packages — Chrome cannot be installed
on ARM64 (confirmed by `configure-linux-roles.yml` where the `google_chrome`
role carries this tag). Backup/restore of a non-existent installation would fail
or be meaningless.

**Alternatives considered**: Applying only `not-supported-on-vagrant-docker` —
rejected; would allow the playbook to run on ARM64 VMs where Chrome is not
installed, causing task failure.

---

### Decision 4: Archive file name

**Decision**: `google-chrome-backup.tar.gz`

**Rationale**: Follows the naming convention of all other application backup
archives in this repo (`chromium-backup.tar.gz`, `cursor-backup.tar.gz`,
`vscode-backup.tar.gz`, etc.).

---

### Decision 5: Restore clean-up path

**Decision**: `delete_before_beneath_home: [".config/google-chrome/Default"]`

**Rationale**: Mirrors the Chromium pattern exactly. Ensures a clean restore by
removing the existing profile directory before extracting the archive. The parent
directory `.config/google-chrome/` is preserved (Chrome may have created other
files there), only `Default` is removed and replaced.

---

### No-change findings

- **Generic task files**: No modifications needed to
  `playbooks/backup/backup.yml` or `playbooks/restore/restore.yml`.
- **No new role**: Backup/restore does not require a role; the existing
  playbook-plus-task-file pattern is correct and sufficient.
- **No new dependencies**: No additions to `requirements.yml` or
  `requirements.txt`.
- **Acceptance test**: Must be performed manually on an AMD64 desktop host.
  No automated test framework is available for GUI browser interactions in
  this project.
