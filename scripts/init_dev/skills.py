"""Deploy the skills listed in .skills.json into the clone via sm."""

import json
import shutil
import subprocess
import tomllib
from pathlib import Path

from .common import REPO_ROOT, InitError

SM_HOME = Path.home() / ".skill-manager"
# Keys are sm's tool ids in .skills.json: cc is Claude Code.
SKILL_DIRS = {"cc": Path(".claude/skills"), "codex": Path(".agents/skills")}


def install(repo_root=REPO_ROOT, sm_home=SM_HOME):
    # Require sm from the VM provisioning.
    if shutil.which("sm") is None:
        raise InitError(
            "sm not on PATH. Provision this VM with the skill_manager role."
        )

    # Check every precondition before sm changes anything.
    _require_auto_adopt_disabled(sm_home / "config.toml")
    skills = _load_manifest(repo_root / ".skills.json")
    _require_in_store(skills, sm_home / "skills")
    _refuse_tracked_collisions(skills, repo_root)

    # Deploy the skills. sm reads .skills.json from its working directory.
    subprocess.run(
        ["sm", "install"],
        cwd=repo_root,
        stdin=subprocess.DEVNULL,
        check=True,
    )

    # Verify the outcome, because sm reports some failures only as warnings.
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
            f"{config} must set autoAdopt = false. Re-run the skill_manager role."
        )


def _load_manifest(path):
    # Read the skill list.
    try:
        skills = json.loads(path.read_text())["skills"]
    except (OSError, ValueError, KeyError) as e:
        raise InitError(f"Cannot read skills from {path}: {e}") from e

    # Accept only skills this step knows where to link.
    for skill in skills:
        if skill["scope"] != "project" or not set(skill["tools"]) <= SKILL_DIRS.keys():
            raise InitError(
                f"{path}: unsupported scope/tools for skill {skill['name']!r}."
            )
    return skills


def _require_in_store(skills, store):
    # sm only warns and exits 0 for a skill missing from its store.
    missing = [
        skill["name"]
        for skill in skills
        if not (store / skill["name"] / "SKILL.md").is_file()
    ]
    if missing:
        raise InitError(
            f"Not in {store}: {', '.join(missing)}. Run: "
            "sm install https://github.com/wonderbird/skill-factory --force"
        )


def _refuse_tracked_collisions(skills, repo_root):
    # sm deletes whatever already sits at a link path, tracked content
    # included.
    paths = [
        str(SKILL_DIRS[tool] / skill["name"])
        for skill in skills
        for tool in skill["tools"]
    ]
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
    for skill in skills:
        for tool in skill["tools"]:
            # Require a symlink into the store.
            link = repo_root / SKILL_DIRS[tool] / skill["name"]
            if (
                not link.is_symlink()
                or link.resolve() != (store / skill["name"]).resolve()
            ):
                raise InitError(f"{link} is not a symlink into {store}.")

            # Require git to ignore it, so the link is never committed.
            ignored = (
                subprocess.run(
                    ["git", "check-ignore", "-q", "--", str(link)],
                    cwd=repo_root,
                    check=False,
                ).returncode
                == 0
            )
            if not ignored:
                raise InitError(f"{link} is not gitignored. Add it to .gitignore.")
