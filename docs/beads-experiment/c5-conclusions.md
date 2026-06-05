# C5: Version-Scoped Conclusions

**Versions:** bd v1.0.4 (ce242a879) · bv v0.16.2  
**Date:** 2026-06-04  
**Sandbox:** `/tmp/beads-sandbox-8p1t` — torn down  
**Issue:** ansible-all-my-things-8p1t.5

---

## Final Conclusions (bd v1.0.4)

### 1. `--parent` is display-only — no readiness gating

`bd update <child> --parent <parent>` creates an organizational relationship.
In bd v1.0.4, it does NOT exclude the parent from `bd ready`, regardless of
issue type (feature, task, epic). Both parent and children appear in `bd ready`
simultaneously.

**Impact on show-next:** An agent cannot infer work order from `--parent`
structure alone. Any issue in `bd ready` is actionable in any order.

### 2. `bd dep add` is the ONLY blocking mechanism

`bd dep add <blocked> <blocker>` creates a true blocking relationship:
- Blocked issue absent from `bd ready`
- Blocked issue present in `bd blocked`
- `bd dep cycles` detects cycles in this edge set

Use `bd dep add` between siblings to enforce sequential ordering.

### 3. Authoritative commands for "next immediate action"

```
bd ready    → authoritative: what is actionable NOW
bd blocked  → authoritative: what is waiting on an explicit blocker
```

All other commands (`dep tree`, `dep list`, `bv unblocks_ids`) are
supplementary graph views — they do NOT override `bd ready` or `bd blocked`.

### 4. `bd dep cycles` does not cover parent-child edges

Cycles involving mixed `--parent` + `bd dep add` wiring in opposite directions
are NOT detected by `bd dep cycles`. Manual audit required:

```bash
bd dep list <id> --direction up    # who depends on this issue
bd dep list <id> --direction down  # what this issue depends on
# Antiparallel: id appears in both up output of B and down output of B for the same pair
```

### 5. bv graph metrics treat parent-child as blocking

`bv --robot-triage` reports `unblocks_ids` for parent issues listing all children,
as if closing the parent would unblock them. In bd v1.0.4 this is incorrect —
children are already in `bd ready`. Use bv for priority ranking and PageRank
context only; never for readiness decisions.

---

## Re-Validation Flag

**Re-validate after bd v1.0.5 if the changelog mentions any of:**
- "parent-child gating"
- "epic gating"
- "bd ready" + parent/child behavior
- "hierarchy" + "readiness"

The pending v1.0.4 → v1.0.5 fix targets persistence bugs (append-notes data
loss, status no-op). It does NOT touch readiness computation. These conclusions
are stable for v1.0.4 and unlikely to be invalidated by the DB fix — but
confirm when upgrading.

---

## Sandbox Teardown Record

- Path: `/tmp/beads-sandbox-8p1t`
- Issues created: sandbox-ztf, sandbox-ljj, sandbox-vr3, sandbox-d8l,
  sandbox-1tp, sandbox-1fd, sandbox-xqo, sandbox-5k6
- Status: removed (`rm -rf /tmp/beads-sandbox-8p1t`)
- Live project issues: untouched throughout the experiment
