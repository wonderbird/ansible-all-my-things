"""Install the Ansible Galaxy content listed in requirements.yml."""

import subprocess

from .common import REPO_ROOT, InitError


def install(venv_python, repo_root=REPO_ROOT):
    # Require the requirements file.
    requirements = repo_root / "requirements.yml"
    if not requirements.is_file():
        raise InitError(f"{requirements} not found.")

    # Install with the venv's ansible-galaxy: a system-wide one may belong to
    # another ansible-core version. The repository root as working directory
    # makes ansible.cfg apply.
    galaxy = venv_python.parent / "ansible-galaxy"
    subprocess.run(
        [str(galaxy), "install", "-r", str(requirements)],
        cwd=repo_root,
        stdin=subprocess.DEVNULL,
        check=True,
    )
