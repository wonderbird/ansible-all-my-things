# Concept: Claude Code Binary Integrity Verification

## Feature Name

Post-installation checksum verification for the Claude Code binary.

## Description

Before running the installer, the playbook asserts that the host architecture is supported, fetches the latest release version from the GitHub Releases API, and retrieves the official release manifest from Anthropic's distribution server. Fetching the manifest first ensures that if it is unreachable, the installer never runs and the system remains unmodified. After the installer completes, the playbook computes the SHA256 checksum of the installed binary and compares it against the published checksum for the current platform. If the checksum does not match, the playbook deletes the binary and fails with a clear error message.

## User Value

A compromised or corrupted binary could execute arbitrary code with the user's privileges. By verifying the checksum against the official manifest, this feature detects tampered or corrupted binaries before they are used. This reduces the supply-chain risk of downloading and executing software from the internet, which is the highest-severity finding from the code review.

## Design Rationale

### Never execute the binary before verifying it

Version discovery via `claude --version` was rejected: running the binary before its integrity is
confirmed defeats the purpose of the check. Instead, the playbook queries the GitHub Releases API
to obtain the current version string, fetches the corresponding manifest from Anthropic's
distribution server, and derives the expected SHA256 checksum — all without touching the binary.

### Fail before the installer runs, not after

The release manifest is fetched before `install.sh` is executed. If the manifest is unreachable,
the playbook fails immediately and the system remains unmodified. This avoids a partial state where
an installer has run but integrity verification cannot proceed.

### Flat task list instead of block/rescue

An early implementation used Ansible's `block`/`rescue` structure. This was replaced with a flat
task list. A `rescue` block wraps all failures from its `block` into a single generic error,
obscuring which task actually failed. A flat list surfaces the name of the failing task directly,
making diagnosis faster.

## Out of Scope

- **Verification of the installer script itself** (`install.sh`): the manifest only covers the compiled binary, not the installer. The installer runs unverified.
- **Version pinning**: the role installs the latest version and verifies whatever was installed. Controlling which version gets installed is a separate concern.
- **Code signature verification**: Anthropic signs macOS and Windows binaries, but not Linux binaries. Signature verification is not applicable to the current Linux-only target.
- **musl-based distributions** (e.g. Alpine): the platform mapping covers glibc-based `linux-arm64` and `linux-x64` only. musl support can be added later if needed.
- **Auto-update verification**: Claude Code auto-updates in the background after installation. Verifying binaries after auto-updates is outside the scope of this Ansible role.
