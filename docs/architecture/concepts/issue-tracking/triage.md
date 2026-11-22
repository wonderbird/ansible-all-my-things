# Issue triage and next-action determination with beads

> **Validated for:** bd v1.3.4 (7ef2fd05e) — 2026-11-21. The `bv` statements
> were last validated with bv v0.16.2 — 2026-06-04.
> Re-validate after a bd upgrade whose changelog mentions parent-child
> gating, hierarchy/readiness, or `bd ready` behaviour.

## Bottom line

- `bd ready` is the **only** authoritative source for what is actionable.
- `bd blocked` is the **only** authoritative source for what is blocked.
- `--parent` does **not** gate the parent's readiness. A block on the parent
  cascades to its children.
- `bd dep add` is the **only** mechanism that blocks an issue.
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
| `bd dep add` cross-type (e.g. feature←task, epic←task, task←epic) | N/A | Yes — blocked absent | Yes |
| `bd dep add` epic←epic | N/A | Yes | Yes |
| `--parent` child of a blocked epic | No — blocked | Yes — absent | Yes |
| `bd dep add` between an issue and its own ancestor or descendant | N/A | N/A — rejected | N/A |

`bd dep add` accepts any pair of issue types, epics included (verified
2026-11-21: `task←task`, `feature←task`, `milestone←task`, `gate←task`,
`epic←epic`, `epic←task` and `task←epic` succeed). It refuses only an edge
between an issue and its own ancestor or descendant, in both directions
(verified 2026-11-22 for a child and a grandchild):

- `<ancestor> <descendant>`: `cannot be blocked by its descendant ...: blocked
  status cascades to descendants, so ... would inherit the block and never
  close`.
- `<descendant> <ancestor>`: `cannot add dependency: ... is already a child of
  .... Children inherit dependency on parent completion via hierarchy. Adding
  an explicit dependency would create a deadlock`.

A `--parent` link adds the CHILDREN section to `bd show` and a `← parent`
annotation in `bd ready`. It never gates the parent. A block on the parent,
however, cascades: while an epic is blocked, its open children are absent from
`bd ready` and listed in `bd blocked`.

A `--parent` link does gate closing. `bd close` refuses any issue with an open
direct child, whatever the types: `cannot close <id>: 1 open child issue(s);
close children first or use --force to override` (verified 2026-11-22 for
epic, feature and task parents with a gate child). The guard checks direct
children only, and `--force` bypasses it.

## Canonical command sequence

```bash
bd list --status=in_progress   # 1. WIP context
bd ready                       # 2. actionable — AUTHORITATIVE
bd blocked                     # 3. blocked    — AUTHORITATIVE
bd show <parent-id>            # 4. CHILDREN = work scope (not blockers)
bd dep cycles                  # 5. wiring check
bv --robot-triage --format toon  # 6. priority ranking only — never readiness
```

## Rules

1. An issue in `bd ready` is actionable, period — regardless of `dep tree`,
   `dep list`, or `bv unblocks_ids`.
2. An issue absent from `bd blocked` is not blocked, regardless of `dep list`.
3. To enforce work order, use `bd dep add <blocked> <blocker>`. It gates the
   blocked (first-arg) issue for any pair of issue types, except an issue and
   its own ancestor or descendant, which bd rejects. A sub-task therefore
   cannot gate its epic. `--parent` alone sequences nothing.
4. Blocking an epic also blocks all its open children. Before you block an
   epic, check with `bd show <epic-id>` that no child must stay actionable.
5. To keep an epic open until a check is done, make the check a child of the
   epic, as the `record-findings` skill does with its findings gate. Never
   close a parent with `bd close --force`.

## Gates

`bd create --help` omits `gate` and `molecule` from its `--type` list, but
bd 1.3.4 accepts both (verified 2026-11-21). `bd create --type gate` leaves
the gate's await type empty. `bd gate create --type=human --blocks <id>` sets
it to `human`, and `bd gate check` never resolves a human gate, so only a
person closes it.

---

*Derived from a bd/bv semantics spike (sandbox experiment, 2026-06-04;
dep-add matrix re-validated with bd v1.3.4, 2026-11-21; close guard verified
2026-11-22).*
