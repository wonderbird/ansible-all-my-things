---
name: role-creator
description: Create a new Ansible role in this repo end-to-end — scaffold, choose the right install pattern, wire version tracking, register it in a profile, and test it with Molecule. Use when adding a role for a new tool or capability.
when_to_use: Triggers include "create a role", "add a role", "new role", "install <tool> via Ansible", "add <tool> to the base profile". Use before scaffolding so the role follows this repo's conventions the first time.
---

# Role Creator

Procedure and tacit conventions for adding a role to this repository. Encodes
only what is **not** obvious from the constitution or `AGENTS.md`; it references
those and the exemplar roles rather than restating them.

**Authoritative sources — read/obey, do not duplicate:**

- `.specify/memory/constitution.md` — Principles (I idempotency, II role-first +
  Molecule + version-update, IV YAGNI, XI DRY, XII fail-loud, XIII no empty
  artefacts).
- `AGENTS.md` — repo workflow, remotes/PR, one-question-at-a-time.
- Skills to invoke at the right steps: `molecule-testing`, `fix-problem`,
  `review-documentation-here`, `format-markdown`, `commit`. If any is not in the
  session's skill list, it is a skill-manager skill — load it before use.

## When to use / not

- **Use** for any new role under `roles/`.
- **Not** for editing an existing role's tasks (just edit), or operator
  playbooks under `playbooks/{update-versions,backup,restore}/` (the
  Maintenance-playbook exception — not roles).

## Step 0 — Classify the role (decision tree)

Pick the archetype first; it drives every later step.

- **Versioned external tool** (dominant case) → install pattern from
  [reference/install-patterns.md](reference/install-patterns.md) **and**
  version-update wiring is **mandatory** (Principle II) —
  [reference/version-update-wiring.md](reference/version-update-wiring.md).
- **Config-only role** (no pinned upstream version, e.g. writes dotfiles) →
  no version-update wiring. If it applies opinionated global config, it likely
  belongs in an opt-in play, not `base` — see ADR
  `docs/architecture/decisions/005-install-only-profile.md`.
- **Runs in a container?** Yes → Molecule scenario (Principle II). No (desktop
  env, display manager, drivers) → validate on a full VM per
  `docs/architecture/concepts/testing.md`; no Molecule.
- **System-wide vs per-user install?** A single binary all users share →
  `/usr/local/bin` (see `opencode`). A tool that installs into each user's home
  or runs per-user → loop over `login_user_names` with `become_user` (see
  `specify_cli`, `ai_agent_workspace`).
- **Linux vs Windows.** Windows roles (`win_*`, `windows_*`) diverge: no
  Molecule, different validation. Out of scope here — mirror an existing
  `windows_*` role instead.

## Step 1 — Scaffold

```bash
bash scripts/new-role.sh <role_name>   # snake_case
```

Gotchas the script does **not** handle:

- It substitutes `ROLE_NAME` only. `ROLE_DESCRIPTION` in `meta/main.yml` is left
  literal — edit it by hand.
- `role-template/` ships only `meta/` and `molecule/default/`. There is **no**
  `tasks/` or `defaults/` — create them yourself, with real content (Principle
  XIII: never commit an empty or SPDX-only stub).

## Step 2 — Author `defaults/` and `tasks/`

Copy the shape of the exemplar role matching your archetype
([reference/install-patterns.md](reference/install-patterns.md)). The canonical
`tasks/main.yml` idiom for a versioned tool:

1. **Validate required vars** — `ansible.builtin.assert` on version format and
   checksum length (Principle XII fail-loud). No `default('')` for required
   values.
2. **Assert supported architecture** — `ansible_facts['architecture'] in <map>`.
3. **Map arch** — to whatever the chosen exemplar's upstream uses; naming
   varies (opencode `x64`/`arm64`; rtk `x86_64-…-musl`/`aarch64-…-gnu`).
4. **Idempotence gate** — derive one `_<role>_needs_install` fact, then guard the
   expensive tasks with `when:`. Signal choice:
   - binary reports the pinned version → compare `<tool> --version` (strip
     leading `v`); see `opencode`.
   - version string can't distinguish the build (source build, commit SHA) →
     write and compare a marker file (e.g. `.git_sha`); see `skill_manager`.
5. **Integrity-gated fetch** — `get_url` with `checksum: "sha256:{{ ... }}"`.
   Download to a file (never pipe to `sha256sum` — truncation gives wrong
   hashes).
6. **Install** — system-wide binary, or `/usr/local/lib/<tool>` + symlink for
   multi-file installs (see `nodejs`).

Rules that bite:

- Every `command`/`shell` needs `creates:` or `changed_when:`, or it breaks
  idempotence — unless it lives inside a `when: _needs_install` block that is
  skipped on the second run.
