"""Classify delivered work and aggregate counts for the flow first look (plan Step 2).

Reads raw/prs.json, raw/merges.json and raw/direct.json and writes counts.json.
The rules are the owner decisions 1-7 and the planner defaults D1-D9 of
.omc/plans/flow-first-look-plan.md. Throwaway script; it is never committed.
"""

import json
import math
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"

CUTOFF = datetime(2026, 4, 1, tzinfo=timezone.utc)
FULL_MONTHS = ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
PARTIAL_MONTH = "2026-11"
ABSORBED = {94: 95, 113: 112}
MIN_READABLE_N = 5
RUN_LENGTH = 6

AUTHOR_TYPES = {
    "eudicy": "agent",
    "Eudicy": "agent",
    "galadriel": "agent",
    "wonderbird": "manual",
    "stefanboos": "manual",
    "Stefan Boos": "manual",
    "app/dependabot": "automated",
    "dependabot[bot]": "automated",
}

LAB_DIRS = {".claude/", ".specify/", ".clinerules/", ".cursor/", ".omc/", ".codex/", ".agents/", ".rtk/"}
LAB_FILES = {"AGENTS.md", "CLAUDE.md", ".skills.json", "skills-lock.json"}
NEUTRAL_DIRS = {"docs/", "specs/", ".beads/"}
NEUTRAL_FILES = {"README.md", "CHANGELOG.md", ".gitignore", "beads-backup.jsonl", "beads_export.jsonl"}

REWORK_PATTERN = re.compile(r"^(fix|bug|revert)\b", re.IGNORECASE)
CHORE_PATTERN = re.compile(r"^chore(\(.+\))?!?:")
BUMP_PATTERN = re.compile(r"^(deps|build\(deps\)|chore\(deps\))\b", re.IGNORECASE)
MERGE_SUBJECT_PATTERN = re.compile(r"^Merge pull request #(\d+)\b")


class GuardError(Exception):
    """A fail-loud guard stopped the classification."""


def main():
    prs = json.loads((RAW / "prs.json").read_text())
    merges = json.loads((RAW / "merges.json").read_text())
    direct = json.loads((RAW / "direct.json").read_text())
    counts = build_counts(prs, merges, direct)
    (HERE / "counts.json").write_text(json.dumps(counts, indent=1) + "\n")
    print(f"delivered PRs {counts['totals']['delivered_prs']}, direct commits {counts['totals']['delivered_direct']}, "
          f"discarded {counts['totals']['discarded']}, closed Dependabot {counts['totals']['closed_dependabot']}")


# ---------------------------------------------------------------- rules


def utc(timestamp):
    """Parse an ISO 8601 timestamp with offset or Z into an aware UTC datetime."""
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(timezone.utc)


def month_of(timestamp):
    return utc(timestamp).strftime("%Y-%m")


def in_scope(timestamp):
    return utc(timestamp) >= CUTOFF


def author_type(identity):
    if identity not in AUTHOR_TYPES:
        raise GuardError(f"author map: unknown identity {identity!r}")
    return AUTHOR_TYPES[identity]


def top_level(path):
    parts = path.split("/", 1)
    return parts[0] + "/" if len(parts) == 2 else parts[0]


def path_class(path):
    top = top_level(path)
    # memory-bank*/ is machines: the owner ruled on 2026-11-20 that it held planning
    # and documentation for machine work, so it falls to the machines default.
    if top in LAB_DIRS or top in LAB_FILES:
        return "lab"
    if top in NEUTRAL_DIRS or top in NEUTRAL_FILES:
        return "neutral"
    return "machines"


def path_vote(files):
    lab = machines = 0
    default_paths = set()
    for path in files:
        kind = path_class(path)
        if kind == "lab":
            lab += 1
        elif kind == "machines":
            machines += 1
            default_paths.add(top_level(path))
    voting = lab + machines
    vote = "lab" if lab > machines else "machines"
    mixed = voting != 0 and max(lab, machines) / voting < 2 / 3
    return {
        "vote": vote,
        "lab": lab,
        "machines": machines,
        "mixed": mixed,
        "neutral_only": voting == 0,
        "default_paths": sorted(default_paths),
    }


def category(kind_of_author, title, files):
    """Return (category, path vote). First match wins: automated, rework, path vote."""
    vote = path_vote(files)
    if kind_of_author == "automated":
        return "automated", vote
    if REWORK_PATTERN.match(title) is not None:
        return "rework", vote
    return vote["vote"], vote


def direct_exclusion(subject, files):
    if files != [] and all(path.startswith(".beads/") for path in files):
        return "beads-only"
    if CHORE_PATTERN.match(subject) is not None:
        return "chore"
    return None


