# Findings

## F1: Split claude_code tasks file

**File:** `roles/claude_code/tasks/main.yml`

**Finding:** Tasks span five distinct concerns and should be split like `roles/tmux/tasks/`.

**Proposed split:**
- `install-deps.yml` — jq and prerequisites
- `install-claude-code.yml` — platform check, checksums, per-user install, integrity verification
- `install-addons.yml` — beads, omc CLI, plugins, omc repo clone
- `configure.yml` — per-user config, agent team windows
- `main.yml` — orchestration only (`include_tasks:` calls in order)
