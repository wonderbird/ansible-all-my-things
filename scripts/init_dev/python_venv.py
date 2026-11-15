"""Provide a working .venv in the clone."""

import os
import shutil
import subprocess
import sys

from .common import REPO_ROOT, InitError


def ensure(repo_root=REPO_ROOT, python=sys.executable):
    """Create .venv unless present, check it works, return its python.

    A child process cannot activate a venv in the calling shell, so later
    steps call the returned interpreter directly.
    """
    # Create .venv unless present. lexists: a dangling .venv symlink counts
    # as present, not as absent.
    venv = repo_root / ".venv"
    if not os.path.lexists(venv):
        result = subprocess.run(
            [python, "-m", "venv", str(venv)],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            # Only this run created it, so nothing of the user's is lost.
            shutil.rmtree(venv, ignore_errors=True)
            raise InitError(
                f"Creating {venv} failed: {result.stderr.strip()} "
                "Install the venv module: sudo apt install python3-venv"
            )

    # Verify that the venv, new or existing, has a python with pip.
    venv_python = venv / "bin" / "python"
    check = (
        subprocess.run(
            [str(venv_python), "-m", "pip", "--version"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )
        if venv_python.exists()
        else None
    )
    if check is None or check.returncode != 0:
        raise InitError(
            f"{venv} exists but is unusable (no working python with pip). "
            f"Remove it and re-run: rm -rf {venv}"
        )
    return venv_python
