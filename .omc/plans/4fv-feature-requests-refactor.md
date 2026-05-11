# Plan: beads-4fv — Refactor `docs/feature-requests/` + Top-Level Docs Rewrite

**Status:** Draft (direct mode, single plan, phased)
**Owner:** galadriel
**Linked issue:** ansible-all-my-things-4fv

---

## 1. Requirements Summary

Consolidate redundant memory-bank-style documentation under `docs/feature-requests/` into:
- Proper **feature-request docs** (`prd.md` + `solution-design.md`) for unfinished work.
- Proper **feature docs** (`docs/features/<name>/concept.md`) for already-implemented work.
- Proper **improvements docs** (`docs/improvements/<name>/concept.md`) for already-implemented improvements.
- Updated **top-level cross-cutting docs** (`docs/productContext.md`, `docs/techContext.md`) reflecting current stable state.

Strategy: **Hybrid Audit + Per-Target Executor** (Option D). Main session never reads raw sources; only the audit digest. Per-target subagents merge in parallel with bounded scope.

### Source inventory (24 files, ~2628 lines)

| Folder | Lines | Notes |
|---|---|---|
| `docs/feature-requests/feat.consistent.provisioning.style/` | ~1126 | 6 files. Partially implemented. |
| `docs/feature-requests/improvement.documentation.updates/` | ~1436 | 6 files. Partially implemented. |
| `docs/feature-requests/feat.install.kiro.ide/` | ~34 | 6 files. Stub. |
| `docs/feature-requests/feat.port.kiro.enhancements/` | ~32 | 6 files. Stub. |

### Destinations

| Target file | Action |
|---|---|
| `docs/features/consistent-provisioning-style/concept.md` | Merge implemented portion of `feat.consistent.provisioning.style/` |
| `docs/feature-requests/feat.consistent.provisioning.style/{prd.md,solution-design.md}` | Replace 6 source files with 2 new ones holding unimplemented portion |
| `docs/improvements/documentation-updates/concept.md` | Rewrite as proper concept doc (was memory-bank-style gap analysis). Folder renamed from typo `documentation-udpates`. |
| `docs/feature-requests/improvement.documentation.updates/{prd.md,solution-design.md}` | Replace 6 source files with 2 new ones holding unimplemented portion |
| `docs/feature-requests/feat.kiro/{prd.md,solution-design.md}` | Bundle both Kiro stub folders into one feature-request |
| `docs/productContext.md` | Full review + rewrite if audit surfaces net-new stable content |
| `docs/techContext.md` | Full review + rewrite if audit surfaces net-new stable content |

---

## 2. Acceptance Criteria

1. `docs/feature-requests/` contains exactly 3 folders: `feat.consistent.provisioning.style/`, `improvement.documentation.updates/`, `feat.kiro/`. Each has exactly `prd.md` + `solution-design.md` (no `activeContext.md`, `progress.md`, `projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`).
2. `docs/features/consistent-provisioning-style/concept.md` contains all stable + implemented content from `feat.consistent.provisioning.style/` source files. No "✅ COMPLETED" / "⏳ IN PROGRESS" status tags remain (per `review-documentation` skill — stable docs describe the system, not project status).
3. `docs/improvements/documentation-updates/concept.md` is a proper concept document (overview, scope, rationale, acceptance) — not a gap analysis. Folder is renamed from `documentation-udpates`.
4. `docs/productContext.md` and `docs/techContext.md` reflect current stable state. Any net-new stable content from feature-request sources is merged in. Status tags removed.
5. The `_AUDIT.md` digest exists (during work) and is deleted at end-of-plan.
6. Old folders `feat.install.kiro.ide/` and `feat.port.kiro.enhancements/` are removed.
7. `bd close ansible-all-my-things-4fv` succeeds.
8. `git status` clean at end. Commit pushed.
9. The `review-documentation-here` skill validation pass identifies no structural violations.

All criteria are file-level testable via `ls`, `grep`, or skill invocation.

---

## 3. Audit Digest Schema (Phase 1 output: `docs/feature-requests/_AUDIT.md`)

```markdown
# Audit Digest — docs/feature-requests cleanup

## Source files (24)
[one section per source file]

### docs/feature-requests/<folder>/<file>.md
**Lines:** <count>
**Summary:** <2-sentence description of contents>
**Sections:**
- L<start>-<end> "<section heading>" → status: KEPT | REDUNDANT | OUTDATED | NET-NEW
  - destination: <target path or "DROP">
  - reason: <one line>
  - bullets to lift (if NET-NEW): <key facts to preserve>
[...]

## Cross-cutting findings
- Implemented features detected: <list>
- Unimplemented work detected per source folder: <list>
- Net-new stable content for top-level docs: <list with destination productContext.md vs techContext.md>
- Contradictions found between sources or vs. top-level: <list>

## Per-target work breakdown
[one section per target file in §1 destinations table]

### Target: docs/features/consistent-provisioning-style/concept.md
**Action:** merge | rewrite | leave-as-is
**Input slices (audit-only, no source rereads needed):**
- <source file path>: lines <range> — <one line>
- ...
**Outline of new content:** <2-5 bullets>
**Notes for executor:** <constraints, e.g., "preserve existing §X heading">
[...]
```

