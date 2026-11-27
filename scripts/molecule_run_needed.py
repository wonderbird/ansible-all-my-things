# SPDX-License-Identifier: MIT-0
"""Print whether Molecule CI must run the full suite for a change.

Prints `true` when any changed file is outside the skip list, `false` when
every changed file is on it. The skip list names paths that no Molecule
scenario reads. Any other path runs the full suite, so coupling that nobody
listed fails safe.
"""

import argparse
import subprocess
import sys
from typing import Final

# Directory prefixes, each ending in "/".
_SKIPPED_DIRECTORIES: Final = (
    ".agents/",
    ".beads/",
    ".claude/",
    ".codex/",
    ".devcontainer/",
    ".github/",
    ".omc/",
    ".rtk/",
    ".specify/",
    "docs/",
    "role-template/",
    "specs/",
)
_SKIPPED_FILES: Final = frozenset(
    {
        ".gitignore",
        # Binary used by the Docker workflow.
        "container-structure-test-linux-arm64",
        ".markdownlint.json",
        ".pre-commit-config.yaml",
        ".shellcheckrc",
        ".skills.json",
        "LICENSE",
        "ruff.toml",
        "skills-lock.json",
    }
)
# The workflow runs the suite, so it sits inside a skipped directory but
# must still trigger it.
_ALWAYS_TESTED: Final = frozenset({".github/workflows/molecule.yml"})


def is_skipped(path: str) -> bool:
    """Return whether a change to `path` (relative to the repository root)
    cannot affect any Molecule scenario."""
    if path in _ALWAYS_TESTED:
        return False
    if path in _SKIPPED_FILES or path.startswith(_SKIPPED_DIRECTORIES):
        return True
    # Markdown inside a role can be a runtime asset, for example a template.
    return path.endswith(".md") and not path.startswith("roles/")


def _changed_files(base: str) -> list[str]:
    # --no-renames lists both sides of a rename, so a file moved out of
    # roles/ still counts as a change to roles/.
    diff = subprocess.run(
        ["git", "diff", "--name-only", "--no-renames", "-z", base, "HEAD", "--"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [path for path in diff.stdout.split("\0") if path != ""]


def main(argv: list[str] | None = None) -> int:
    # Read the base commit to compare with HEAD.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        help="Compare this commit with HEAD. Without it, the full suite runs.",
    )
    args = parser.parse_args(argv)

    # Without a base there is no diff to judge, so run everything.
    if args.base is None:
        print("No base commit; running the full Molecule suite.", file=sys.stderr)
        print("true")
        return 0

    # List the changed files; a git failure ends the run.
    try:
        changed = _changed_files(args.base)
    except subprocess.CalledProcessError as e:
        print(
            f"molecule_run_needed: {e} Check that --base names a commit "
            "in this clone; a shallow checkout may need a deeper fetch-depth.",
            file=sys.stderr,
        )
        print(e.stderr, file=sys.stderr)
        return 1

    # Report the files that trigger the run, so the log explains the decision.
    relevant = [path for path in changed if not is_skipped(path)]
    if len(changed) == 0:
        print("No changed files; skipping Molecule.", file=sys.stderr)
        print("false")
    elif len(relevant) > 0:
        print("Molecule-relevant changes:", file=sys.stderr)
        for path in relevant:
            print(f"  {path}", file=sys.stderr)
        print("true")
    else:
        print(
            f"All {len(changed)} changed files are on the skip list; "
            "skipping Molecule.",
            file=sys.stderr,
        )
        print("false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
