<!-- SPDX-License-Identifier: MIT-0 -->
# skill_manager — Design

Non-obvious decisions for the `skill_manager` role.

## Why Build From Source

Skill Manager publishes no release tarballs or prebuilt binaries — the
documented install is a source build (`git clone` → `npm install` →
`npm run build` → `npm link`). The role mirrors that build but installs
system-wide instead of via `npm link` (which only registers the command for
the user that ran it, not for every login user on a shared host).

## Integrity Model

The trust chain is HTTPS to `github.com` plus a locally pinned full commit SHA
in `defaults/main.yml`. Pinning a commit SHA — not a branch name or a tag —
means the exact tree is fixed: a re-clone always resolves to the same content,
and upstream force-pushes or new commits cannot silently change what is built.

## Runtime node_modules Are Retained

The build (`tsup`, ESM, `platform: node`) externalises runtime dependencies
rather than bundling them, so `dist/bin/sm.js` imports bare specifiers (e.g.
`commander`) that must resolve against a sibling `node_modules`. The role
therefore keeps `node_modules` beside `dist/` under
`skill_manager_install_dir`, running `npm prune --omit=dev` after the build to
drop build-only dependencies (`tsup` and friends) while keeping the runtime
set. The `sm` symlink points at `dist/bin/sm.js`, whose tsup-injected
`#!/usr/bin/env node` shebang makes it directly executable.

## Idempotency

The pinned commit SHA is written to `.git_sha` inside the install directory
after a successful build. On re-run the role reads that marker and derives a
single `_skill_manager_needs_install` fact; the expensive block (remove, clone,
`npm ci`, build, prune) is skipped entirely when the marker already matches the
pinned SHA. `sm --version` cannot be used as the idempotency signal because it
reports the package.json version (e.g. `1.0.2`), which does not change between
commits on the same release line. Molecule's `idempotence` phase enforces the
no-op re-run.

## Dependency on nodejs

`npm ci` and `npm run build` hard-fail without node and npm, which only the
`nodejs` role provisions on target hosts. Per
`docs/architecture/concepts/role-dependency-declaration.md` this is a genuine
hard runtime dependency, so it is declared in `meta/main.yml` `dependencies:`
— in addition to explicit ordering in the base playbook and the Molecule
`converge.yml`.

## Auto-Adopt Is Disabled Per User

By default `sm` runs an auto-adopt scan before almost every command: it moves
each unmanaged skill it finds under the user's tool directories and under the
current directory's `.claude/` or `.agents/` into its own store, then replaces
the original with a symlink. Running `sm` inside a checkout that holds skills
would therefore rewrite that checkout. The role deploys
`~/.skill-manager/config.toml` with `autoAdopt = false` for every login user so
`sm` only touches skills it is told to manage.

`sm` reads the config from the invoking user's home, so the setting is a
per-user file rather than a system-wide one, owned by that user because `sm`
writes its store and state into the same directory.

The role owns the whole file (`ansible.builtin.copy`) instead of only the
`autoAdopt` key (`community.general.ini_file`). No other key is set by hand on
provisioned hosts, and owning the file keeps the result fully determined by the
role. Some `sm` entry points treat a config they cannot parse as auto-adopt
enabled, so a deterministic file is also the safer one.

## Version-Update Integration

The role registers with the project-wide version-update mechanism, but unlike
release-tag tools it tracks a commit SHA:

- `tasks/fetch-github-commit-sha.yml` queries the GitHub API for the HEAD
  commit of the upstream default branch (`master`).
- `perform-updates.yml` writes the new HEAD SHA back into `defaults/main.yml`.
  There is no checksum to recompute — the commit SHA is itself the integrity
  pin.