def is_bump(title):
    return BUMP_PATTERN.match(title) is not None or title.strip().lower() == "update versions"


def check_absorbed(merged_in_scope, merge_numbers):
    without_own_merge = set(merged_in_scope) - set(merge_numbers)
    if without_own_merge != set(ABSORBED):
        raise GuardError(
            f"{{94, 113}} assertion: merged PRs without their own first-parent merge are "
            f"{sorted(without_own_merge)}, expected {sorted(ABSORBED)}; ask the owner before fetching"
        )


def check_merge_subjects(merges, merged_numbers):
    numbers = []
    for merge in merges:
        match = MERGE_SUBJECT_PATTERN.match(merge["subject"])
        if match is None:
            raise GuardError(f"merge-subject assertion: {merge['sha'][:7]} is not a PR merge: {merge['subject']!r}")
        number = int(match.group(1))
        if number not in merged_numbers:
            raise GuardError(f"merge-subject assertion: {merge['sha'][:7]} names #{number}, which is not a MERGED PR")
        numbers.append(number)
    return numbers


def p_chart(points):
    """Judge a share series as a p-chart. points: list of (month, numerator, base)."""
    readable = [(month, num, n) for month, num, n in points if n >= MIN_READABLE_N]
    flagged = [month for month, _, n in points if n < MIN_READABLE_N]
    total_n = sum(n for _, _, n in readable)
    if total_n == 0:
        return {"p_bar": None, "months": [], "flagged": flagged, "signals": [], "run_rule_possible": False,
                "verdict": "no readable month"}
    p_bar = sum(num for _, num, _ in readable) / total_n

    # Per-month limits and points outside them
    months = []
    signals = []
    for month, num, n in readable:
        sigma = math.sqrt(p_bar * (1 - p_bar) / n)
        lower = max(0.0, p_bar - 3 * sigma)
        upper = min(1.0, p_bar + 3 * sigma)
        share = num / n
        outside = share < lower or share > upper
        months.append({"month": month, "num": num, "n": n, "share": share, "lower": lower, "upper": upper,
                       "outside": outside})
        if outside:
            signals.append(f"{month} outside limits ({share:.0%} vs {lower:.0%}..{upper:.0%})")

    # Run rule: RUN_LENGTH consecutive rises or falls needs RUN_LENGTH + 1 readable months
    run_rule_possible = len(readable) >= RUN_LENGTH + 1
    shares = [entry["share"] for entry in months]
    rises = falls = 0
    for previous, current in zip(shares, shares[1:], strict=False):
        rises = rises + 1 if current > previous else 0
        falls = falls + 1 if current < previous else 0
        if rises >= RUN_LENGTH or falls >= RUN_LENGTH:
            signals.append(f"{RUN_LENGTH} consecutive {'rises' if rises >= RUN_LENGTH else 'falls'}")
            break

    verdict = "signal: " + "; ".join(signals) if signals != [] else "no signal"
    return {"p_bar": p_bar, "months": months, "flagged": flagged, "signals": signals,
            "run_rule_possible": run_rule_possible, "verdict": verdict}


# ---------------------------------------------------------------- aggregation


def build_counts(prs, merges, direct):
    prs_by_number = {pr["number"]: pr for pr in prs}
    merged_in_scope = [pr["number"] for pr in prs if pr["state"] == "MERGED" and in_scope(pr["mergedAt"])]
    merged_numbers = {pr["number"] for pr in prs if pr["state"] == "MERGED"}

    # Guards before any counting
    scoped_merges = [merge for merge in merges if in_scope(merge["committed"])]
    merge_numbers = check_merge_subjects(scoped_merges, merged_numbers)
    check_absorbed(merged_in_scope, merge_numbers)

    # Delivered PR items
    items = []
    for merge, number in zip(scoped_merges, merge_numbers, strict=True):
        pr = prs_by_number[number]
        opener_type = author_type(pr["author"]["login"])
        commit_types = Counter(author_type(name) for name in merge["commit_authors"])
        kind, vote = category(opener_type, pr["title"], merge["files"])
        items.append({
            "channel": "PR", "id": f"#{number}", "month": month_of(merge["committed"]), "title": pr["title"],
            "author_type": opener_type, "commit_author_types": dict(commit_types), "category": kind,
            "commit_count": merge["commit_count"], "bump": is_bump(pr["title"]), **vote,
        })

    # Delivered direct commits
    excluded = Counter()
    for commit in direct:
        if not in_scope(commit["committed"]):
            continue
        reason = direct_exclusion(commit["subject"], commit["files"])
        if reason is not None:
            excluded[reason] += 1
            continue
        commit_type = author_type(commit["author"])
        kind, vote = category(commit_type, commit["subject"], commit["files"])
        items.append({
            "channel": "direct", "id": commit["sha"][:7], "month": month_of(commit["committed"]),
            "title": commit["subject"], "author_type": commit_type, "commit_author_types": {commit_type: 1},
            "category": kind, "commit_count": 1, "bump": is_bump(commit["subject"]), **vote,
        })

    # Discarded: closed unmerged PRs, Dependabot kept apart
    discarded = []
    for pr in prs:
        if pr["state"] != "CLOSED" or not in_scope(pr["closedAt"]):
            continue
        discarded.append({"id": f"#{pr['number']}", "month": month_of(pr["closedAt"]), "title": pr["title"],
                          "author_type": author_type(pr["author"]["login"])})

    return _aggregate(items, discarded, excluded)


