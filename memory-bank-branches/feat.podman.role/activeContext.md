# Active Context — feat.podman.role

## Current Work Focus

Branch `006-podman-rootless-role` — all implementation and testing complete.
Next action: create PR to merge into `main`.

## Recent Decisions (This Session)

- **T023 complete**: `molecule test` passes for `roles/java/` — all phases
  green (prepare, converge, idempotence, verify, destroy)
- **Molecule fixes applied** to make tests runnable:
  - `meta/main.yml`: added `namespace: wonderbird`, `role_name: java`
  - `molecule.yml`: added `ANSIBLE_ROLES_PATH: "${MOLECULE_PROJECT_DIRECTORY}/../"`
  - `prepare.yml`: split `&&`-chained `raw` into two separate tasks; added
    `become: false` to both (sudo not yet installed during bootstrap)
  - `tasks/main.yml`: removed unconditional "Remove sdkman installer" task
    (deleted the file → re-downloaded on idempotence run → not idempotent)
- **Molecule warnings resolved**:
  - `molecule.yml`: explicit `test_sequence` omitting unused phases
  - `verify.yml`: `ansible_env.PATH` → `ansible_facts['env']['PATH']`
- **Constitution amended** to v1.2.0: Principles II and III updated to
  require `molecule test` for containerizable roles; Vagrant retained as
  fallback for full-VM roles
- **Rule 340-molecule-testing.mdc** created in `.cursor/rules/` and
  registered in `CLAUDE.md` rule index

## Next Steps

1. **Create PR** to merge `006-podman-rootless-role` into `main`

## Active Decisions and Considerations

- `podman system migrate` runs unconditionally with `changed_when: false`
  (see systemPatterns.md D3)
- Build context must be `.devcontainer/` — not `.`
- `&&` in YAML `>` folded scalars is unreliable with the Podman connection
  plugin — always use separate `raw` tasks for bootstrap steps
- `apt-get -qq update` (flag before subcommand) works; `apt-get update -qq`
  fails in Ubuntu 24.04 apt 2.7.x ("The update command takes no arguments")
- `ansible_facts['env']['PATH']` is the correct form; `ansible_env` removed
  in 2.24

## Patterns and Preferences Learned

- Always run `format-markdown` on any `.md` file after editing
- `## Recent Changes` sections in `CLAUDE.md` are forbidden — git history
  is authoritative
- `speckit.analyze` surfaces variable-name drift — run before implementing
- **`become_user` without task-level `become: true`** is correct: play-level
  `become: true` is inherited
- The sync impact report HTML comment in constitution.md is required by
  `speckit.constitution` but can be deleted after review (per project owner)
- **Molecule subagents** for format-markdown lack Bash access by default —
  run markdownlint directly in the main session instead
