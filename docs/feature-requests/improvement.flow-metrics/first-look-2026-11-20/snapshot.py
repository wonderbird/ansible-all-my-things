"""Snapshot the raw inputs of the flow first look (plan Step 1).

Reads git at the snapshot SHA recorded in raw/snapshot-ref.txt and the live
GitHub PR list, and writes raw/prs.json, raw/merges.json and raw/direct.json.
Throwaway script for one look; it is never committed.
"""

import json
import subprocess
from pathlib import Path

REPO = Path("/home/galadriel/Documents/Cline/ansible-all-my-things")
RAW = Path(__file__).resolve().parent / "raw"
CUTOFF = "2026-04-01T00:00:00Z"
GH_LIMIT = 1000
PR_FIELDS = "number,title,state,author,baseRefName,mergedAt,closedAt,mergeCommit"


def main():
    snapshot_sha = _read_snapshot_sha()

    # GitHub PR metadata
    prs = json.loads(
        _run(["gh", "pr", "list", "--state", "all", "--limit", str(GH_LIMIT), "--json", PR_FIELDS])
    )
    if len(prs) >= GH_LIMIT:
        raise SystemExit(f"gh limit assertion: {len(prs)} PRs reached --limit {GH_LIMIT}; result may be truncated")
    _write("prs.json", prs)

    # First-parent merges with their files, commit count and commit authors
    merges = [_describe_merge(line) for line in _first_parent_lines(snapshot_sha, "--merges")]
    _write("merges.json", merges)

    # First-parent direct commits with their files
    _write("direct.json", _direct_commits(snapshot_sha))
    print(f"snapshot {snapshot_sha}: {len(prs)} PRs, {len(merges)} merges written to {RAW}")


def _read_snapshot_sha():
    first_line = (RAW / "snapshot-ref.txt").read_text().splitlines()[0]
    return first_line.split()[0]


def _first_parent_lines(snapshot_sha, merge_flag):
    output = _run(
        ["git", "log", "--first-parent", merge_flag, f"--since={CUTOFF}", "--format=%H%x09%cI%x09%an%x09%s", snapshot_sha]
    )
    return [line for line in output.splitlines() if line != ""]


def _describe_merge(line):
    sha, committed, author, subject = line.split("\t", 3)
    files = _run(["git", "diff", "--name-only", f"{sha}^1", sha]).splitlines()
    commit_count = int(_run(["git", "rev-list", "--no-merges", "--count", f"{sha}^1..{sha}^2"]).strip())
    commit_authors = _run(["git", "log", "--no-merges", "--format=%an", f"{sha}^1..{sha}^2"]).splitlines()
    return {
        "sha": sha,
        "committed": committed,
        "author": author,
        "subject": subject,
        "files": files,
        "commit_count": commit_count,
        "commit_authors": commit_authors,
    }


def _direct_commits(snapshot_sha):
    output = _run(
        [
            "git", "log", "--first-parent", "--no-merges", f"--since={CUTOFF}",
            "--format=@@%H%x09%cI%x09%an%x09%s", "--name-only", snapshot_sha,
        ]
    )
    commits = []
    for block in output.split("@@")[1:]:
        lines = [line for line in block.strip().split("\n") if line != ""]
        sha, committed, author, subject = lines[0].split("\t", 3)
        commits.append({"sha": sha, "committed": committed, "author": author, "subject": subject, "files": lines[1:]})
    return commits


def _write(name, data):
    (RAW / name).write_text(json.dumps(data, indent=1) + "\n")


def _run(command):
    return subprocess.run(command, cwd=REPO, capture_output=True, text=True, check=True).stdout


if __name__ == "__main__":
    main()
