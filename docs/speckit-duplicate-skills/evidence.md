# Speckit Skill Duplication — Evidence

## Summary

Every "core" speckit workflow appears twice in skill catalog:

- `.claude/skills/speckit-<name>/SKILL.md` (hyphen, e.g. `speckit-plan`)
- `.claude/commands/speckit.<name>.md` (dot, e.g. `speckit.plan`)

9 commands duplicated. 5 git-extension skills NOT duplicated (no
`.claude/commands/speckit.git.*` exist) — control case, see below.

## File Inventory

| Name           | Skill (hyphen)                                  | Command (dot)                          |
|----------------|--------------------------------------------------|-----------------------------------------|
| analyze        | `.claude/skills/speckit-analyze/SKILL.md`        | `.claude/commands/speckit.analyze.md`    |
| checklist      | `.claude/skills/speckit-checklist/SKILL.md`      | `.claude/commands/speckit.checklist.md`  |
| clarify        | `.claude/skills/speckit-clarify/SKILL.md`        | `.claude/commands/speckit.clarify.md`    |
| constitution   | `.claude/skills/speckit-constitution/SKILL.md`   | `.claude/commands/speckit.constitution.md` |
| implement      | `.claude/skills/speckit-implement/SKILL.md`      | `.claude/commands/speckit.implement.md`  |
| plan           | `.claude/skills/speckit-plan/SKILL.md`           | `.claude/commands/speckit.plan.md`       |
| specify        | `.claude/skills/speckit-specify/SKILL.md`        | `.claude/commands/speckit.specify.md`    |
| tasks          | `.claude/skills/speckit-tasks/SKILL.md`          | `.claude/commands/speckit.tasks.md`      |
| taskstoissues  | `.claude/skills/speckit-taskstoissues/SKILL.md`  | `.claude/commands/speckit.taskstoissues.md` |

Skills-only, no command equivalent (git extension):

`speckit-git-commit`, `speckit-git-feature`, `speckit-git-initialize`,
`speckit-git-remote`, `speckit-git-validate`.

## Timeline (git history)

- `1191dd2` (2026-03-11) "feat: add spec-kit commands, templates and scripts"
  → added the 9 `.claude/commands/speckit.*.md` files (dot-named). Pre-manifest
  spec-kit generation — no `.specify/integration.json` or manifest files existed
  yet.
- `0ecc931` (2026-06-11) "ai: update spec kit" → spec-kit upgraded to v0.8.18.
  - Added all 14 `.claude/skills/speckit-*/SKILL.md` files (9 core + 5 git
    extension, hyphen-named).
  - Added new tracking files: `.specify/integration.json`,
    `.specify/integrations/claude.manifest.json`,
    `.specify/integrations/speckit.manifest.json`,
    `.specify/init-options.json`, `.specify/extensions.yml`,
    `.specify/extensions/.registry`, `.specify/extensions/git/*`.
  - Did **not** touch or remove anything under `.claude/commands/`.

## Manifest Evidence

`.specify/integrations/claude.manifest.json` (speckit v0.8.18,
`installed_at: 2026-06-11T15:13:16Z`) tracks exactly 9 files — all
`.claude/skills/speckit-<name>/SKILL.md` for the 9 core commands. The
`.claude/commands/speckit.*.md` files (9, dot-named) appear in **no**
manifest.

Caveat: the 5 `.claude/skills/speckit-git-*/SKILL.md` (git extension)
files *also* don't appear in `claude.manifest.json` — they're tracked via
`.specify/extensions/.registry` instead. So "absent from
`claude.manifest.json`" alone doesn't prove a file is an orphan. The
dispositive fact for the 9 command files is the **timeline**: `1191dd2`
(2026-03-11) predates `0ecc931` (2026-06-11), which is when *any* manifest
or registry first appeared in this repo — the command files predate the
entire tracking system, not just one manifest.

`.specify/integration.json`:

```json
"integration_settings": {
  "claude": { "script": "sh", "invoke_separator": "-" }
}
```

`invoke_separator: "-"` explains the hyphen naming of new skill files.

`.specify/init-options.json` contains `"ai_skills": true` — new option that
enables the Skills-based Claude integration in v0.8.18.

## Content Comparison (`plan` example)

`.claude/skills/speckit-plan/SKILL.md`:

- Frontmatter: `name`, `description`, `argument-hint`, `compatibility`,
  `metadata.author: github-spec-kit`, `metadata.source:
  templates/commands/plan.md`, `user-invocable`, `disable-model-invocation`.
- Body: same Outline / Phases / Key-rules as the command version, **plus**
  a "Pre-Execution Checks" and "Mandatory Post-Execution Hooks" section
  (dispatches `.specify/extensions.yml` hooks) and a "Done When" checklist.

`.claude/commands/speckit.plan.md`:

- Frontmatter: `description` + `handoffs` (to `speckit.tasks`,
  `speckit.checklist`).
- Body: Outline / Phases / Key-rules only — no extension-hook dispatch.
  Step 3 of Phase 1 calls `update-agent-context.sh` directly.

→ Skill version is a superset of *body/workflow logic*: same core
workflow plus the `extensions.yml` hook-dispatch mechanism that did not
exist when the command version was installed.

**Not a superset of frontmatter**: 5 command files (`clarify`,
`constitution`, `plan`, `specify`, `tasks`) carry a `handoffs:` key
suggesting follow-up commands (e.g. `speckit.plan` → `speckit.tasks`,
`speckit.checklist`). Verified: **none** of the 14
`.claude/skills/speckit-*/SKILL.md` files contain a `handoffs:` key. The
skill versions drop this command-chaining hint entirely.

## Live References to `.claude/commands/speckit.*.md`

- `.specify/workflows/speckit/workflow.yml` (added by `0ecc931`) has steps
  with `command: speckit.specify`, `speckit.plan`, `speckit.tasks`,
  `speckit.implement`. This workflow declares compatibility with multiple
  integrations (`claude`, `copilot`, `gemini`, `opencode` —
  `requires.integrations.any`), so `command:` values are **abstract,
  per-integration command IDs**, not literal file paths — a literal
  `.claude/commands/...` path would not resolve for non-Claude
  integrations. For the `claude` integration,
  `integration_settings.claude.invoke_separator: "-"` (in
  `.specify/integration.json`) maps `speckit.plan` → `speckit-plan`, i.e.
  the **skill**. `workflow.yml` does not depend on
  `.claude/commands/speckit.*.md`.
- `.claude/commands/speckit.constitution.md:49` (one of the 9 files in
  question) instructs: "Read each command file in
  `.claude/commands/speckit.*.md` ... to verify no outdated references
  remain." This self-reference is contained entirely within the file set
  proposed for removal — deleting all 9 files removes this instruction
  along with its only container. No file *outside* the 9 references
  `.claude/commands/speckit.*.md`.

## Extension Evidence (control case — no duplication)

`.specify/extensions/git/commands/speckit.git.*.md` (5, dot-named, source
templates inside `.specify/extensions/git/`) were installed as
`.claude/skills/speckit-git-*/SKILL.md` (5, hyphen-named) by `0ecc931`. No
`.claude/commands/speckit.git.*.md` exist — the git extension is new in
v0.8.18, so there is no pre-existing command file to collide with.

This confirms: duplication occurs **only** for commands that existed in
both the old (`.claude/commands/`, pre-0.8.18) and new
(`.claude/skills/`, v0.8.18) integration generations.
