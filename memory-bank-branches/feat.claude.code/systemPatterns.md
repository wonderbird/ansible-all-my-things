# System Patterns

## Role structure

Each software installation has a dedicated Ansible role under `roles/`. Roles are applied to host groups via playbooks. The `claude_code` role is applied via `configure-linux-roles.yml` alongside `cursor_ide`.

## Key files for this feature

- `roles/claude_code/tasks/main.yml` — installation and verification tasks
- `roles/claude_code/defaults/main.yml` — manifest URL base and platform mapping
- `roles/claude_code/meta/main.yml` — role metadata
- `configure-linux-roles.yml` — playbook applying Linux roles

## Verification flow

1. `assert` → verify `ansible_architecture` is in `claude_code_platform_map`
2. `uri` → GitHub Releases API → `set_fact: claude_code_version` (tag stripped of leading `v`)
3. `uri` → fetch `{manifest_base_url}/{claude_code_version}/manifest.json`
4. `set_fact: claude_code_expected_checksum` from `manifest.json.platforms[platform].checksum`
5. Installer runs unconditionally (no `creates` guard) → produces `/home/{user}/.local/bin/claude`
6. `stat` with `follow: true` → SHA256 of each user's binary
7. On `not item.stat.exists` or mismatch → delete binary → `fail` with both checksums
8. `PATH` is added to `.bashrc` only after successful verification

Architecture mapping and manifest details are in `techContext.md`.

## Conventions

- `blockinfile` markers must be role-specific (e.g., `# {mark} ANSIBLE MANAGED BLOCK - Claude Code PATH`)
- `meta/main.yml` description field describes the role, not the author
- All tasks use `become_user: "{{ item }}"` with `loop: "{{ desktop_user_names }}"`
