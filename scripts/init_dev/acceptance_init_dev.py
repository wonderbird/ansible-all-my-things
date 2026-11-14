"""End-to-end check of init_dev's promise on a provisioned VM.

Runs the real script twice on a fresh copy of the working tree, with the
real sm, direnv, venv and pip, and checks the outcomes. Needs network and
takes about half a minute, so the name keeps it out of the default test
run; see README.md for the command.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from .common import REPO_ROOT


class InitDevAcceptanceTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.clone = copy_working_tree(Path(tmp.name) / "clone")
        self.env = isolated_env(home=Path(tmp.name) / "home")

    def test_prepares_clone_and_can_run_again(self):
        # Run twice: the second run proves that init_dev is re-runnable.
        self.run_init_dev()
        self.run_init_dev()

        # Check each outcome init_dev promises.
        self.assert_skills_deployed()
        self.assert_direnv_activates_venv()
        self.assert_venv_provides_requirements()
        self.assert_nothing_left_to_commit()
        self.assert_commit_runs_ruff()

    def assert_skills_deployed(self):
        manifest = json.loads((self.clone / ".skills.json").read_text())
        for skill in manifest["skills"]:
            skill_file = self.clone / ".claude/skills" / skill["name"] / "SKILL.md"
            self.assertTrue(skill_file.is_file(), f"skill {skill['name']} not deployed")

    def assert_direnv_activates_venv(self):
        prefix = self.in_direnv("python", "-c", "import sys; print(sys.prefix)")
        self.assertEqual(
            Path(prefix.stdout.strip()).resolve(),
            (self.clone / ".venv").resolve(),
            prefix.stderr,
        )

    def assert_venv_provides_requirements(self):
        # An import through the venv's python, not `ansible --version`: the
        # VM may also have a system-wide ansible on PATH.
        ansible = self.in_direnv("python", "-c", "import ansible")
        self.assertEqual(ansible.returncode, 0, ansible.stderr)

    def assert_nothing_left_to_commit(self):
        untracked = self.run_in_clone(
            "git", "ls-files", "--others", "--exclude-standard"
        )
        modified = self.run_in_clone("git", "diff", "--name-only")
        self.assertEqual(
            untracked.stdout + modified.stdout,
            "",
            "initialization left files git would commit",
        )

    def assert_commit_runs_ruff(self):
        # Stage a script that ruff would reformat, then try to commit it.
        (self.clone / "scripts/unformatted.py").write_text("x=1\n")
        self.run_in_clone("git", "add", "scripts/unformatted.py")
        commit = self.run_in_clone(
            "git",
            "-c",
            "user.name=init_dev",
            "-c",
            "user.email=init_dev@example.invalid",
            "commit",
            "-m",
            "unformatted",
        )

        # The pre-commit hook rejects the commit.
        self.assertNotEqual(commit.returncode, 0, "commit bypassed the hook")
        self.assertIn("ruff", commit.stdout + commit.stderr)

    def run_init_dev(self):
        result = self.run_in_clone(sys.executable, "-m", "scripts.init_dev")
        self.assertEqual(
            result.returncode, 0, f"init_dev failed:\n{result.stdout}{result.stderr}"
        )

    def in_direnv(self, *cmd):
        return self.run_in_clone("direnv", "exec", str(self.clone), *cmd)

    def run_in_clone(self, *cmd):
        return subprocess.run(
            cmd,
            cwd=self.clone,
            env=self.env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )


def copy_working_tree(target):
    # List what git would commit, not what a `git clone` would get:
    # uncommitted changes to init_dev are what a developer wants to test.
    files = (
        subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
        )
        .stdout.decode()
        .split("\0")
    )

    # Copy the listed files. A tracked file deleted from the working tree is
    # listed too, but has nothing to copy.
    for name in [name for name in files if name != ""]:
        source = REPO_ROOT / name
        if source.is_file():
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    # Make the copy a repository like a clone: init_dev queries git and
    # .gitignore, and the staged files are the baseline for the check
    # that initialization leaves nothing to commit.
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    return target


def isolated_env(home):
    # Give the test its own HOME, so sm's link records and direnv's allow
    # list stay out of the real ones, which would otherwise point at a
    # deleted clone. sm needs its configuration and store there.
    shutil.copytree(
        Path.home() / ".skill-manager", home / ".skill-manager", symlinks=True
    )

    # Drop the caller's active direnv and venv, and point HOME and the XDG
    # directories at the test's HOME.
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("DIRENV_", "VIRTUAL_ENV"))
    }
    env.update(
        HOME=str(home),
        XDG_DATA_HOME=str(home / ".local/share"),
        XDG_CONFIG_HOME=str(home / ".config"),
        # Reusing the real download caches only saves time.
        PIP_CACHE_DIR=str(Path.home() / ".cache/pip"),
        PRE_COMMIT_HOME=str(Path.home() / ".cache/pre-commit"),
    )
    return env
