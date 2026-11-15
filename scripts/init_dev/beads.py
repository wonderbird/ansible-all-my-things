"""Set up the beads issue tracker and load the tracked issues into it."""

import shutil
import subprocess
from pathlib import Path

from .common import REPO_ROOT, InitError


def ensure(repo_root=REPO_ROOT):
    # Require bd from the VM provisioning, and the tracked issues.
    if shutil.which("bd") is None:
        raise InitError("bd not on PATH. Provision this VM with the beads_go role.")
    beads_dir = repo_root / ".beads"
    issues = beads_dir / "issues.jsonl"
    if not issues.is_file():
        raise InitError(f"{issues} not found.")

    # Restrict .beads to its owner, as bd demands. A clone creates it with
    # the default permissions.
    beads_dir.chmod(0o700)

    # Create the embedded database. Stealth mode installs no git hooks, and
    # --init-if-missing lets a second run pass an existing database.
    _bd(repo_root, "init", "--stealth", "--init-if-missing", "--non-interactive")

    # Stealth mode excludes all of .beads/ from git, which overrides the
    # .gitignore exception that keeps issues.jsonl tracked.
    _remove_beads_exclude(repo_root)

    # Verify that git sees issues.jsonl. check-ignore exits 1 for a path
    # that no rule ignores.
    visible_to_git = (
        subprocess.run(
            ["git", "check-ignore", "-q", "--no-index", "--", str(issues)],
            cwd=repo_root,
            check=False,
        ).returncode
        == 1
    )
    if not visible_to_git:
        raise InitError(
            f"git does not track {issues}. Check .gitignore and "
            "the exclude file in the git directory."
        )

    # Load the tracked issues. An import keeps local edits that are newer.
    _bd(repo_root, "import", str(issues))


def _bd(repo_root, *args):
    subprocess.run(
        ["bd", *args],
        cwd=repo_root,
        stdin=subprocess.DEVNULL,
        check=True,
    )


def _remove_beads_exclude(repo_root):
    # The git directory of a worktree is not .git, so ask git for the path.
    exclude = repo_root / Path(
        subprocess.run(
            ["git", "rev-parse", "--git-path", "info/exclude"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )
    if not exclude.is_file():
        return

    lines = exclude.read_text().splitlines(keepends=True)
    kept = [line for line in lines if line.rstrip("\n") != ".beads/"]
    if kept != lines:
        exclude.write_text("".join(kept))
