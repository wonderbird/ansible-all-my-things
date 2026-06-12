# Possible Solutions

Each solution lists the root cause ID(s) (see `root-cause-candidates.md`)
it addresses.

## S1 — Delete the 9 orphaned `.claude/commands/speckit.*.md` files

Addresses: **RC1, RC2, RC3**

Remove the 9 dot-named command files listed in `evidence.md`'s File
Inventory. The hyphen-named `.claude/skills/speckit-<name>/SKILL.md`
versions are a superset of the *workflow logic* (same steps plus
`extensions.yml` hook dispatch), and nothing outside the 9 files
references `.claude/commands/speckit.*.md` (see "Live References" in
`evidence.md`) — `workflow.yml` uses abstract per-integration command IDs,
and `speckit.constitution.md`'s self-reference is removed along with its
own file.

**Open point for the implementer**: 5 of the 9 command files carry a
`handoffs:` frontmatter key (command-chaining hints to follow-up commands)
that has no equivalent in any skill file. Deleting the commands drops this
hint. Decide whether to accept the loss or port `handoffs` into the
corresponding `SKILL.md` frontmatter as part of the S1 change — either is
viable, but it should be a deliberate choice, not an oversight.

## S2 — Check for an official spec-kit migration/cleanup command first

Addresses: **RC1, RC2, RC3**

Before doing S1, check upstream spec-kit v0.8.18 docs/CLI (`speckit
--help`, changelog) for a migration or cleanup command (e.g. `speckit
doctor`, `speckit migrate`, `speckit clean`) that removes files superseded
by `ai_skills`. If one exists, run it and verify it produces the same end
state as S1 (including a decision on the `handoffs` question above). If
none exists, proceed directly with S1.

## S3 — Report upstream: updater should detect/remove superseded command files

Addresses: **RC1, RC2**

File an issue (or PR) against spec-kit's "claude" integration
installer/updater: when `ai_skills: true` installs
`.claude/skills/speckit-<name>/SKILL.md`, the updater should detect a
pre-existing `.claude/commands/speckit.<name>.md` with the same `<name>`
and either remove it or warn the user. Fixes the class of problem for
future updates and other projects; does not by itself fix this repo's
current state.

## S4 — Document a post-update orphan-check step

Addresses: **RC2, RC3, RC4**

Add a step to this project's spec-kit usage docs (e.g. `CONTRIBUTING.md`):
after running `speckit update`, check for `.claude/commands/speckit.*.md`
files that duplicate a `.claude/skills/speckit-*/` entry, and remove the
command file. Cheap, repo-local, future-update insurance — independent of
whether upstream ever implements S3.

## S5 — Accept no built-in conflict detection

Addresses: **RC4**

Claude Code does not warn when a custom command and a Skill cover the same
workflow; no tooling change is proposed for this. Covered by S1 (removes
the current duplication) and S4 (catches recurrences after future
updates) — no separate action needed.

## S6 — Standardize on the `speckit` CLI for install/update

Addresses: **RC5**

If a future investigation finds installs performed via inconsistent
mechanisms (manual template copy vs. CLI), document in `CONTRIBUTING.md`
that `speckit init` / `speckit update` is the only supported install path.
Low priority: RC5 is the least-supported candidate and current evidence
shows a single coherent CLI-driven timeline.
