#!/usr/bin/env python3
"""Initialize a fresh clone of this repository for development.

Runs on the Ubuntu VMs this repository provisions. Every step is safe to
re-run, because agent VMs are destroyed and re-provisioned regularly.

Usage: init-dev.py
"""
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SM_HOME = Path.home() / ".skill-manager"
# sm deploys project-scoped skills into one directory per tool.
SKILL_DIRS = {"cc": Path(".claude/skills"), "codex": Path(".agents/skills")}
# Setting VIRTUAL_ENV first makes direnv's python layout use .venv instead of
# building its own venv under .direnv/.
ENVRC = 'export VIRTUAL_ENV="$PWD/.venv"\nlayout python3\n'


class InitError(Exception):
    """A step failed; the message names the cause and the fix."""


def check_platform(os_release=Path("/etc/os-release")):
    ids = set()
    if os_release.is_file():
        ids = {
            line.partition("=")[2].strip('"')
            for line in os_release.read_text().splitlines()
            if line.startswith("ID=")
        }
    if ids != {"ubuntu"}:
        raise InitError(
            f"Ubuntu required; {os_release} reports ID={ids or 'none'}."
        )
    if os.geteuid() == 0:
        raise InitError(
            "Do not run as root: sm would link skills from "
            "/root/.skill-manager."
        )


def install_skills(repo_root=REPO_ROOT, sm_home=SM_HOME):
    if shutil.which("sm") is None:
        raise InitError(
            "sm not on PATH. Provision this VM with the skill_manager role."
        )
    _require_auto_adopt_disabled(sm_home / "config.toml")
    skills = _load_manifest(repo_root / ".skills.json")
    _require_in_store(skills, sm_home / "skills")
    _refuse_tracked_collisions(skills, repo_root)
    # sm reads .skills.json from its working directory.
    subprocess.run(
        ["sm", "install"],
        cwd=repo_root,
        stdin=subprocess.DEVNULL,
        check=True,
    )
    _verify_links(skills, repo_root, sm_home / "skills")


def _require_auto_adopt_disabled(config):
    # With auto-adopt on, sm moves the repo's tracked skills into its store
    # and replaces them with symlinks.
    try:
        auto_adopt = tomllib.loads(config.read_text()).get("autoAdopt")
    except (OSError, tomllib.TOMLDecodeError) as e:
        raise InitError(
            f"Cannot read {config}: {e}. Re-run the skill_manager role."
        ) from e
    if auto_adopt is not False:
        raise InitError(
            f"{config} must set autoAdopt = false. "
            "Re-run the skill_manager role."
        )


def _load_manifest(path):
    try:
        skills = json.loads(path.read_text())["skills"]
    except (OSError, ValueError, KeyError) as e:
        raise InitError(f"Cannot read skills from {path}: {e}") from e
    for s in skills:
        if s["scope"] != "project" or not set(s["tools"]) <= SKILL_DIRS.keys():
            raise InitError(
                f"{path}: unsupported scope/tools for skill {s['name']!r}."
            )
    return skills


def _require_in_store(skills, store):
    # sm only warns and exits 0 for a skill missing from its store.
    missing = [
        s["name"] for s in skills
        if not (store / s["name"] / "SKILL.md").is_file()
    ]
    if missing:
        raise InitError(
            f"Not in {store}: {', '.join(missing)}. Run: "
            "sm install https://github.com/wonderbird/skill-factory --force"
        )


def _refuse_tracked_collisions(skills, repo_root):
    # sm deletes whatever already sits at a link path, tracked content
    # included.
    paths = [str(SKILL_DIRS[t] / s["name"]) for s in skills for t in s["tools"]]
    tracked = subprocess.run(
        ["git", "ls-files", "--", *paths],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    if tracked:
        raise InitError(
            f"Manifest skills collide with tracked files: {', '.join(tracked)}"
        )


def _verify_links(skills, repo_root, store):
    for s in skills:
        for tool in s["tools"]:
            link = repo_root / SKILL_DIRS[tool] / s["name"]
            if (not link.is_symlink()
                    or link.resolve() != (store / s["name"]).resolve()):
                raise InitError(f"{link} is not a symlink into {store}.")
            ignored = subprocess.run(
                ["git", "check-ignore", "-q", "--", str(link)],
                cwd=repo_root,
            ).returncode == 0
            if not ignored:
                raise InitError(f"{link} is not gitignored. Add it to .gitignore.")


def ensure_venv(repo_root=REPO_ROOT, python=sys.executable):
    """Create .venv unless present, check it works, return its python.

    A child process cannot activate a venv in the calling shell, so later
    steps call the returned interpreter directly.
    """
    venv = repo_root / ".venv"
    venv_python = venv / "bin" / "python"
    # lexists: a dangling .venv symlink counts as present, not as absent.
    if not os.path.lexists(venv):
        result = subprocess.run(
            [python, "-m", "venv", str(venv)],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # Only this run created it, so nothing of the user's is lost.
            shutil.rmtree(venv, ignore_errors=True)
            raise InitError(
                f"Creating {venv} failed: {result.stderr.strip()} "
                "Install the venv module: sudo apt install python3-venv"
            )
    check = subprocess.run(
        [str(venv_python), "-m", "pip", "--version"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    ) if venv_python.exists() else None
    if check is None or check.returncode != 0:
        raise InitError(
            f"{venv} exists but is unusable (no working python with pip). "
            f"Remove it and re-run: rm -rf {venv}"
        )
    return venv_python


def ensure_envrc(repo_root=REPO_ROOT):
    """Make direnv activate .venv whenever a shell enters the repository."""
    if shutil.which("direnv") is None:
        raise InitError(
            "direnv not on PATH. Provision this VM with the direnv role."
        )
    envrc = repo_root / ".envrc"
    venv = repo_root / ".venv"
    if os.path.lexists(envrc):
        # .envrc is gitignored, so a foreign one may hold the user's secrets.
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
    # Approving is safe only because the content is exactly ENVRC.
    subprocess.run(
        ["direnv", "allow", str(repo_root)],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        ["direnv", "exec", str(repo_root),
         "python", "-c", "import sys; print(sys.prefix)"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    prefix = result.stdout.strip()
    if result.returncode != 0 or Path(prefix).resolve() != venv.resolve():
        raise InitError(
            f"direnv does not activate {venv}: python in {repo_root} "
            f"reports prefix {prefix or 'none'!r}. {result.stderr.strip()}"
        )


def install_requirements(venv_python, repo_root=REPO_ROOT):
    requirements = repo_root / "requirements.txt"
    if not requirements.is_file():
        raise InitError(f"{requirements} not found.")
    # The venv's own interpreter: a bare `pip` would be whichever one the
    # calling shell happens to resolve.
    pip = [str(venv_python), "-m", "pip", "--disable-pip-version-check"]
    subprocess.run(
        [*pip, "install", "--no-input", "-r", str(requirements)],
        cwd=repo_root,
        stdin=subprocess.DEVNULL,
        check=True,
    )
    # pip install exits 0 even when it leaves conflicting versions behind.
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


def main():
    try:
        check_platform()
        install_skills()
        venv_python = ensure_venv()
        ensure_envrc()
        install_requirements(venv_python)
    except (InitError, subprocess.CalledProcessError) as e:
        print(f"init-dev: {e}", file=sys.stderr)
        return 1
    print("init-dev: repository initialized.")
    print(f"direnv activates .venv at your next prompt inside {REPO_ROOT}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