The schema lets each executor work from its target section + the cited slice bullets only — never re-opening the 24 source files.

---

## 4. Implementation Steps

### Phase 1 — Audit (sequential, single subagent)

**Step 1.1** — Spawn `analyst` subagent (Opus).

- **Subagent type:** `oh-my-claudecode:analyst`
- **Model:** `opus`
- **Inputs (read):**
  - All 24 files under `docs/feature-requests/**`
  - `docs/productContext.md`, `docs/techContext.md`
  - `docs/architecture/solution-strategy.md`, `docs/architecture/decisions/**`, `docs/architecture/technical-debt/**`
  - `docs/features/consistent-provisioning-style/concept.md`
  - `docs/improvements/documentation-udpates/concept.md` (note current typo path)
  - `docs/features/**/concept.md`, `docs/features/**/prd.md` (for pattern reference)
  - `.specify/memory/constitution.md`
  - `AGENTS.md`
  - `.claude/skills/review-documentation-here/SKILL.md`
  - `/home/galadriel/.claude/skills/memory-bank-by-cline/SKILL.md`
- **Output (write):** `docs/feature-requests/_AUDIT.md` per schema in §3
- **Acceptance:** digest covers every source file; every section classified; every target has an input-slice list.
- **Prompt template:** "Produce a structured documentation-merge audit per schema at .omc/plans/4fv-feature-requests-refactor.md §3. Classify every section of every source file. Identify implemented vs unimplemented work per folder. Identify net-new content for top-level docs. Do not write any merge output yet."

### Phase 2 — Human review gate

**Step 2.1** — Main session reads `_AUDIT.md` (only) and presents summary to user via `AskUserQuestion`.

- Options: **Approve** | **Request changes (free-text)** | **Reject + revise scope**
- If "Request changes": re-run Phase 1 with feedback. Max 2 audit iterations.

### Phase 3 — Per-target executor merges (parallel where safe)

Each step spawns an `executor` subagent (Sonnet). Each reads **only** its target file + its `_AUDIT.md` slice. None re-reads source folders. Steps 3.1–3.5 are independent and run in parallel. Step 3.6–3.7 (top-level rewrites) run after 3.1–3.5 so they can incorporate any "lifted to top-level" decisions surfaced earlier.

**Step 3.1** — Merge implemented portion into feature concept.
- **Subagent:** executor, sonnet
- **Inputs:** `docs/features/consistent-provisioning-style/concept.md` + `_AUDIT.md` (slice for this target)
- **Output:** rewritten `docs/features/consistent-provisioning-style/concept.md`

**Step 3.2** — Create feature-request docs (unimplemented portion).
- **Subagent:** executor, sonnet
- **Inputs:** `_AUDIT.md` slice for `feat.consistent.provisioning.style/`
- **Outputs:**
  - Write `docs/feature-requests/feat.consistent.provisioning.style/prd.md`
  - Write `docs/feature-requests/feat.consistent.provisioning.style/solution-design.md`
  - Delete old: `activeContext.md`, `productContext.md`, `progress.md`, `projectbrief.md`, `systemPatterns.md`, `techContext.md` in same folder

**Step 3.3** — Rewrite improvements concept.
- **Subagent:** executor, sonnet
- **Inputs:** `docs/improvements/documentation-udpates/concept.md` + `_AUDIT.md` slice
- **Outputs:**
  - `git mv docs/improvements/documentation-udpates docs/improvements/documentation-updates`
  - Rewrite `docs/improvements/documentation-updates/concept.md` as proper concept doc

**Step 3.4** — Create improvement feature-request docs.
- **Subagent:** executor, sonnet
- **Inputs:** `_AUDIT.md` slice for `improvement.documentation.updates/`
- **Outputs:**
  - Write `docs/feature-requests/improvement.documentation.updates/prd.md`
  - Write `docs/feature-requests/improvement.documentation.updates/solution-design.md`
  - Delete the 6 old files in same folder

**Step 3.5** — Bundle Kiro feature-request.
- **Subagent:** executor, sonnet
- **Inputs:** `_AUDIT.md` slice for both `feat.install.kiro.ide/` + `feat.port.kiro.enhancements/`
- **Outputs:**
  - `mkdir docs/feature-requests/feat.kiro`
  - Write `docs/feature-requests/feat.kiro/prd.md`
  - Write `docs/feature-requests/feat.kiro/solution-design.md`
  - `git rm -r docs/feature-requests/feat.install.kiro.ide docs/feature-requests/feat.port.kiro.enhancements`

**Step 3.6** — Rewrite `docs/productContext.md` (sequential after 3.1–3.5).
- **Subagent:** executor, sonnet
- **Inputs:** current `docs/productContext.md` + `_AUDIT.md` slice for top-level product content
- **Output:** rewritten `docs/productContext.md` with status tags stripped, net-new stable content merged.

