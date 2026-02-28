# Active Context

## Current state

Implementation is complete and has passed code review. All findings resolved.

Files in final state:

- `roles/claude_code/defaults/main.yml` — `claude_code_manifest_base_url` and `claude_code_platform_map`
- `roles/claude_code/tasks/main.yml` — flat task list: assert architecture → fetch manifest → install → verify checksum → add PATH
- `docs/features/claude-code/concept.md` — updated to reflect final design
- `docs/features/claude-code/prd.md` — updated to reflect final design and implementation steps
- `docs/features/claude-code/acceptance-tests.feature` — Gherkin acceptance tests derived from code review scenarios
- `docs/architecture/technical_debt.md` — created; TD-001 records the accepted risk of unverified `install.sh`

## Immediate next action

Stage 2: test, debug, and safety checks.

1. Run role on a test VM — confirm verification passes on a clean install
2. Truncate binary and re-run — confirm deletion and failure message
3. Set wrong manifest URL — confirm failure before installer runs
4. Re-run on already-installed machine — confirm idempotent behaviour
5. Confirm no secrets appear in task output

## Key decisions made

- Manifest is fetched **before** the installer runs — if the manifest is unreachable the system remains unmodified
- Architecture assertion is the first task — fails fast before any network requests
- Use GitHub Releases API for version discovery (not `claude --version`) — avoids executing an unverified binary
- Flat task structure — no `block`/`rescue`; infrastructure failures surface as raw Ansible errors with clear task names
- `stat` uses `follow: true` — checksum is computed on the target file even if the binary is a symlink
- `when` condition guards `item.stat.checksum` with `not item.stat.exists` — avoids undefined variable error if binary is absent
- PATH is added to `.bashrc` only after successful verification — no PATH entry for a deleted binary
- Manifest base URL and platform mapping in `roles/claude_code/defaults/main.yml`
- On checksum mismatch or absent binary: delete, then `fail` with expected and actual checksums
- musl-based distros are out of scope for now