- Roles that build with node/npm must set `PATH` to include `/usr/local/bin`
  (where `nodejs` symlinks `node`/`npm`); set it once at block level, not per
  task.
- Roles that clone repos install `git` themselves via `apt` (see
  `ai_agent_workspace`); do not assume it is present.
- Never use `blockinfile` `append_newline`/`prepend_newline` (Principle I).

## Step 3 — `meta/main.yml`

- Set `galaxy_info.description` (the literal `ROLE_DESCRIPTION` left by the
  scaffold). `galaxy_info.role_name` is already substituted by `new-role.sh` —
  there is no top-level `role_name` key.
- **Dependency decision** (`docs/architecture/concepts/role-dependency-declaration.md`):
  - Hard runtime dep (a task hard-fails without another role's artefact, and
    only that role provides it) → declare in `dependencies:` **and** order it in
    the profile playbook **and** list it in Molecule `converge.yml` (all three;
    see `skill_manager` → `nodejs`).
  - Orchestration-convenience ordering only → explicit ordering **only**,
    never a `meta` dependency.

## Step 4 — Version-update wiring (mandatory when a version/SHA is pinned)

A pinned tool with no wiring silently escapes drift tracking (Principle II).
Four touchpoints, all required — details and the fetch-task reuse matrix in
[reference/version-update-wiring.md](reference/version-update-wiring.md):

1. A fetch task under `playbooks/update-versions/tasks/` — **reuse** an existing
   parametrized one where possible.
2. `query-versions.yml` — slurp defaults, extract current pin, fetch, report,
   add to the aggregate fail-when.
3. `perform-updates.yml` — fetch + `replace` the pin (re-compute checksums if
   any).
4. `docs/architecture/version-update-playbooks.md` — source-type list, tasks
   tree, and Tracked-tools table.

## Step 5 — Molecule scenario

Invoke the **`molecule-testing`** skill — it is authoritative for the scenario
files. Role-creation intersections only:

- Dockerfile: add `ca-certificates` if the role uses `get_url` over HTTPS; add
  build packages the role needs at converge time; do not add packages the role
  installs itself.
- `converge.yml`: list dependency roles explicitly, in order, before the role
  under test.
- Delete `prepare.yml` if nothing role-specific remains (Principle XIII).

## Step 6 — Register in a profile

Edit `playbooks/configure-profile-roles.yml` (the role lists), not
`configure-profile.yml` (the entry play). Add the role to the correct play's
`roles:`:

- `base` — all Linux hosts.
- `claude_opinionated` — opt-in global agent config only.
- `desktop` — desktop-only; add `tags: not-supported-on-arm64` for roles that
  cannot run on arm64.

Order the role **after** any role it depends on.

## Step 7 — Co-located docs

Every tool role has both (repo convention):

- `README.md` — what it installs, the boundary (what it does *not* do),
  requirements, role-variable table, dependencies, example playbook.
- `DESIGN.md` — non-obvious decisions: integrity model, idempotency signal
  rationale, why-not-a-package, version-update integration.

Mirror `roles/opencode/{README,DESIGN}.md`.

## Step 8 — Test and validate (local, before cloud — Principle III)

```bash
python3 -m venv .venv && source .venv/bin/activate   # if .venv absent
pip install -r requirements.txt
cd roles/<role_name>
../../scripts/with-molecule-lock.sh molecule test     # lock avoids the shared
                                                      # `instance` container clash
```

- Do not assume host arch — check `uname -m` when it matters.
- Spurious apt 404 during converge from a stale cached base image →
  `podman system prune -a -f`, then re-run (known flake, not a code defect).
- On any unexpected failure, invoke the `fix-problem` skill (Principle VII).

## Step 9 — Close out

1. Track findings discovered while implementing as beads, same priority,
   blocking the source task (Principle VIII).
2. Invoke `review-documentation-here`, then `format-markdown` (markdown must be
   lint-clean under `.markdownlint.json`, Principle VI).
3. Commit via the `commit` skill (Principle V). Conservative git policy: do not
   push or open a PR without explicit authority.

## Final checklist

- [ ] Scaffolded via `new-role.sh`; `ROLE_DESCRIPTION` replaced; no empty stubs.
- [ ] `tasks`/`defaults` follow the exemplar; required vars asserted; idempotent.
- [ ] `meta` dependencies correct (hard dep → three places).
- [ ] Version-update wired in all four touchpoints (if pinned).
- [ ] Molecule full lifecycle passes (`converge`, `idempotence` changed=0,
      `verify`).
- [ ] Registered in the correct profile play, ordered after deps.
- [ ] `README.md` + `DESIGN.md` present; markdown lint-clean.
- [ ] Findings tracked; committed via `commit` skill.
