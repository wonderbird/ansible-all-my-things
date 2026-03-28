# Feature Specification: Backup Google Chrome Browser Configuration

**Feature Branch**: `002-backup-chrome-config`
**Created**: 2026-03-24
**Status**: Draft
**Input**: User description: "I wish to backup my google chrome browser configuration the same way I backup the configuration of the chromium browser"

## Clarifications

### Session 2026-03-24

- Q: What is the priority framing for this feature? → A: Not a core feature, but important for a convenient user experience.
- Q: What is the required end-to-end test procedure? → A: Configure browser to show home button (at least), backup, verify archive exists, remove configuration from target host, verify home button is no longer visible (profile absent), close browser, remove configuration again, restore configuration from backup, verify home button is visible (and any other configured changes). Note: Chrome does not show a first-run dialog when Default/ is absent — home button visibility is the reliable indicator.
- Q: Are there additional Ansible tags beyond `not-supported-on-vagrant-docker`? → A: Yes — `not-supported-on-vagrant-arm64` also applies (see configure-linux-roles.yml).
- Q: Are the assumptions about config directory, single desktop user, and reuse of generic task files confirmed? → A: All three confirmed.

### Session 2026-03-28

- Q: Should a new FR be added that fully specifies the missing-profile graceful-skip behavior (stat check + operator-visible debug message + skip tasks, no error raised)? → A: Yes — add FR-009.
- Q: Should an acceptance scenario be added to US1 for the missing-profile case? → A: Yes — add scenario 4; profile directory may be absent whether or not Chrome is installed.
- Q: Does the restore side's missing-archive edge case need a new FR, or is the generic restore task's existing behavior sufficient? → A: Defer to implementation — generic restore task governs; no new FR needed.
- Q: Does Chrome show its first-run configuration dialog when `~/.config/google-chrome/Default` is absent? → A: No — observed during E2E testing on hobbiton (2026-03-28). Chrome tracks first-run state outside of `Default/` (e.g. in `~/.config/google-chrome/Local State` or a `First Run` sentinel file). The home button visibility is the reliable indicator of whether the profile is absent or restored.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Back Up Google Chrome Settings (Priority: P1)

As a desktop user, when I run the backup playbook, my Google Chrome browser configuration is archived and stored alongside other application backups (e.g., Chromium), so that I can recover my browser profile if my system is lost or reinstalled.

**Why this priority**: Backup must exist before restore can work. Within this feature, it is the prerequisite step. The feature itself is not a core system capability but is important for a convenient user experience — restoring a familiar browser profile saves significant manual reconfiguration effort.

**Independent Test**: Can be fully tested by configuring the browser to show the home button, running the main backup playbook, and verifying a `google-chrome-backup.tar.gz` archive is created at the backup destination.

**Acceptance Scenarios**:

1. **Given** the desktop user has configured Google Chrome to show the home button, **When** the backup playbook runs, **Then** a compressed archive `google-chrome-backup.tar.gz` is created at the backup destination.
2. **Given** the backup playbook has run, **When** the resulting archive is inspected, **Then** it does not contain cache files, history, local/session/shared/web storage, blob storage, or favicons.
3. **Given** the backup playbook runs, **When** it completes successfully, **Then** the Google Chrome backup is performed as part of the same backup run that backs up Chromium and other applications.
4. **Given** `~/.config/google-chrome/Default` does not exist on the host (whether or not Chrome is installed), **When** the backup playbook runs, **Then** no error is raised, an operator-visible debug message is emitted indicating the profile directory is absent, and no archive is created.

---

### User Story 2 - Restore Google Chrome Settings (Priority: P2)

As a desktop user, when I run the restore playbook on a machine where the Chrome profile has been removed, my Google Chrome browser configuration is restored from the backup archive, so that I have the same browser profile as before without needing to reconfigure it manually.

**Why this priority**: Restore is the purpose of backup. Without a working restore path, the backup delivers no user value. Restoring the profile means the user finds their prior settings intact (e.g., the home button is visible) without needing to reconfigure Chrome from scratch.

**Independent Test**: Can be tested by removing the Chrome configuration directory, running the restore playbook, and verifying that previously configured settings (e.g., home button visibility) are present after launch.

**Acceptance Scenarios**:

1. **Given** a `google-chrome-backup.tar.gz` archive exists at the backup source and the Chrome configuration directory has been removed from the host, **When** the restore playbook runs, **Then** the archive contents are extracted to `~/.config/google-chrome/Default` for the primary desktop user.
2. **Given** a restore is triggered, **When** the restore playbook runs, **Then** any pre-existing Google Chrome configuration directory is removed before extracting the archive, ensuring a clean state.
3. **Given** the restore playbook runs, **When** it completes, **Then** the Google Chrome restore is performed as part of the same restore run that restores Chromium and other applications.

---

### User Story 3 - End-to-End Backup and Restore Verification (Priority: P3)

As a desktop user, I can verify that the full backup-and-restore cycle preserves my Google Chrome configuration faithfully, so that I have confidence the backup is valid and the restore produces a working browser profile identical to the original.

**Why this priority**: The individual backup and restore stories are independently valuable, but this story validates that the two work together correctly and that the restored profile actually matches the original — not just that files are copied.

