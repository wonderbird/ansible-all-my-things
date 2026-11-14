"""Run every initialization step in order; see the package docstring."""
import subprocess
import sys

from . import direnv_envrc, pip_requirements, platform_check, python_venv, skills
from .common import REPO_ROOT, InitError


def main():
    try:
        platform_check.check()
        skills.install()
        venv_python = python_venv.ensure()
        direnv_envrc.ensure()
        pip_requirements.install(venv_python)
    except (InitError, subprocess.CalledProcessError) as e:
        print(f"init-dev: {e}", file=sys.stderr)
        return 1
    print("init-dev: repository initialized.")
    print(f"direnv activates .venv at your next prompt inside {REPO_ROOT}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