def _aggregate(items, discarded, excluded):
    months = FULL_MONTHS + [PARTIAL_MONTH]

    # Month x category, with the D8 base n (non-automated delivered items)
    month_category = {month: Counter() for month in months}
    for item in items:
        month_category[item["month"]][item["category"]] += 1
    month_rows = {}
    for month in months:
        row = month_category[month]
        base = row["machines"] + row["lab"] + row["rework"]
        month_rows[month] = {"machines": row["machines"], "lab": row["lab"], "rework": row["rework"],
                             "automated": row["automated"], "base_n": base}

    # Month x five author segments
    segments = {month: Counter() for month in months}
    for item in items:
        segments[item["month"]][f"{item['author_type']} {item['channel']}"] += 1

    # Discarded per month
    discarded_rows = {month: Counter() for month in months}
    for entry in discarded:
        key = "closed_dependabot" if entry["author_type"] == "automated" else "discarded"
        discarded_rows[entry["month"]][key] += 1

    # Category x author, rework split, bumps
    category_author = defaultdict(Counter)
    rework_split = Counter()
    bumps = Counter()
    for item in items:
        category_author[item["category"]][item["author_type"]] += 1
        if item["category"] == "rework":
            rework_split[item["vote"]] += 1
        if item["bump"]:
            bumps[item["author_type"]] += 1

    # Median commits per delivered non-Dependabot PR per month
    medians = {}
    for month in months:
        sizes = [item["commit_count"] for item in items
                 if item["month"] == month and item["channel"] == "PR" and item["author_type"] != "automated"]
        medians[month] = statistics.median(sizes) if sizes != [] else None

    # D8 share series on fixed bases, full months only
    def series(numerator, base):
        points = []
        for month in FULL_MONTHS:
            in_base = [item for item in items if item["month"] == month and base(item)]
            points.append((month, sum(1 for item in in_base if numerator(item)), len(in_base)))
        return p_chart(points)

    def non_automated(item):
        return item["author_type"] != "automated"

    d8 = {
        "rework_share": series(lambda item: item["category"] == "rework", non_automated),
        "manual_share": series(lambda item: item["author_type"] == "manual", non_automated),
        "agent_rework_share": series(lambda item: item["category"] == "rework",
                                     lambda item: item["author_type"] == "agent"),
    }

    # Diagnostics
    default_paths = Counter(path for item in items for path in item["default_paths"])
    disagreements = [
        {"id": item["id"], "opener": item["author_type"], "commit_authors": item["commit_author_types"]}
        for item in items
        if item["channel"] == "PR" and set(item["commit_author_types"]) != {item["author_type"]}
    ]
    delivered_prs = sum(1 for item in items if item["channel"] == "PR")
    return {
        "months": months,
        "partial_month": PARTIAL_MONTH,
        "month_category": month_rows,
        "month_segments": {month: dict(segments[month]) for month in months},
        "month_discarded": {month: dict(discarded_rows[month]) for month in months},
        "category_author": {kind: dict(row) for kind, row in category_author.items()},
        "rework_split": dict(rework_split),
        "bumps_by_author": dict(bumps),
        "median_commits_per_pr": medians,
        "d8": d8,
        "diagnostics": {
            "mixed": sum(1 for item in items if item["mixed"]),
            "neutral_only": sum(1 for item in items if item["neutral_only"]),
            "default_machines_paths": dict(default_paths.most_common()),
            "opener_commit_disagreements": disagreements,
            "direct_excluded": dict(excluded),
        },
        "absorbed": {f"#{number}": f"#{into}" for number, into in ABSORBED.items()},
        "totals": {
            "delivered_prs": delivered_prs,
            "delivered_direct": len(items) - delivered_prs,
            "discarded": sum(1 for entry in discarded if entry["author_type"] != "automated"),
            "closed_dependabot": sum(1 for entry in discarded if entry["author_type"] == "automated"),
        },
        "items": items,
        "discarded_items": discarded,
    }


if __name__ == "__main__":
    main()
