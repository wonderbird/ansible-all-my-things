# PRD: Claude Code Binary Integrity Verification

## Objective

Verify the SHA256 checksum of the installed Claude Code binary against Anthropic's official release manifest, failing the playbook and removing the binary on mismatch.

## Scope

### In scope

- Assert that the host architecture is in the platform map before any network requests
- Determine the latest released version via the GitHub Releases API before running the installer
- Fetch the release manifest for that version before running the installer
- Map `ansible_architecture` to manifest platform keys (`linux-arm64`, `linux-x64`)
- Compare SHA256 checksums; on mismatch delete the binary and fail
- Extract the manifest base URL into a role variable for maintainability

### Out of scope

- Installer script verification, version pinning, code signature verification, musl distros, auto-update verification (see concept.md)

## User Stories

1. As a system administrator, I want the playbook to verify the Claude Code binary after installation, so that I can trust it has not been tampered with or corrupted.
2. As a system administrator, I want a clear error message and automatic removal of the binary when verification fails, so that no compromised binary remains on the system.
3. As a role maintainer, I want the manifest URL base and platform mapping defined as variables, so that I can adapt them without modifying task logic.

## Acceptance Criteria

```gherkin
Scenario: Successful verification
  Given the host architecture is supported
  And the manifest is reachable
  And the Claude Code installer completes for a user
  When the playbook verifies the binary checksum
  Then the SHA256 of the local binary matches the manifest
  And the playbook continues without error

Scenario: Checksum mismatch
  Given the manifest has been fetched successfully
  And the Claude Code installer has completed for a user
  When the SHA256 of the local binary does not match the manifest
  Then the binary is deleted from the user's ~/.local/bin/claude
  And the playbook fails with a message containing the expected and actual checksums

Scenario: Manifest unreachable
  Given the host architecture is supported
  When the release manifest cannot be fetched
  Then the playbook fails before running the installer
  And the system remains unmodified

Scenario: Unsupported architecture
  Given the host architecture is not in the platform map
  When the role is applied
  Then the playbook fails immediately before any network requests
  And the failure message lists the supported architectures
```

## Implementation Plan

### Stage 1: Functionality

1. Add default variables to `roles/claude_code/defaults/main.yml`: manifest base URL, architecture-to-platform mapping dict
2. Add task: assert that `ansible_architecture` is in the platform map
3. Add task: fetch latest version from GitHub Releases API; extract version number via `regex_replace`
4. Add task: fetch manifest JSON using `uri` module with the resolved version
5. Add task: extract expected checksum from manifest JSON using the platform mapping
6. Run installer unconditionally for each user (no `creates` guard)
7. Add task: compute SHA256 of the binary using `stat` module with `checksum_algorithm: sha256` and `follow: true`
8. Add task: on mismatch or missing binary (`not item.stat.exists`), delete binary and `fail` with both checksums
9. Add claude to PATH only after successful verification

### Stage 2: Test, Debug, and Safety Checks

1. Run the role on a test VM and confirm the verification passes for a clean install
2. Manually corrupt the binary (e.g. truncate) and re-run; confirm deletion and failure message
3. Simulate an unreachable manifest (e.g. wrong URL) and confirm the failure message includes the URL
4. Verify idempotency: re-run the playbook when Claude Code is already installed and verify it skips installation but still verifies (or skips verification appropriately)
5. Validate architecture mapping on both `x86_64` and `aarch64` targets if available
6. Confirm no secrets or tokens appear in task output or logs

All Stage 2 steps were executed on 2026-02-28 and passed.
