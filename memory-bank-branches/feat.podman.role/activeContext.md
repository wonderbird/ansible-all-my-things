# Active Context — feat.podman.role

## Current Work Focus

Branch `006-podman-rootless-role` — implementation complete. A technical code
review was performed (2026-04-12) and produced findings that must be addressed
before creating the PR.

Findings are saved in `REVIEW-FINDINGS.md` at the project root.

## Next Steps

Address review findings in order of severity, then create the PR:

1. **M1** — Document Molecule exemption for `roles/podman/` in `DESIGN.md`
   (podman-in-podman problem; `apt` + `lineinfile` tasks could be partially
   tested but `podman system migrate` requires privileged mode not available
   in the driver). Alternatively, add a partial Molecule scenario that covers
   the `apt` and `lineinfile` tasks with the `migrate` task skipped via a
   variable guard.
2. **M2** — Align `prepare.yml` with rule 340 template: remove `-qq` from
   `apt-get update -qq` in `roles/java/molecule/default/prepare.yml`.
3. **L1** — Add `namespace: wonderbird` and `role_name: podman` to
   `roles/podman/meta/main.yml`.
4. **L2** — In `roles/java/tasks/main.yml`, register the sdkman install task
   result and delete `/tmp/sdkman-install.sh` conditionally
   (`when: install_result is changed`).
5. **I1** — Add `update_cache: false` to the podman `apt` task in
   `roles/podman/tasks/main.yml`.
6. **I2** — Add inline comment to the two `raw` tasks in
   `roles/java/molecule/default/prepare.yml` explaining `become: false`.
7. **Create PR** to merge `006-podman-rootless-role` into `main`.

## Review Findings Summary (2026-04-12)

Source: `REVIEW-FINDINGS.md`

- **M1**: No Molecule scenario for `roles/podman/`; exemption not documented
- **M2**: `prepare.yml` uses `apt-get update -qq`; rule 340 template shows
  `apt-get update` (no flags) — divergence creates a copy-paste trap
- **L1**: `podman/meta/main.yml` missing `namespace` and `role_name` (required
  for Molecule prerun, as learned from java role fix)
- **L2**: SDKMAN installer `/tmp/sdkman-install.sh` left on disk indefinitely
  (cleanup task removed to fix idempotence but no conditional replacement added)
- **I1**: `update_cache` not explicit in podman apt task
- **I2**: Play-level `become` interplay in `prepare.yml` lacks an explanatory comment

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
