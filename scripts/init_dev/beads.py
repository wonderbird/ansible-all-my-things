"""Set up the beads issue tracker and load the tracked issues into it."""

import shutil
import subprocess
from pathlib import Path

from .common import REPO_ROOT, InitError


def ensure(repo_root=REPO_ROOT):
    # Require bd from the VM provisioning, and the tracked .beads files.
    if shutil.which("bd") is None:
        raise InitError("bd not on PATH. Provision this VM with the beads_go role.")
    beads_dir = repo_root / ".beads"
    issues = beads_dir / "issues.jsonl"
    tracked_files = [issues, beads_dir / "config.yaml", beads_dir / "metadata.json"]
    missing = [str(path) for path in tracked_files if not path.is_file()]
    if len(missing) > 0:
        raise InitError(
            f"Not found: {', '.join(missing)}. "
            "Restore them from git: git checkout -- .beads/"
        )

    # Restrict .beads to its owner, as bd demands. A clone creates it with
    # the default permissions.
    beads_dir.chmod(0o700)

    # Create the embedded database. Stealth mode installs no git hooks, and
    # --init-if-missing lets a second run pass an existing database.
    _bd(repo_root, "init", "--stealth", "--init-if-missing", "--non-interactive")

    # Stealth mode excludes all of .beads/ from git, which overrides the
    # .gitignore exceptions that keep the .beads files tracked.
    _remove_beads_exclude(repo_root)

    # Verify that git sees every tracked file.
    ignored = [str(path) for path in tracked_files if _git_ignores(repo_root, path)]
    if len(ignored) > 0:
        raise InitError(
            f"git does not track {', '.join(ignored)}. Check .gitignore and "
            "the exclude file in the git directory."
        )

    # Load the tracked issues. An import keeps local edits that are newer.
    _bd(repo_root, "import", str(issues))


def _git_ignores(repo_root, path):
    # check-ignore exits 0 for an ignored path and 1 for a path that no rule
    # ignores. Any other code means git itself failed.
    result = subprocess.run(
        ["git", "check-ignore", "-q", "--no-index", "--", str(path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise InitError(
            f"git check-ignore failed for {path} with exit code "
            f"{result.returncode}: {result.stderr.strip()}"
        )
    return result.returncode == 0


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
