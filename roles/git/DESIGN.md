<!-- SPDX-License-Identifier: MIT-0 -->

# git role — Design Notes

## No pinned version

The role installs the `git` apt package unpinned (`state: present`),
mirroring the `vim`/`ruby` precedent. A pinned version was considered and
rejected: apt version strings for distro packages are architecture- and
release-specific, making a pin brittle across the amd64/arm64 targets this
repository provisions. The version-update-playbook mechanism under
`playbooks/update-versions/` targets tools pinned via `defaults/main.yml`
fetched from upstream releases (e.g. GitHub); it does not apply here
because no version is pinned. No requirement drives a reproducible git
version, so YAGNI (Principle IV) favors the unpinned apt-latest install.

## Why a dedicated role instead of per-role installs

Before this role existed, `git` was installed ad hoc inside every role
that needed it (`ai_agent_workspace`, `beads_go`, `beads_rust`,
`claude_code`, `skill_manager`, `specify_cli`, `tmux`), each repeating the
same one-line apt task — a Principle XI (DRY) violation flagged during the
PR #108 review (tracked as beads issue `ansible-all-my-things-ojz6`).

Extracting a dedicated `git` role and having each consumer declare it as a
`meta/main.yml` dependency (the same pattern `skill_manager` uses for
`nodejs`) removes the duplication while keeping each role single-purpose
(Principle II). The rejected alternative — a `developer_tools` grab-bag
role bundling several CLI utilities — was ruled out: it conflicts with
this repository's one-tool-one-role convention and would be harder to
test and version independently per tool.

See `docs/architecture/concepts/role-dependency-declaration.md` for the
general decision test this role's consumers apply, and each consumer
role's own `meta/main.yml` for its declared dependency on `git`.
