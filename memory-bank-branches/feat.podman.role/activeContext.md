# Active Context — feat.podman.role

## Current Work Focus

Branch `006-podman-rootless-role` — all phases complete, including
acceptance testing. Ready to commit and open PR.

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

## Next Steps

1. **Commit** all changes on branch `006-podman-rootless-role`
2. **Create PR** to merge into `main`

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
