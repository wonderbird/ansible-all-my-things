# C3: Controlled Experiment Matrix

**Versions:** bd v1.0.4 (ce242a879) · bv v0.16.2  
**Date:** 2026-06-04  
**Sandbox:** `/tmp/beads-sandbox-8p1t` (git + bd init, prefix `sandbox`)  
**Issue:** ansible-all-my-things-8p1t.3

---

## Sandbox Tree (baseline)

```
sandbox-ztf  [feature]  Back up and restore tool settings
  └── sandbox-ljj  [task]  Findings: tool backup investigation   (--parent)
        ├── sandbox-vr3  [task]  Finding: config file path missing  (--parent)
        └── sandbox-d8l  [task]  Finding: DB path resolution wrong  (--parent)
```

---

## EXP-C: `--parent` with feature/task types (baseline)

**Variable:** parent type = feature (sandbox-ztf); container type = task (sandbox-ljj)  
**Setup:** tree wired entirely via `--parent`  
**Hypothesis (from AGENTS.md):** parent excluded from `bd ready` while open children exist

**Observed:**
```
bd ready → all 4 issues listed (sandbox-ztf, sandbox-ljj, sandbox-vr3, sandbox-d8l)
bd blocked → No blocked issues
```

**Result: REFUTES hypothesis.** `--parent` does NOT gate parents of type feature or task.

---

## EXP-A: `--parent` with epic type

**Variable:** parent type changed to epic  
**Setup:**  
```
sandbox-1tp  [epic]   [EXP-A] Epic parent
  └── sandbox-1fd  [task]  [EXP-A] Child of epic   (--parent)
```

**Hypothesis:** epic type behaves differently — gated by open children

**Observed:**
```
bd ready → both sandbox-1tp AND sandbox-1fd appear
  ○ sandbox-1fd ● P2 [EXP-A] Child of epic ← [EXP-A] Epic parent
  ○ sandbox-1tp ● P2 [epic] [EXP-A] Epic parent
bd blocked → no results for either
```

**Result: REFUTES hypothesis.** Epic parent also appears in `bd ready` with open child.  
**`--parent` does NOT gate ANY parent type in bd v1.0.4.**

> Note: the `←` annotation in `bd ready` output is display-only — indicates the
> parent relationship, does NOT imply blocking.

---

## EXP-B: explicit `bd dep add`

**Variable:** wiring mechanism — explicit `bd dep add` instead of `--parent`  
**Setup:**  
```
sandbox-xqo  [task]  [EXP-B] Blocker
sandbox-5k6  [task]  [EXP-B] Blocked   →  bd dep add sandbox-5k6 sandbox-xqo
```

**Hypothesis:** explicit dep creates a true blocking relationship

**Observed:**
```
bd dep add sandbox-5k6 sandbox-xqo
→ "Added dependency: sandbox-5k6 depends on sandbox-xqo (blocks)"

bd ready →
  ○ sandbox-xqo ● P2 [EXP-B] Blocker    ← only blocker appears
  (sandbox-5k6 absent)

bd blocked →
  [● P2] sandbox-5k6: [EXP-B] Blocked by explicit dep
    Blocked by 1 open dependencies: [sandbox-xqo]
```

**Result: CONFIRMS hypothesis.** `bd dep add` creates a true blocking relationship:
- Blocker appears in `bd ready`
- Blocked issue absent from `bd ready`, present in `bd blocked`

---

## EXP-D: sibling sequential deps via `bd dep add`

**Variable:** dep between sibling children  
**Setup:**  
```
sandbox-vr3  Finding 1  (no blockers)
sandbox-d8l  Finding 2  →  bd dep add sandbox-d8l sandbox-vr3
```

**Hypothesis:** sibling dep creates sequential blocking (d8l waits for vr3)

**Observed:**
```
bd ready →
  ○ sandbox-vr3 ● P2 Finding: config file path missing    ← only vr3 ready
  (sandbox-d8l absent)

bd blocked →
  [● P2] sandbox-d8l: Finding: DB path resolution wrong
    Blocked by 1 open dependencies: [sandbox-vr3]
```

**Result: CONFIRMS hypothesis.** Sibling `bd dep add` creates proper sequential blocking.

