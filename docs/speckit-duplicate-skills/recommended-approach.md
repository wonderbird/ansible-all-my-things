# Recommended Approach

## Background (for newcomers)

This repo's Claude Code skill catalog lists every "core" spec-kit workflow
twice — e.g. both `speckit-plan` (a **Skill**, dir
`.claude/skills/speckit-plan/`) and `speckit.plan` (a **Command**, file
`.claude/commands/speckit.plan.md`). Same applies to `analyze`,
`checklist`, `clarify`, `constitution`, `implement`, `specify`, `tasks`,
`taskstoissues` — 9 pairs total. Full details: `evidence.md`.

**Short version of the root cause** (full discussion: `root-cause-candidates.md`,
ID **RC1**): the 9 `.claude/commands/speckit.*.md` files are leftovers from
an older spec-kit install (2026-03-11). A later update to spec-kit v0.8.18
(2026-06-11) introduced Skills as the new integration mechanism and added
the 9 `.claude/skills/speckit-*/SKILL.md` equivalents — but the updater had
no way to know the old command files existed, so it never removed them.
They're harmless duplicates, not a sign of misconfiguration.

The pairs below match each root cause (`RC1`–`RC5`) to a fix
(`S1`–`S6`, full list: `possible-solutions.md`), **ordered by how likely
each fix is to actually resolve things** — #1 is the one to act on; the
rest are optional follow-ups or "no action needed" for completeness.

## 1. Delete the 9 leftover command files (RC1 + S1)

This is the actual fix. Remove the 9 `.claude/commands/speckit.*.md`
files listed in `evidence.md`. The matching `.claude/skills/speckit-*`
versions already cover the same workflow steps, plus a newer hook
mechanism (`extensions.yml`) the old files don't have.

No hidden dependencies on the command files:

- The bundled `speckit` workflow (`.specify/workflows/speckit/workflow.yml`)
  refers to commands like `speckit.plan` by an abstract name shared across
  multiple AI tools (Claude, Copilot, Gemini, ...), not by this repo's file
  path. For Claude, that abstract name maps to the **Skill**
  (`speckit-plan`), not the command file. Deleting the command files
  doesn't break this workflow.
- `speckit.constitution.md` (one of the 9 files) tells the agent to check
  "every file in `.claude/commands/speckit.*.md`" — but that instruction
  only exists inside the 9 files being deleted. Nothing outside them
  points at `.claude/commands/`.

**One thing to decide before deleting**: 5 of the 9 command files have a
`handoffs:` field — a hint that, e.g., after running `speckit.plan` you
might want to run `speckit.tasks` next. None of the Skill files have this.
Deleting the command files removes that hint. Either that's fine (the
Skills work without it), or someone adds equivalent `handoffs:` entries to
the Skill files as part of this change. Make this an explicit choice, not
an accident.

**Before deleting, ~5 minutes**: check if spec-kit itself ships a command
for this (something like `speckit doctor` or `speckit migrate`). If it
does and it also handles the `handoffs:` question, use it instead. If not,
just delete the 9 files.

## 2. Add a check to the upgrade docs (RC2/RC3/RC4 + S4)

Why this happened in the first place: spec-kit's updater doesn't clean up
files from older installs (RC2/RC3), and Claude Code itself never warns
when a Skill and a Command cover the same thing (RC4) — so nothing would
flag this if it happened again after a future `speckit update`.

Fix: add one line to `CONTRIBUTING.md` (or wherever spec-kit usage is
documented) — after running `speckit update`, check whether any
`.claude/commands/speckit.*.md` now duplicates a
`.claude/skills/speckit-*/` entry, and remove it if so. Cheap insurance
against this recurring.

## 3. Optional: report it to spec-kit upstream (RC1/RC2 + S3)

Same root cause as #1, but as a tooling gap in spec-kit itself: its
updater could detect "I'm installing a Skill for `plan`, and
`.claude/commands/speckit.plan.md` already exists from an older install —
remove it." Worth filing upstream if you maintain a relationship with the
spec-kit project, but it won't fix *this* repo (that's #1) and isn't on
any particular timeline.

## 4 & 5. No action needed (RC4 + S5, RC5 + S6)

- RC4 (Claude Code doesn't warn about Skill/Command overlap) is already
  handled by #1 (removes today's duplication) and #2 (catches it next
  time).
- RC5 (maybe the two installs used different tooling entirely) doesn't add
  anything #1 doesn't already explain — listed in
  `root-cause-candidates.md` for completeness, but no action follows from
  it unless new evidence turns up.

## Doing this work

1. Do #1: optionally check for a spec-kit migration command, decide the
   `handoffs:` question, delete the 9 `.claude/commands/speckit.*.md`
   files, commit.
2. Do #2: add the `CONTRIBUTING.md` check-after-update step, commit.
3. #3 is optional and separate from this repo's work.
