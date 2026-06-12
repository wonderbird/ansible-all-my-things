# Root Cause Candidates

IDs used in `possible-solutions.md` and `recommended-approach.md`.

## RC1 — Updater manifest blind to pre-manifest files

`0ecc931` introduced the manifest/tracking system
(`integration.json`, `claude.manifest.json`, `speckit.manifest.json`) for
the first time. The 9 `.claude/commands/speckit.*.md` files were installed
by `1191dd2`, **before** any manifest existed. The v0.8.18 updater can only
know about, and clean up, files it itself wrote and recorded. Old files with
no manifest entry are invisible to it — they survive the upgrade as orphans.

**Discussion**: directly supported by evidence. `claude.manifest.json`
lists exactly the 9 new skill files — though absence from one manifest
isn't proof of orphan status by itself (the 5 git-extension skills are
also absent from it, tracked elsewhere). The dispositive fact is the
**timeline**: `1191dd2` (2026-03-11) predates `0ecc931` (2026-06-11), the
commit that introduced the *entire* manifest/registry system. The
`.claude/commands/*.md` files predate every tracking mechanism that could
have recorded them. The diff of `0ecc931` is purely additive for
`.claude/commands/` (zero lines touched). This is the most direct,
mechanical explanation and requires no assumption about upstream intent.

## RC2 — Additive-only upgrade design (no destructive cleanup by default)

Even if the updater *could* pattern-match `speckit.<name>.md` →
`speckit-<name>`, a safety-first upgrade tool may never delete files it
doesn't own, to avoid destroying user customizations. Cleanup of
superseded integration files would then require an explicit, separate,
opt-in step (e.g. a `speckit migrate` / `speckit clean` command).

**Discussion**: plausible design philosophy for an upgrade tool touching a
user's repo, but unverifiable from this repo alone — would need upstream
spec-kit source/docs to confirm such a command exists. Treat as a
contributing factor to RC1 rather than independent: it explains *why* RC1's
gap was an acceptable trade-off for upstream, not an oversight.

## RC3 — Migration step not executed

If v0.8.18 documents a manual migration step ("remove old
`.claude/commands/speckit.*.md` after enabling `ai_skills`"), it simply
wasn't run during `0ecc931`.

**Discussion**: consistent with evidence (nothing under `.claude/commands/`
was touched), but requires checking upstream spec-kit changelog/release
notes for v0.8.18 to confirm such a step is documented — out of scope for
this repo-local investigation. Cannot be verified or ruled out from local
evidence alone.

## RC4 — No conflict detection between Commands and Skills

Claude Code loads `.claude/commands/*.md` (custom slash commands) and
`.claude/skills/*/SKILL.md` (Skills) as independent mechanisms. Both
`speckit.plan` and `speckit-plan` are valid, simultaneously available, and
neither tool warns that two entries cover the same workflow.

**Discussion**: true and relevant — explains why the duplication went
unnoticed for ~3 months (2026-03-11 to 2026-06-11, and beyond, until this
investigation). It is not itself a *cause* of the duplication (RC1 is the
cause), but it explains the lack of any forcing function to catch or fix
it sooner.

## RC5 — Inconsistent installation methods across time

The March install (`1191dd2`, "feat: add spec-kit commands, templates and
scripts") and the June update (`0ecc931`, "ai: update spec kit") may have
used two different installation mechanisms entirely (e.g. manual template
copy vs. full `speckit` CLI), rather than one coherent install→upgrade
lineage.

**Discussion**: weakly supported. The June commit's `init-options.json`
(`"speckit_version": "0.8.18"`, `"ai_skills": true`, `"here": true`) and
manifest files look like a single coherent `speckit init`/`update` CLI run.
The March commit predates any manifest convention, which is fully explained
by RC1 (manifests didn't exist yet in that spec-kit version) without needing
a "different tool" assumption. RC5 adds no explanatory power beyond RC1 and
is the least likely candidate.
