# Speckit Skill/Command Dedup Guide

A quick playbook for the next time `specify integration upgrade claude` (or
any spec-kit update) leaves duplicate entries in the Claude Code skill
catalog. Background and full investigation: `evidence.md`,
`root-cause-candidates.md`, `possible-solutions.md`,
`recommended-approach.md`.

## How to spot it

Spec-kit installs each core workflow as a **Skill**
(`.claude/skills/speckit-<name>/SKILL.md`, hyphenated). Older installs used
**Commands** (`.claude/commands/speckit.<name>.md`, dot-separated). If both
exist for the same `<name>`, the workflow shows up twice in `/help` and the
skill catalog.

Check for duplicates:

```bash
for f in .claude/skills/speckit-*/SKILL.md; do
  name="$(basename "$(dirname "$f")")"      # speckit-plan
  dotname="speckit.${name#speckit-}.md"     # speckit.plan.md
  [ -f ".claude/commands/$dotname" ] && echo "DUP: $name <-> .claude/commands/$dotname"
done
```

Any `DUP:` line is a leftover command file from before spec-kit added the
Skill-based integration (v0.8.18, 2026-06-11 in this repo's history).
spec-kit's updater adds new Skill files but does not remove old Command
files — that's the whole bug.

## How to fix it

1. **Confirm no spec-kit migration command exists yet.** Run
   `specify --version` and `specify --help`. As of v0.8.18 there is no
   `update`/`migrate`/`doctor` subcommand that does this safely.
   `specify integration upgrade <key>` exists but reinstalls the whole
   integration with diff-aware file handling and requires `--force` once any
   file is modified — too broad/risky for removing a handful of leftover
   files. If a future version adds a narrow "remove superseded files"
   command, prefer that instead of manual deletion.

2. **Check the `handoffs:` field.** Some Command files have a `handoffs:`
   frontmatter field (e.g. "after `plan`, suggest running `tasks`"). Decide
   whether to port these into the matching `SKILL.md` files before deleting,
   or accept losing the hint (Skills work fine without it). Make this an
   explicit choice — don't silently drop it.

3. **Grep for live references** before deleting, in case something outside
   the duplicated files points at `.claude/commands/speckit.*.md`:

   ```bash
   grep -rn "claude/commands/speckit" --include="*.md" --include="*.yml" --include="*.yaml" .
   ```

   References found only inside the files being deleted (e.g. a command
   telling the agent to check "every file in `.claude/commands/speckit.*.md`")
   are self-contained and go away with the deletion.

4. **Delete the duplicate Command files**:

   ```bash
   rm .claude/commands/speckit.<name>.md   # for each DUP found above
   ```

5. **Verify**: re-run the dedup check from step 1 (should report nothing),
   and re-run the grep from step 3 (should only hit other docs/investigation
   files, not active config).

## Prevention

`CONTRIBUTING.md` already has a note to re-run this check after any future
`specify integration upgrade` — keep that note up to date if the detection
command above changes.
