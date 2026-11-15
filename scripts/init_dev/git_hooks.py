"""Install the pre-commit git hooks into the clone."""

import subprocess

from .common import REPO_ROOT


def install(venv_python, repo_root=REPO_ROOT):
    # Install the hooks and their environments now, so a missing network
    # shows up here instead of at the first commit. pre-commit comes from
    # requirements.txt, so the venv's interpreter runs it.
    subprocess.run(
        [str(venv_python), "-m", "pre_commit", "install", "--install-hooks"],
        cwd=repo_root,
        stdin=subprocess.DEVNULL,
        check=True,
    )
