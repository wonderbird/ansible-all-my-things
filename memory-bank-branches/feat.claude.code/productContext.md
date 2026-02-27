# Product Context

The `claude_code` role installs Anthropic's Claude Code CLI on Linux systems. It downloads an installer script from the internet and executes it for each desktop user.

A code review identified that the binary is installed without integrity verification (highest-severity finding). This feature adds post-installation SHA256 checksum verification against Anthropic's official release manifest to detect tampered or corrupted binaries.

Detailed concept and PRD are in `docs/features/claude-code/`. This memory bank is self-contained for implementation purposes.
