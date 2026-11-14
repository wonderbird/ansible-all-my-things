"""Make direnv activate .venv whenever a shell enters the repository."""

import os
import shutil
import subprocess
from pathlib import Path

from .common import REPO_ROOT, InitError

# Setting VIRTUAL_ENV first makes direnv's python layout use .venv instead of
# building its own venv under .direnv/.
ENVRC = 'export VIRTUAL_ENV="$PWD/.venv"\nlayout python3\n'


def ensure(repo_root=REPO_ROOT):
    # Require direnv from the VM provisioning.
    if shutil.which("direnv") is None:
        raise InitError("direnv not on PATH. Provision this VM with the direnv role.")

    # Write .envrc, but never replace a foreign one: .envrc is gitignored,
    # so it may hold the user's secrets.
    envrc = repo_root / ".envrc"
    if os.path.lexists(envrc):
        try:
            foreign = envrc.read_text() != ENVRC
        except OSError:
            foreign = True
        if foreign:
            raise InitError(
                f"{envrc} exists with content this script did not write. "
                f"Remove it, or replace its content with:\n{ENVRC}"
            )
    else:
        envrc.write_text(ENVRC)

    # Approve .envrc. This is safe only because its content is exactly ENVRC.
    subprocess.run(
        ["direnv", "allow", str(repo_root)],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=True,
    )

    # Verify that a python started through direnv runs from .venv.
    venv = repo_root / ".venv"
    result = subprocess.run(
        [
            "direnv",
            "exec",
            str(repo_root),
            "python",
            "-c",
            "import sys; print(sys.prefix)",
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )
    prefix = result.stdout.strip()
    if result.returncode != 0 or Path(prefix).resolve() != venv.resolve():
        raise InitError(
            f"direnv does not activate {venv}: python in {repo_root} "
            f"reports prefix {prefix or 'none'!r}. {result.stderr.strip()}"
        )
