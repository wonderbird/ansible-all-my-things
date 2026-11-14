"""Deploy the skills listed in .skills.json into the clone via sm."""
import json
import shutil
import subprocess
import tomllib
from pathlib import Path

from .common import REPO_ROOT, InitError

SM_HOME = Path.home() / ".skill-manager"
SKILL_DIRS = {"cc": Path(".claude/skills"), "codex": Path(".agents/skills")}


def install(repo_root=REPO_ROOT, sm_home=SM_HOME):
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
