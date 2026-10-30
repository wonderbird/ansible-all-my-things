# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/2.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The desktop profile installs Android Studio and Flutter on AMD64 hosts, and
  Cursor on every desktop host. ARM64 hosts must pass
  `--skip-tags not-supported-on-arm64`.
- The first desktop apply downloads several gigabytes for each login user,
  and every later apply re-downloads the Cursor package.
- Every Linux host gets the Bun runtime, with `bun` and `bunx` on the PATH.
- `claude_code_config` imports the ai-agent-workspace skills into each login
  user's `sm` store, deploying none.
- Every Linux host gets the uv Python manager, with `uv` and `uvx` on the PATH.

### Changed

- `configure-profile.yml` fails at preflight when `login_users` is undefined
  or empty.
- Roles that configure per-user state fail when `login_user_names` is
  undefined or empty.
- `perform-updates.yml` reports every tool that failed, and keeps updating the
  other tools when one upstream source is unavailable.
- `perform-updates.yml` refuses to run with `--check`, naming the reason.
- Tracked tools are declared in `playbooks/update-versions/vars/tools.yml`;
  adding a tool is one entry, and a malformed one fails at play start.
- **Breaking:** The `skill_manager` role disables `sm` skill auto-adopt and
  replaces each login user's `sm` config. Run `sm import` to adopt skills.
- **Breaking:** Only hosts in `claude_opinionated` get the ai-agent-workspace
  clone. Add a host to `claude_opinionated` to keep it.
- **Breaking:** The `nodejs` role installs Node.js 26. Existing hosts upgrade
  only after removing `/usr/local/bin/node` and re-running the role.

### Removed

- `podman` role default `login_user_names: []` — callers must supply at least
  one user name.
- `query-versions.yml`. Run `perform-updates.yml` and read `git diff`: it
  reports the same drift, having already applied it.
- **Breaking:** `claude_code_config` links no ai-agent-workspace skill into
  `~/.claude/skills`. Unlink existing ones: `find ~/.claude/skills -maxdepth 1
  -lname '*/ai-agent-workspace/skills/*' -delete`.
- **Breaking:** The `nodejs` role links no `corepack` command. Install it with
  `npm install --global corepack`.

### Fixed

- `perform-updates.yml` fails, naming the file and pin, when a pin is missing
  or duplicated.
- `perform-updates.yml` fails, naming the repository and tag, when a tool's
  latest GitHub release lacks the asset that tool installs.
- `perform-updates.yml` fails, naming the tool, when a tool's fetch leaves the
  value an earlier tool fetched.
- The `rtk`, `beads_go`, `beads_rust` and `beads_viewer` roles upgrade an
  installed binary to the pinned version.

[Unreleased]: https://github.com/wonderbird/ansible-all-my-things/commits/main
