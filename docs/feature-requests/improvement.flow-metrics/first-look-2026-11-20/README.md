# Flow First Look, 2026-11-20 (Frozen)

This folder is a frozen copy of a one-off look at where delivered work in
this repository flows. Work is sorted into machines, lab, rework,
automated and discarded per month. The look covers 2026-04-01 to
2026-11-20, from git snapshot `0455604`. The page `report.html` explains
the categories and the charts. `answers.md` holds the answers, and
`method-evidence.md` holds the rules and the checks.

The copy is not maintained. It exists so the result can be reproduced and
discussed. A durable script for this metric would be built fresh, with
tests and drift detection, in `scripts/`.

## Reproduce

Run from this folder. Everything works offline from `raw/`:

```bash
python3 classify.py     # writes counts.json from raw/
python3 check_cases.py  # planted cases, both directions
python3 reconcile.py    # totals against independent baselines
python3 render.py       # writes report.html; open it in a browser
```

`snapshot.py` re-reads git and GitHub and overwrites `raw/`. Its `REPO`
constant holds an absolute path that must be adjusted first. A new snapshot
gives different numbers, and the fixed baselines in `reconcile.py` then no
longer apply.
