# C1: Ground Truth — bd/bv Commands and Expected Signals

**Versions:** bd v1.0.4 (ce242a879) · bv v0.16.2  
**Date:** 2026-06-04  
**Branch:** worktree-spike+8p1t-bd-bv-semantics  
**Issue:** ansible-all-my-things-8p1t.1

---

## 1. Command Inventory for "Next Immediate Action"

The following commands are required to answer "what is the next immediate
action?" unambiguously.

| # | Command | Role |
|---|---------|------|
| 1 | `bd list --status=in_progress` | Identify active WIP; scope the analysis |
| 2 | `bd ready` | **Authoritative**: all issues with no open blocking deps |
| 3 | `bd blocked` | **Authoritative**: all issues blocked by open explicit deps |
| 4 | `bd show <id>` | Full issue detail — CHILDREN section shows parent-child members |
| 5 | `bd dep list <id> --direction up` | What depends on this issue (who it gates) |
| 6 | `bd dep cycles` | Detect wiring errors — must return "No cycles" |
| 7 | `bv --robot-triage --format toon` | Graph metrics, PageRank, betweenness — supplementary only |

Commands **not** suitable as authoritative readiness signals:
- `bd dep tree <id>` — direction is counterintuitive for parent-child; see §3
- `bv unblocks_ids` — counts parent-child as blocking; `bd ready` does not; see §4

---

## 2. Desired Semantics

For an issue `X` to appear in `bd ready`:
- `X` must have status `open`
- Every explicit dep-add blocker of `X` must be closed

For a parent-issue `P` with children `C1..Cn` attached via `--parent`:
- `P` is excluded from `bd ready` while any child is open (parent-gating)
- Children `C1..Cn` are NOT gated by `P`'s status — they appear in `bd ready`
  regardless of whether `P` is `open`, `in_progress`, or anything else

This is the intended design: **children block the parent, not the other
way around.**

---

## 3. DESIRED vs OBSERVED — Two-Column Record

Tested against the live `ansible-all-my-things` repo with spike
`ansible-all-my-things-8p1t` (in_progress) and 8 children (all open).

| Command | Desired signal | Observed | Gap? |
|---------|---------------|----------|------|
| `bd ready` | All actionable issues including spike children | All 8 children listed as ready | **None — correct** |
| `bd blocked` | Issues blocked by open explicit deps; no spike children | 13 blocked issues, zero spike children | **None — correct** |
| `bd dep cycles` | No cycles | "✓ No dependency cycles detected" | **None — correct** |
| `bd dep list 8p1t` (down) | No results — parent has no explicit blockers | "has no dependencies" | **None — correct** |
| `bd dep list 8p1t --direction up` | Shows 8 children via parent-child | All 8 children listed via parent-child | **None — correct (but label misleads; see below)** |
| `bd dep list 8p1t.1` (down) | Should signal "not blocked" | Shows `8p1t (in_progress) via parent-child` — implies child depends on parent | **Misleading: stored as child→parent dep, but NOT enforced as blocker** |
| `bd dep tree 8p1t` | Ideally shows children below parent | Shows ONLY `8p1t` — no children | **Missing: parent-child not visible from parent in dep tree** |
| `bd dep tree 8p1t.1` | Show what blocks C1 | Shows `8p1t [parent-child]` below C1 — as if parent is a blocker | **Misleading: visual suggests C1 depends on 8p1t, but 8p1t does NOT block C1** |
| `bv unblocks_ids` for `8p1t` | Match issues NOT in `bd ready` | Lists all 8 children — but all 8 already in `bd ready` | **Misleading: bv treats parent-child as blocking; bd does not** |

---

## 4. Root Cause of Agent Disagreement

Two agents can read the same tree and reach opposite conclusions because
two commands tell contradictory stories:

**Path A — agent reads `dep tree 8p1t.1`:**
```
8p1t.1 [READY]
  └── 8p1t (in_progress) [parent-child]
```
Conclusion: "C1 depends on 8p1t; 8p1t is in_progress not closed → C1 is blocked."  
**Wrong.** `dep tree` direction for parent-child shows the storage direction
(child stores a pointer to parent), NOT a blocking direction.

**Path B — agent reads `bd ready`:**
```
○ ansible-all-my-things-8p1t.1 ● P2 C1: Define ground truth ...
```
Conclusion: "C1 is in bd ready → actionable."  
**Correct.** `bd ready` is the authoritative readiness gate.

**`bv` amplifies Path A:** `bv --robot-triage` reports `unblocks_count: 8` for
`8p1t`, listing all children as issues it would "unblock." This makes an agent
think the parent must be closed before children can be worked. But those
children are already in `bd ready`. bv computes unblocks from graph edges
including parent-child; `bd` does not honor that direction for child readiness.

---

## 5. Canonical Wiring Rule

```
# CORRECT: attach child to parent → parent is gated, children are free
bd update <child-id> --parent <parent-id>

# Verify: children appear in bd ready immediately
bd ready | grep <child-id>   # must appear

# Verify: parent is gated while children open
bd ready | grep <parent-id>  # must NOT appear

# WRONG (for sub-tasks): creates a true blocking dep — child excluded from bd ready
bd dep add <child-id> <parent-id>   # child blocked until parent closed
```

When you need children to be **sequentially blocked** (C2 cannot start until
C1 closes), add explicit dep edges between siblings:

```
bd dep add 8p1t.2 8p1t.1   # C2 depends on C1
bd dep add 8p1t.3 8p1t.2   # C3 depends on C2
# etc.
```

Without sibling deps, all children are independently ready.

---

## 6. Pending bd v1.0.4 Fix — Scope

The memory note for this spike states: "Unknown whether upcoming bd release
corrects hierarchy/blocking (readiness) semantics — DATABASE changes are in
changelog."

**Observed:** The data-loss bugs in bd v1.0.4 are:
- `bd update --append-notes` → silent no-op (exit 0, nothing persisted)
- `bd update --status in_progress` chained after `--claim` → silent no-op

Both are persistence bugs, not readiness/dependency computation bugs.

**Conclusion:** The pending fix targets persistence (DB writes). It does NOT
touch the parent-child gating logic or the `bd ready` readiness algorithm.
All findings in this spike are valid for v1.0.4 and do NOT require
re-validation after the DB fix.

---

## 7. Spike Exit Criteria (confirmed)

The spike (`8p1t`) is complete when:

1. **Canonical wiring** for parent-child + sequential sub-task deps is stated
   with command evidence (this document + C3 sandbox results)
2. **Canonical command sequence** for show-next is defined: `bd list
   --status=in_progress` → `bd ready` → `bd blocked` → `bd show <wip>` for
   CHILDREN context; `bv --robot-triage` supplementary only
3. **Conclusion survives cold-read** (C4 verification)
4. **`my-omc-show-next` skill updated** (C6) with authoritative-source rule
5. **Live RTK tree re-wired** per findings (C7)

---

## 8. Key Rule for `my-omc-show-next`

> **`bd ready` is the single authoritative source for actionability.**
> `dep tree`, `dep list --direction down`, and `bv unblocks_ids` are
> supplementary graph views and MUST NOT override `bd ready`.
> An issue in `bd ready` is actionable, period.
