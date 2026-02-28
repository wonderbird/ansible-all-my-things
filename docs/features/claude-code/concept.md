# Concept: Claude Code Binary Integrity Verification

## Feature Name

Post-installation checksum verification for the Claude Code binary.

## Description

Before running the installer, the playbook asserts that the host architecture is supported, fetches the latest release version from the GitHub Releases API, and retrieves the official release manifest from Anthropic's distribution server. Fetching the manifest first ensures that if it is unreachable, the installer never runs and the system remains unmodified. After the installer completes, the playbook computes the SHA256 checksum of the installed binary and compares it against the published checksum for the current platform. If the checksum does not match, the playbook deletes the binary and fails with a clear error message.

## User Value

A compromised or corrupted binary could execute arbitrary code with the user's privileges. By verifying the checksum against the official manifest, this feature detects tampered or corrupted binaries before they are used. This reduces the supply-chain risk of downloading and executing software from the internet, which is the highest-severity finding from the code review.

## Out of Scope

- **Verification of the installer script itself** (`install.sh`): the manifest only covers the compiled binary, not the installer. The installer runs unverified.
- **Version pinning**: the role installs the latest version and verifies whatever was installed. Controlling which version gets installed is a separate concern.
- **Code signature verification**: Anthropic signs macOS and Windows binaries, but not Linux binaries. Signature verification is not applicable to the current Linux-only target.
- **musl-based distributions** (e.g. Alpine): the platform mapping covers glibc-based `linux-arm64` and `linux-x64` only. musl support can be added later if needed.
- **Auto-update verification**: Claude Code auto-updates in the background after installation. Verifying binaries after auto-updates is outside the scope of this Ansible role.
