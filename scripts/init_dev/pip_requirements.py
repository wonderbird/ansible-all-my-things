"""Install requirements.txt into the venv."""
import subprocess

from .common import REPO_ROOT, InitError


def install(venv_python, repo_root=REPO_ROOT):
    # Require the requirements file.
    requirements = repo_root / "requirements.txt"
    if not requirements.is_file():
        raise InitError(f"{requirements} not found.")

    # Install through the venv's own interpreter: a bare `pip` would be
    # whichever one the calling shell happens to resolve.
    pip = [str(venv_python), "-m", "pip", "--disable-pip-version-check"]
    subprocess.run(
        [*pip, "install", "--no-input", "-r", str(requirements)],
        cwd=repo_root,
        stdin=subprocess.DEVNULL,
        check=True,
    )

    # Verify the installed versions: pip install exits 0 even when it leaves
    # conflicting versions behind.
    check = subprocess.run(
        [*pip, "check"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    if check.returncode != 0:
        raise InitError(
            f"Conflicting packages in {venv_python.parent.parent}:\n"
            f"{check.stdout.strip()}"
        )
