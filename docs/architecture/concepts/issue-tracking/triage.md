# Issue triage and next-action determination with beads

> **Validated for:** bd v1.0.4 (ce242a879) · bv v0.16.2 — 2026-06-04;
> dep-add type matrix re-validated 2026-06-06.
> Re-validate after bd v1.0.5 only if its changelog mentions parent-child
> gating, hierarchy/readiness, or `bd ready` behaviour.

## Bottom line

- `bd ready` is the **only** authoritative source for what is actionable.
- `bd blocked` is the **only** authoritative source for what is blocked.
- `--parent` is **display-only** — it does **not** gate readiness.
- `bd dep add` is the **only** mechanism that gates an issue in `bd ready`.
- `bv`, `bd dep tree`, and `bd dep list` are graph views — never use them to
  decide readiness.

## Why this matters

Two agents read the same issue hierarchy and reached opposite next-action
conclusions; neither matched `bd ready`. The cause: a parent-child edge
(`--parent`) shows up in `bd dep tree` and `bv --robot-triage` as if it were a
blocker, but `bd ready` does not treat it as one. Reasoning from the graph views
instead of `bd ready` produces wrong answers.

## What the experiment proved

A sandbox repo was used to change one wiring variable at a time and record
`bd ready` / `bd blocked`:

| Wiring | Parent in `bd ready`? | Child gated? | In `bd blocked`? |
| --- | --- | --- | --- |
| `--parent` (feature / task / epic) | Yes — not gated | No | No |
| `bd dep add <blocked> <blocker>` (same type) | N/A (blocker is ready) | Yes — absent | Yes |
| `bd dep add <sib2> <sib1>` | N/A | Yes — sib2 absent | Yes |
| `bd dep add` non-epic cross-type (e.g. feature←task) | N/A | Yes — blocked absent | Yes |
| `bd dep add` epic←epic | N/A | Yes | Yes |
| `bd dep add` epic↔non-epic (either direction) | N/A | N/A — rejected | N/A |

So in bd v1.0.4 `--parent` never blocks anything. It only adds the CHILDREN
section to `bd show`, a `← parent` annotation in `bd ready`, a non-blocking
`dep list --direction down` entry, and a (misleading) edge in `bv` graph metrics.

Separately, `bd dep add` accepts **any pair of issue types except `epic`**: an
epic connects only to another epic. Only epic↔non-epic edges are refused — in
**both** directions, with the same error: `Error: epics can only block other
epics, not tasks` (printed verbatim even when the non-epic is a feature,
milestone, or gate — the message always says "not tasks"). Every non-epic
pairing is accepted, same- or cross-type (verified 2026-06-06: `task←task`,
`feature←task`, `milestone←task`, `gate←task` succeed; `epic←epic` succeeds;
`epic↔non-epic` rejected both directions). A `--parent` link neither adds nor
removes any of these — it gates nothing.

**Caveat:** `bd dep cycles` does not catch a cycle formed by mixing `--parent`
and `bd dep add` in opposite directions between the same two issues. Audit
manually with `bd dep list <id> --direction up|down` when both are used.

## Canonical command sequence

```bash
bd list --status=in_progress   # 1. WIP context
bd ready                       # 2. actionable — AUTHORITATIVE
bd blocked                     # 3. blocked    — AUTHORITATIVE
bd show <parent-id>            # 4. CHILDREN = work scope (not blockers)
bd dep cycles                  # 5. wiring check (misses antiparallel — see caveat)
bv --robot-triage --format toon  # 6. priority ranking only — never readiness
```

## Rules

1. An issue in `bd ready` is actionable, period — regardless of `dep tree`,
   `dep list`, or `bv unblocks_ids`.
2. An issue absent from `bd blocked` is not blocked, regardless of `dep list`.
3. To enforce work order, use `bd dep add` — it connects **any pair of issue
   types except `epic`**, which connects only to another epic.
   `bd dep add <blocked> <blocker>` gates the blocked (first-arg) issue whenever
   the pair is permitted (any non-epic pair, or epic↔epic). Tasks **can** block
   tasks. Only epic↔non-epic is rejected — in **both** directions, emitting the
   same error regardless of argument order or the non-epic's actual type
   (`Error: epics can only block other epics, not tasks`). So a non-epic
   sub-task CANNOT gate its epic, and an epic CANNOT be gated out of `bd ready`
   by any non-epic (see AGENTS.md "Attaching Issues to Epics"). `--parent` alone
   sequences nothing.

   **Cycle-detector blind spot:** this hazard applies to ANY pair that can form
   a `bd dep add` edge — any non-epic pair (same- or cross-type) and epic↔epic.
   If the child was already attached with
   `--parent <container>`, the gating `bd dep add` adds an edge antiparallel to
   that `--parent` edge — the exact pair `bd dep cycles` cannot detect (see the
   [caveat above](#what-the-experiment-proved)). Do not apply this
   container-gating pattern in bulk; reserve it for deliberate one-offs and
   audit each one manually with `bd dep list <id> --direction up|down`.

---

*Derived from a bd/bv semantics spike (sandbox experiment, 2026-06-04;
dep-add type matrix re-validated 2026-06-06).*
