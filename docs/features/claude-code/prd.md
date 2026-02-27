# PRD: Claude Code Binary Integrity Verification

## Objective

Verify the SHA256 checksum of the installed Claude Code binary against Anthropic's official release manifest, failing the playbook and removing the binary on mismatch.

## Scope

### In scope

- Determine installed version via `claude --version`
- Fetch the release manifest for that version
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
  Given the Claude Code installer has completed for a user
  When the playbook verifies the binary checksum
  Then it fetches the manifest for the installed version
  And the SHA256 of the local binary matches the manifest
  And the playbook continues without error

Scenario: Checksum mismatch
  Given the Claude Code installer has completed for a user
  When the SHA256 of the local binary does not match the manifest
  Then the binary is deleted from the user's ~/.local/bin/claude
  And the playbook fails with a message containing the expected and actual checksums

Scenario: Manifest unreachable
  Given the Claude Code installer has completed for a user
  When the release manifest cannot be fetched
  Then the playbook fails with a message indicating the manifest URL and HTTP status
```

## Implementation Plan

### Stage 1: Functionality

1. Add default variables to `roles/claude_code/defaults/main.yml`: manifest base URL, architecture-to-platform mapping dict
2. Add task: get installed version via `claude --version` (as each user), register result
3. Add task: fetch manifest JSON using `uri` module with the registered version
4. Add task: compute SHA256 of the binary using `stat` module with `checksum_algorithm: sha256`
5. Add task: extract expected checksum from manifest JSON using the platform mapping
6. Add task in `block`/`rescue`: compare checksums; on mismatch delete binary and `fail` with both checksums
7. Verify the verification tasks only run when the installer actually ran (respect the `creates` guard on the install task)

### Stage 2: Test, Debug, and Safety Checks

1. Run the role on a test VM and confirm the verification passes for a clean install
2. Manually corrupt the binary (e.g. truncate) and re-run; confirm deletion and failure message
3. Simulate an unreachable manifest (e.g. wrong URL) and confirm the failure message includes the URL
4. Verify idempotency: re-run the playbook when Claude Code is already installed and verify it skips installation but still verifies (or skips verification appropriately)
5. Validate architecture mapping on both `x86_64` and `aarch64` targets if available
6. Confirm no secrets or tokens appear in task output or logs