**Step 3.7** — Rewrite `docs/techContext.md` (sequential after 3.1–3.5, parallel with 3.6).
- **Subagent:** executor, sonnet
- **Inputs:** current `docs/techContext.md` + `_AUDIT.md` slice for top-level tech content
- **Output:** rewritten `docs/techContext.md` with status tags stripped, net-new stable content merged.

### Phase 4 — Cleanup

**Step 4.1** — Delete `docs/feature-requests/_AUDIT.md`.
**Step 4.2** — Verify acceptance criteria 1–6 via `ls` + `grep` from main session.

### Phase 5 — Verification

**Step 5.1** — Invoke `Skill("review-documentation-here")` from main session. Process any findings.

**Step 5.2** — Optional second-pass `code-reviewer` agent on the new docs for SOLID-style consistency (heading hierarchy, no status tags in stable docs, cross-links valid).

### Phase 6 — Close

**Step 6.1** — `bd close ansible-all-my-things-4fv`
**Step 6.2** — `git add docs/ .omc/plans/ && git commit && git push`
**Step 6.3** — `bd dolt push`

---

## 5. Risks + Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Audit misclassifies "implemented" vs "unimplemented" content | M | H | Phase 2 human review gate. User can request changes (max 2 iterations). |
| Executor hallucinates content beyond its audit slice | L | H | Each executor receives explicit "no source-folder rereads" constraint. Verify via diff that new content traces to audit bullets. |
| Top-level rewrite drifts top-level docs from current reality | M | M | Step 3.6/3.7 require executors to preserve existing top-level structure unless audit explicitly flags net-new. |
| Typo rename breaks unknown external link | L | L | grep already confirmed zero refs to "udpates" outside the folder. |
| Context exhaustion in main session | M | H | Main reads only `_AUDIT.md`. Per-executor scope bounded to one target. Phases 3.1–3.5 parallel to avoid sequential context bloat. |
| Source files deleted before audit consumed | L | H | Delete-old steps live inside executors that also write replacements. Single-step atomicity per folder. |
| `review-documentation-here` flags issues post-merge | M | L | Phase 5 catches; loop back into a targeted executor fix. |
| Bundled Kiro folder loses distinction between install + port | L | M | Solution-design has two clearly-labeled sections per audit slice. |
| Constitution / AGENTS.md guidance contradicts the chosen structure | L | M | Audit must read both and flag contradictions in its cross-cutting findings section. |

---

## 6. Verification Steps

```bash
# Criterion 1 — folder contents
ls docs/feature-requests/
# expect: feat.consistent.provisioning.style  feat.kiro  improvement.documentation.updates

for d in docs/feature-requests/*/; do
  echo "== $d =="
  ls "$d"
  # expect exactly: prd.md  solution-design.md
done

# Criterion 2 — no status tags in stable feature docs
grep -E "✅|⏳|❌|COMPLETED|IN PROGRESS" docs/features/consistent-provisioning-style/concept.md && echo FAIL || echo PASS

# Criterion 3 — typo folder gone, proper concept in place
test -d docs/improvements/documentation-udpates && echo FAIL || echo PASS
test -f docs/improvements/documentation-updates/concept.md && echo PASS || echo FAIL

# Criterion 4 — no status tags in top-level docs
grep -E "✅|⏳|❌|COMPLETED|IN PROGRESS" docs/productContext.md docs/techContext.md && echo FAIL || echo PASS

# Criterion 5 — audit cleanup
test -f docs/feature-requests/_AUDIT.md && echo FAIL || echo PASS

# Criterion 6 — kiro source folders gone
test -d docs/feature-requests/feat.install.kiro.ide && echo FAIL || echo PASS
test -d docs/feature-requests/feat.port.kiro.enhancements && echo FAIL || echo PASS

# Criterion 7 — beads closed
bd show ansible-all-my-things-4fv | grep -i closed

# Criterion 8 — git clean
git status --porcelain | wc -l   # expect 0 after commit + push
```

---

## 7. Context-Token Budget

- **Main session:** reads `_AUDIT.md` (~300-500 lines projected) + verification command output only. **No source-folder reads.**
- **Analyst (Phase 1):** ~2628 source lines + ~600 target lines + skills/constitution. Single bounded burn in subagent.
- **Each executor (Phase 3):** target file (~50-400 lines) + audit slice (~50-100 lines). Bounded.
- Parallel execution in Phase 3.1–3.5 keeps total wall time low and prevents sequential context accumulation.

---

## 8. Open Items Resolved

- Kiro bundled folder name: **`feat.kiro`**.
- Typo `documentation-udpates` → **`documentation-updates`** via `git mv` (no external refs found).
- Top-level `productContext.md` + `techContext.md`: **full review + rewrite if audit warrants** (Phase 3.6 + 3.7).
- Existing `docs/improvements/documentation-udpates/concept.md`: **rewrite as proper concept** (Phase 3.3).

---

## 9. Out of Scope

- Task breakdown for the new feature-requests (will redo when repo evolves — explicit user instruction).
- Restructure of role-level docs (`roles/*/README.md`, `DESIGN.md`) — separate concern.
- Changes to `specs/` working context.
- Migration of any other memory-bank-style folders not listed in §1.