**Independent Test**: Verified by executing the complete test sequence: configure Chrome settings (e.g., enable home button), backup, remove config, confirm Chrome settings are absent (e.g., home button not visible), close Chrome, remove config again, restore, confirm settings are preserved (e.g., home button visible).

**Acceptance Scenarios**:

1. **Given** Google Chrome has been configured with at least the home button enabled, **When** the backup playbook runs, **Then** a `google-chrome-backup.tar.gz` archive is present at the backup destination.
2. **Given** the backup archive exists and the Chrome configuration directory is removed from the host, **When** Google Chrome is launched, **Then** Chrome does not have the previously configured settings (e.g., the home button is not visible), confirming the profile is absent. Note: Chrome does not show a first-run dialog in this state; first-run state is tracked outside `Default/`.
3. **Given** Chrome has been closed after profile removal (which may have recreated `Default/` with fresh defaults), **When** the Chrome configuration directory is removed again and the restore playbook runs, **Then** the restore playbook completes successfully.
4. **Given** the restore has completed, **When** Google Chrome is launched, **Then** the home button is visible (and any other settings configured before the backup are present), confirming the restored profile matches the original.

---

### Edge Cases

- What happens when `~/.config/google-chrome/Default` does not exist (whether or not Chrome is installed)? See FR-009: the backup playbook checks for directory existence with `stat`, emits an operator-visible `debug` message when absent, and skips all backup tasks without raising an error.
- What happens if the archive is missing during restore? The behavior is governed by the existing generic `playbooks/restore/restore.yml` task file, which is reused as-is (see Assumptions). No additional FR is required.
- After Chrome recreates default config files on launch (which occurs even without a first-run dialog), those files must be removed before the restore is run to prevent a dirty restore state (covered in User Story 3, scenario 3).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The backup playbook MUST archive the Google Chrome configuration directory (`~/.config/google-chrome/Default`) for the primary desktop user, producing a `google-chrome-backup.tar.gz` file at the backup destination.
- **FR-002**: The backup MUST exclude ephemeral and cache data from the archive, using the same exclusion categories as the Chromium backup: cache, history, local/session/shared/web storage, blob storage, and favicons.
- **FR-003**: The restore playbook MUST extract the `google-chrome-backup.tar.gz` archive to `~/.config/google-chrome/Default` for the primary desktop user.
- **FR-004**: The restore MUST remove any pre-existing Google Chrome configuration directory before extracting the archive, ensuring a clean restore.
- **FR-005**: The Google Chrome backup playbook MUST be imported into the main `backup.yml` orchestration file, alongside the Chromium backup.
- **FR-006**: The Google Chrome restore playbook MUST be imported into the main `restore.yml` orchestration file, alongside the Chromium restore.
- **FR-007**: Both the backup and restore playbooks MUST carry both the `not-supported-on-vagrant-docker` and `not-supported-on-vagrant-arm64` tags.
- **FR-008**: The backup playbook MUST operate on the `backup_from_host` host group; the restore playbook MUST operate on the `linux` host group — consistent with the Chromium pattern.
- **FR-009**: When the backup playbook runs and `~/.config/google-chrome/Default` does not exist on the target host, the playbook MUST use `stat` to check for the directory's existence, emit an operator-visible `debug` message indicating the profile is absent, and skip all backup tasks without raising an error.

### Key Entities

- **Google Chrome configuration directory**: The user-specific directory on the host system where Google Chrome stores its profile data (extensions, bookmarks, preferences, etc.). Located at `~/.config/google-chrome/Default`.
- **Backup archive**: A compressed tar archive (`google-chrome-backup.tar.gz`) stored at the backup destination, containing the non-ephemeral contents of the Chrome configuration directory.
- **Desktop user**: The primary desktop user whose Chrome profile is backed up and restored, identified via `desktop_users[0].name`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the main backup playbook produces a `google-chrome-backup.tar.gz` archive that does not contain any cache or ephemeral data.
- **SC-002**: After a complete backup-remove-restore cycle, Google Chrome launches with previously configured settings present (e.g., the home button is visible), confirming the profile was faithfully restored.
- **SC-003**: After restore, Google Chrome displays the home button (and any other settings that were configured before the backup), confirming no configuration loss.
- **SC-004**: The Google Chrome backup and restore are integrated into the existing orchestration so that a single run of `backup.yml` or `restore.yml` covers both Chromium and Google Chrome without additional manual steps.
- **SC-005**: The Google Chrome backup and restore playbooks follow the same structure and conventions as the existing Chromium equivalents, including identical tagging (`not-supported-on-vagrant-docker`, `not-supported-on-vagrant-arm64`), variable naming, and task delegation patterns.

## Assumptions

- Google Chrome on the target system stores its profile at `~/.config/google-chrome/Default` (standard Linux installation path, not a snap package). **Confirmed.**
- The same exclusion patterns used for Chromium (cache, history, storage types, favicons) are appropriate for Google Chrome, since both are Chromium-based browsers with identical profile structures.
- Only the primary desktop user (`desktop_users[0].name`) has a Chrome profile to back up. **Confirmed.**
- The generic `backup.yml` and `restore.yml` task files in `playbooks/backup/` and `playbooks/restore/` are reused as-is, with only the path and filename variables changing. **Confirmed.**
