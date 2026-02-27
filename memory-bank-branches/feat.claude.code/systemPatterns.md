# System Patterns

## Role structure

Each software installation has a dedicated Ansible role under `roles/`. Roles are applied to host groups via playbooks. The `claude_code` role is applied via `configure-linux-roles.yml` alongside `cursor_ide`.

## Key files for this feature

- `roles/claude_code/tasks/main.yml` — installation and verification tasks
- `roles/claude_code/defaults/main.yml` — to be created; holds manifest URL base and platform mapping
- `roles/claude_code/meta/main.yml` — role metadata
- `configure-linux-roles.yml` — playbook applying Linux roles

## Verification flow

1. Installer runs (existing) → creates `/home/{user}/.local/bin/claude`
2. Get installed version via `claude --version` (per user)
3. Fetch manifest JSON from `{manifest_base_url}/{version}/manifest.json`
4. Compute SHA256 of local binary via `stat` module
5. Compare checksums; on mismatch → delete binary → `fail`

Architecture mapping and manifest details are in `techContext.md`.

## Conventions

- `blockinfile` markers must be role-specific (e.g., `# {mark} ANSIBLE MANAGED BLOCK - Claude Code PATH`)
- `meta/main.yml` description field describes the role, not the author
- All tasks use `become_user: "{{ item }}"` with `loop: "{{ desktop_user_names }}"`