---

## Summary Table

| Wiring | Mechanism | Parent in `bd ready`? | Child gated? | In `bd blocked`? |
|--------|-----------|----------------------|--------------|-----------------|
| `--parent` (feature) | parent-child | Yes — NOT gated | No | No |
| `--parent` (task) | parent-child | Yes — NOT gated | No | No |
| `--parent` (epic) | parent-child | Yes — NOT gated | No | No |
| `bd dep add child parent` | blocks | N/A — parent is blocker | Yes — absent from `bd ready` | Yes |
| `bd dep add sib2 sib1` | blocks | N/A | Yes — sib2 absent | Yes |

---

## Critical Finding: `--parent` is display-only in bd v1.0.4

**`--parent` does not create a blocking relationship of any kind:**
- Parent is not excluded from `bd ready`
- Child is not excluded from `bd ready`
- Nothing appears in `bd blocked`
- No cycle-check involvement

`--parent` only:
- Creates a `parent-child` edge stored in the dependency table
- Causes the CHILDREN section to appear in `bd show <parent>`
- Adds a `← parent-title` annotation to the child in `bd ready` output
- Creates a `dep list --direction down` entry on the child pointing to the parent
- Contributes to bv graph metrics (pagerank, betweenness) as if it were a blocking edge

**`bd dep add` is the ONLY mechanism that gates issues in `bd ready`.**

---

## Revision to C1 Ground Truth

C1 stated: "Parent is GATED by open children (parent excluded from `bd ready` while children are open)."

**This is incorrect for bd v1.0.4.** The experiments show no gating occurs via `--parent` for any type. The C1 doc captures the DESIRED semantics; the OBSERVED semantics are that `--parent` is display-only. This is the gap.

The AGENTS.md description ("epic is excluded from `bd ready` while any open child exists") describes intended design — NOT observed behavior in v1.0.4.

---

## Canonical Next-Action Command Sequence

Given these findings, the authoritative sequence for "what is the next immediate action" is:

```bash
# Step 1: Identify WIP context
bd list --status=in_progress

# Step 2: Find all actionable issues (authoritative)
bd ready

# Step 3: Find all explicitly blocked issues (authoritative)
bd blocked

# Step 4: Understand a specific parent's work scope
bd show <parent-id>   # CHILDREN section shows sub-tasks

# Step 5: Understand stored dependency edges for a specific issue
# WARNING: parent-child entries in --direction down are NOT blockers (display-only)
# Use bd blocked (Step 3) as the ONLY authoritative blocker source
bd dep list <id> --direction down   # what is stored as depending on this issue
                                    # parent-child entries here are NOT blockers
bd dep list <id> --direction up     # what depends on this issue (who it gates)

# Step 6: Detect explicit dep wiring errors
bd dep cycles   # must return "No cycles"
                # NOTE: does NOT detect antiparallel wiring — if you mixed --parent
                # and bd dep add between the same two issues, manually verify:
                #   bd dep list <id-A> --direction up   (who depends on A)
                #   bd dep list <id-A> --direction down (what A depends on)
                # Antiparallel = A appears in up AND down for the same pair

# Step 7 (supplementary only — do NOT use for readiness decisions)
bv --robot-triage --format toon
```

**Rules derived from experiments:**

1. **`bd ready` is the ONLY authoritative source for actionability.**
   An issue in `bd ready` is actionable regardless of what `dep tree`, `dep list`,
   or `bv unblocks_ids` suggest.

2. **`bd blocked` is the ONLY authoritative source for blocking.**
   An issue absent from `bd blocked` is not blocked, regardless of `dep list` output.

3. **`--parent` = display + bv graph only.**
   Never interpret a `dep list --direction down` parent-child entry as a blocker.
   Never interpret `bv unblocks_ids` for a parent as "children need parent closed."

4. **To enforce sequential work order, use `bd dep add`.**
   `--parent` alone does not enforce ordering.

5. **`bd dep cycles` does not detect all cycles.**
   Antiparallel `--parent` + `bd dep add` in opposite directions can coexist without
   being flagged. Manual audit required when both wiring mechanisms are mixed.
