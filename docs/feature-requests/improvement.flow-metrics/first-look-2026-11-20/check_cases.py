"""Planted cases for the flow first look (plan Step 4), each proven in both directions.

Stop cases: the bad input must stop with the named guard; the real snapshot
must not stop. Classification cases: a contrast input differing in the one
decisive detail must give a different result. Prints one line per case and
direction; exits 1 if any fails.
"""

import json
import sys
from pathlib import Path

import classify
from classify import GuardError

RAW = Path(__file__).resolve().parent / "raw"
results = []


def main():
    case_rework_precedence()
    case_automated_precedence()
    case_beads_neutral()
    case_tie_is_machines_mixed()
    case_neutral_only()
    case_beads_only_excluded()
    case_chore_excluded()
    case_cutoff_boundary()
    case_unknown_opener_stops()
    case_agent_identities()
    case_p_chart()
    case_absorbed_assertion()
    real_snapshot_passes_all_guards()

    failed = [line for ok, line in results if not ok]
    for ok, line in results:
        print(("PASS " if ok else "FAIL ") + line)
    print(f"{len(results) - len(failed)}/{len(results)} checks passed")
    sys.exit(1 if failed != [] else 0)


def case_rework_precedence():
    check(1, "fix(x) on .claude/ is rework", category_of("agent", "fix(x): y", [".claude/a.md"]) == "rework")
    check(1, "contrast feat(x) on .claude/ is lab", category_of("agent", "feat(x): y", [".claude/a.md"]) == "lab")


def case_automated_precedence():
    check(2, "Dependabot fix: is automated", category_of("automated", "fix: bump", [".github/w.yml"]) == "automated")
    check(2, "contrast agent fix: is rework", category_of("agent", "fix: bump", [".github/w.yml"]) == "rework")


def case_beads_neutral():
    check(3, ".claude/ + .beads/ is lab", category_of("agent", "feat: x", [".claude/a", ".beads/issues.jsonl"]) == "lab")
    check(3, "contrast .claude/ + roles/ is not lab", category_of("agent", "feat: x", [".claude/a", "roles/r/x"]) != "lab")


def case_tie_is_machines_mixed():
    tie = classify.path_vote([".claude/a", "roles/r/x"])
    check(4, "1 lab + 1 roles is machines, mixed", tie["vote"] == "machines" and tie["mixed"] is True)
    majority = classify.path_vote([".claude/a", ".claude/b", "roles/r/x"])
    check(4, "contrast 2 lab + 1 roles is lab, not mixed", majority["vote"] == "lab" and majority["mixed"] is False)


def case_neutral_only():
    neutral = classify.path_vote(["docs/a.md", "specs/b.md"])
    check(5, "docs/ + specs/ is machines, neutral_only, not mixed",
          neutral["vote"] == "machines" and neutral["neutral_only"] is True and neutral["mixed"] is False)
    voting = classify.path_vote(["docs/a.md", ".claude/b"])
    check(5, "contrast docs/ + .claude/ is lab, not neutral_only",
          voting["vote"] == "lab" and voting["neutral_only"] is False)


def case_beads_only_excluded():
    check(6, ".beads/-only direct commit is excluded",
          classify.direct_exclusion("chore: export", [".beads/issues.jsonl"]) == "beads-only")
    check(6, "contrast .beads/ + roles/ is not excluded",
          classify.direct_exclusion("feat: x", [".beads/issues.jsonl", "roles/r/x"]) is None)


def case_chore_excluded():
    check(7, "chore(x): direct commit is excluded", classify.direct_exclusion("chore(x): y", ["roles/r"]) == "chore")
    check(7, "contrast feat(x): is not excluded", classify.direct_exclusion("feat(x): y", ["roles/r"]) is None)


def case_cutoff_boundary():
    check(8, "2026-03-31T23:59:59Z is out", classify.in_scope("2026-03-31T23:59:59Z") is False)
    check(8, "contrast 2026-04-01T00:00:00Z is in", classify.in_scope("2026-04-01T00:00:00Z") is True)
    check(8, "2026-04-01T01:59:59+02:00 is out (UTC)", classify.in_scope("2026-04-01T01:59:59+02:00") is False)


