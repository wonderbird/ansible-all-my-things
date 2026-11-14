import subprocess
import sys

from . import (
    direnv_envrc,
    pip_requirements,
    platform_check,
    python_venv,
    skills,
    user_check,
)
from .common import REPO_ROOT, InitError


def main():
    # Run the steps in the order of their prerequisites. Stop at the first
    # failure.
    try:
        platform_check.check()
        user_check.check()
        skills.install()
        venv_python = python_venv.ensure()
        direnv_envrc.ensure()
        pip_requirements.install(venv_python)
    except (InitError, subprocess.CalledProcessError) as e:
        print(f"init-dev: {e}", file=sys.stderr)
        return 1

    # Tell the user how the venv becomes active in their shell.
    print("init-dev: repository initialized.")
    print(f"direnv activates .venv at your next prompt inside {REPO_ROOT}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
