# Active Context — feat.podman.role

## Current Work Focus

Branch `006-podman-rootless-role` — Podman role complete; Molecule test
scaffold for the `java` role implemented and committed. T023 (running
`molecule test`) is the remaining acceptance step.

## Recent Decisions (This Session)

- **Rootless Podman chosen** over rootful: no systemd-in-container needed
  for the `.devcontainer` use case
- **`test/docker/Dockerfile` dropped from scope**: requires privileged /
  rootful mode — not needed for the AI agent sandbox goal
- **`lineinfile` chosen** for subuid/subgid: `ansible.builtin.user` has no
  subuid support in any released Ansible version; `usermod --add-subuids`
  is non-idempotent
- **No docker shim**: caller uses `podman build` / `podman run` directly
- **`desktop_user_names: []`** added as default in `defaults/main.yml` to
  prevent unhelpful "undefined variable" errors
- **DESIGN.md Decision 4** added: documents the shared-start-value trade-off
  for multi-user servers
- **Molecule test added to `java` role** (T017–T022 complete): this is the
  primary acceptance criterion that proves Podman is working. Uses
  `molecule-plugins[podman]`, `ubuntu:24.04`, `testuser`, and verifies
  `java -version` output contains "Temurin"
- **`zip`, `unzip`, `curl` prerequisite task** added as first task in
  `roles/java/tasks/main.yml` (sdkman installer requires these)
- **SC-005 replaced**: manual Vagrant run replaced by `molecule test` as
  the authoritative acceptance criterion for the java role

## Next Steps

1. **Run `molecule test`** inside `roles/java/` (T023 — Phase 4 acceptance)
2. **Create PR** to merge `006-podman-rootless-role` into `main`

## Active Decisions and Considerations

- The `# syntax=docker/dockerfile:1` BuildKit directive in
  `.devcontainer/Dockerfile` is silently ignored by Podman — no workaround
  needed
- All image references are fully qualified (`docker.io/python:trixie`) —
  no `registries.conf` configuration required
- `podman system migrate` runs unconditionally with `changed_when: false`
  (see systemPatterns.md D3 for rationale)
- **Build context must be `.devcontainer/`**: all `COPY` source files
  (`awscliv2-public-key.asc`, `install-aws-cli.sh`, etc.) reside inside
  `.devcontainer/`, not the repo root. Correct command:
  `podman build -t devcontainer .devcontainer/`
- **Molecule prepare.yml** uses `ansible.builtin.raw` (container has no
  Python before prepare runs); `become: true` at play level is required
- **verify.yml PATH**: uses
  `/home/testuser/.sdkman/candidates/java/current/bin:{{ ansible_env.PATH | default(...) }}`
  to reach the `java` binary

## Open Questions / Blockers

None.

## Patterns and Preferences Learned

- Always run `format-markdown` on any `.md` file after editing (constitution
  Principle VI + rule 400)
- The `(feature-name)` annotation style in `CLAUDE.md` was rejected — use
  clean, feature-agnostic bullets in `## Active Technologies`
- `## Recent Changes` sections in `CLAUDE.md` are forbidden (rule
  330-git-usage.mdc — git history is authoritative)
- The `speckit.analyze` step surfaces variable-name drift between
  `research.md` and `tasks.md` / `data-model.md` — always run it and fix
  inconsistencies before implementing
- **`become_user` without task-level `become: true`** is correct in this
  project: play-level `become: true` is inherited; task-level `become_user`
  only overrides the target user — do NOT add task-level `become: true` to
  role tasks (FR-010)
