# Active Context — feat.podman.role

## Current Work Focus

Branch `006-podman-rootless-role` — implementation complete, code review
complete, acceptance testing in progress (Phase 4 of the SDD workflow).

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

1. **Run acceptance test T020** against the local VM (the only remaining
   open task):
   - SC-001: `podman --version` → version string
   - SC-002: `podman build -t devcontainer -f .devcontainer/Dockerfile .`
     → succeeds
   - SC-003: `podman run --rm devcontainer ansible --version` → version
     string
   - SC-004: re-run role → zero `changed` tasks
2. **Check T020** in `specs/006-podman-rootless-role/tasks.md`
3. **Commit** all changes on branch `006-podman-rootless-role`
4. **Create PR** to merge into `main`

## Active Decisions and Considerations

- The `# syntax=docker/dockerfile:1` BuildKit directive in
  `.devcontainer/Dockerfile` is silently ignored by Podman — no workaround
  needed
- All image references are fully qualified (`docker.io/python:trixie`) —
  no `registries.conf` configuration required
- `podman system migrate` runs unconditionally with `changed_when: false`
  (see systemPatterns.md D3 for rationale)

## Open Questions / Blockers

None. The only open item is the human-run acceptance test (T020).

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
