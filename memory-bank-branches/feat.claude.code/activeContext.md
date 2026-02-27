# Active Context

## Current state

The `claude_code` role exists and installs Claude Code without integrity verification. A code review has been completed. Findings 2–4 are resolved. Finding 1 (HIGH: no checksum verification) is the remaining work item.

Feature concept and PRD are written and approved:
- `docs/features/claude-code/concept.md`
- `docs/features/claude-code/prd.md`

## Immediate next action

Implement binary checksum verification. Concrete steps:

1. Create `roles/claude_code/defaults/main.yml` with variables `claude_code_manifest_base_url` and `claude_code_platform_map`
2. Add task: run `claude --version` per user, register result, parse version from stdout
3. Add task: fetch manifest JSON via `uri` module using the parsed version
4. Add task: compute SHA256 of `/home/{{ item }}/.local/bin/claude` via `stat` module
5. Add task: extract expected checksum from manifest JSON using platform mapping
6. Add `block`/`rescue`: compare checksums; on mismatch delete binary and `fail` with both checksums
7. Ensure verification tasks only run when the installer actually ran (chain off the install task's `changed` state)

## Key decisions made

- Verify post-installation (not pre-installation) — the manifest covers the binary, not the installer script
- Use `claude --version` for dynamic version discovery — no version pinning
- Manifest base URL and platform mapping go into `roles/claude_code/defaults/main.yml`
- Variable names: `claude_code_manifest_base_url`, `claude_code_platform_map`
- On checksum mismatch: delete binary, then fail with both expected and actual checksums
- musl-based distros are out of scope for now