def case_unknown_opener_stops():
    prs, merges = synthetic_dataset(opener="mallory")
    check(9, "unknown in-scope opener stops naming author map", stops_with(prs, merges, [], "author map"))
    prs, merges = synthetic_dataset(opener="eudicy")
    check(9, "contrast known opener does not stop", not stops_with(prs, merges, [], ""))


def case_agent_identities():
    check(10, "galadriel and lowercase eudicy are agent",
          classify.author_type("galadriel") == "agent" and classify.author_type("eudicy") == "agent")
    try:
        classify.author_type("Galadriel")
        stopped = False
    except GuardError as error:
        stopped = "author map" in str(error)
    check(10, "contrast Galadriel (case differs) stops", stopped)


def case_p_chart():
    steady = [(f"m{i}", 6, 30) for i in range(5)]
    at_mean = classify.p_chart(steady)
    check(11, "month at p-bar 0.2 with n=30 gives no signal",
          abs(at_mean["p_bar"] - 0.2) < 1e-9 and at_mean["signals"] == [])
    extreme = classify.p_chart(steady[:4] + [("m4", 27, 30)])
    check(11, "contrast month at 0.9 with n=30 gives a signal",
          any(signal.startswith("m4 outside") for signal in extreme["signals"]))
    small = classify.p_chart(steady + [("tiny", 4, 4)])
    check(11, "month with n=4 is flagged and left out of p-bar",
          small["flagged"] == ["tiny"] and abs(small["p_bar"] - 0.2) < 1e-9)


def case_absorbed_assertion():
    prs, merges = synthetic_dataset(opener="eudicy", extra_merged_without_merge=500)
    check(12, "third merged PR without own merge stops naming {94, 113}", stops_with(prs, merges, [], "{94, 113}"))
    prs, merges = synthetic_dataset(opener="eudicy")
    check(12, "contrast only 94 and 113 without own merge does not stop", not stops_with(prs, merges, [], ""))


def real_snapshot_passes_all_guards():
    prs = json.loads((RAW / "prs.json").read_text())
    merges = json.loads((RAW / "merges.json").read_text())
    direct = json.loads((RAW / "direct.json").read_text())
    check("9,12", "real snapshot passes every guard (passing direction)", not stops_with(prs, merges, direct, ""))


# ---------------------------------------------------------------- helpers


def check(case, label, ok):
    results.append((ok, f"case {case}: {label}"))


def category_of(author_kind, title, files):
    return classify.category(author_kind, title, files)[0]


def stops_with(prs, merges, direct, guard_name):
    try:
        classify.build_counts(prs, merges, direct)
    except GuardError as error:
        return guard_name in str(error)
    return False


def synthetic_dataset(opener, extra_merged_without_merge=None):
    """One delivered PR #1 with its merge, plus #94 and #113 merged without own merge."""
    prs = [
        pr_record(1, opener),
        pr_record(94, "eudicy"),
        pr_record(113, "eudicy"),
    ]
    if extra_merged_without_merge is not None:
        prs.append(pr_record(extra_merged_without_merge, "eudicy"))
    merges = [{
        "sha": "a" * 40, "committed": "2026-05-02T10:00:00+02:00", "author": "Stefan Boos",
        "subject": "Merge pull request #1 from x/y", "files": ["roles/r/x"], "commit_count": 1,
        "commit_authors": ["Eudicy"],
    }]
    return prs, merges


def pr_record(number, login):
    return {"number": number, "title": "feat: x", "state": "MERGED", "author": {"login": login},
            "baseRefName": "main", "mergedAt": "2026-05-02T08:00:00Z", "closedAt": "2026-05-02T08:00:00Z",
            "mergeCommit": {"oid": "b" * 40}}


if __name__ == "__main__":
    main()
