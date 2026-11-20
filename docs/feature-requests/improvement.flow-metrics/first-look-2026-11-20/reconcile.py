"""Reconcile the classification against independent baselines (plan Step 4).

The baselines were counted with git and gh outside classify.py (plan section
"Independent Baselines", VERIFIED 2026-11-20 at 0455604); the direct-commit
baseline is re-derived by the plan's one-liner into raw/direct-baseline.txt.
With --drop-direct-row the first delivered direct commit is removed from the
input on purpose, so the direct-commit equation must fail.
"""

import json
import sys
from pathlib import Path

import classify

RAW = Path(__file__).resolve().parent / "raw"
MERGED_PRS_BASELINE = 126
MERGE_COMMITS_BASELINE = 124
CLOSED_PRS_BASELINE = 16


def main():
    prs = json.loads((RAW / "prs.json").read_text())
    merges = json.loads((RAW / "merges.json").read_text())
    direct = json.loads((RAW / "direct.json").read_text())
    direct_baseline = _read_direct_baseline()

    # Deliberate break: drop the first direct commit that would be delivered
    if "--drop-direct-row" in sys.argv:
        index = next(i for i, commit in enumerate(direct)
                     if classify.in_scope(commit["committed"])
                     and classify.direct_exclusion(commit["subject"], commit["files"]) is None)
        print(f"deliberate break: dropped direct commit {direct[index]['sha'][:7]}")
        direct = direct[:index] + direct[index + 1:]

    # The four equations
    totals = classify.build_counts(prs, merges, direct)["totals"]
    absorbed = len(classify.ABSORBED)
    equations = [
        ("delivered PRs + absorbed = merged PRs", totals["delivered_prs"] + absorbed, MERGED_PRS_BASELINE),
        ("delivered PRs = merge commits", totals["delivered_prs"], MERGE_COMMITS_BASELINE),
        ("delivered direct commits = direct baseline", totals["delivered_direct"], direct_baseline),
        ("discarded + closed Dependabot = closed PRs", totals["discarded"] + totals["closed_dependabot"],
         CLOSED_PRS_BASELINE),
    ]
    failed = 0
    for label, actual, expected in equations:
        ok = actual == expected
        failed += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} {label}: {actual} vs {expected}")
    sys.exit(1 if failed != 0 else 0)


def _read_direct_baseline():
    fields = (RAW / "direct-baseline.txt").read_text().split()
    return int(fields[fields.index("remaining") + 1])


if __name__ == "__main__":
    main()
