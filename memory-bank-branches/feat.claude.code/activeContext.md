# Active Context

## Current state

Binary checksum verification (Stage 1) has been implemented. All code review findings are resolved.

Committed as `2ca5349`. Files changed:
- `roles/claude_code/defaults/main.yml` — created with `claude_code_manifest_base_url` and `claude_code_platform_map`
- `roles/claude_code/tasks/main.yml` — verification block added after install task; `creates` guard removed so installer always runs; version and expected checksum each extracted into a dedicated `set_fact` task for readability

Feature concept and PRD are written and approved:
- `docs/features/claude-code/concept.md`
- `docs/features/claude-code/prd.md`

## Immediate next action

Stage 2: test, debug, and safety checks.

1. Run role on a test VM — confirm verification passes on a clean install
2. Truncate binary and re-run — confirm deletion and failure message
3. Set wrong manifest URL — confirm failure message includes URL
4. Re-run on already-installed machine — confirm installer and verification both run cleanly
5. Confirm no secrets appear in task output

## Key decisions made

- Verify post-installation (not pre-installation) — the manifest covers the binary, not the installer script
- Use GitHub Releases API for version discovery (not `claude --version`) — avoids executing an unverified binary; the GitHub release is Anthropic's public, documented release contract
- Manifest base URL and platform mapping go into `roles/claude_code/defaults/main.yml`
- Variable names: `claude_code_manifest_base_url`, `claude_code_platform_map`
- On checksum mismatch: delete binary, then fail with both expected and actual checksums
- musl-based distros are out of scope for now
