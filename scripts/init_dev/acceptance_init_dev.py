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
        self.tmp = Path(tmp.name)
        self.clone = self.tmp / "clone"
        self._copy_working_tree()
        self.env = self._isolated_env()

    def _copy_working_tree(self):
        # A copy of what git would commit, not a `git clone`: uncommitted
        # changes to init_dev are what a developer wants to test.
        files = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others",
             "--exclude-standard"],
            cwd=REPO_ROOT, capture_output=True, check=True,
        ).stdout.decode().split("\0")

        for name in [n for n in files if n != ""]:
            source = REPO_ROOT / name
            if source.is_file():
                target = self.clone / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

        # Make the copy a repository like a clone: init_dev queries git and
        # .gitignore, and the staged files are the baseline for the check
        # that initialization leaves nothing to commit.
        subprocess.run(["git", "init", "-q"], cwd=self.clone, check=True)
        subprocess.run(["git", "add", "-A"], cwd=self.clone, check=True)

    def _isolated_env(self):
        # A separate HOME keeps sm's link records and direnv's allow list out
        # of the real ones, which would otherwise point at a deleted clone.
        home = self.tmp / "home"
        shutil.copytree(Path.home() / ".skill-manager",
                        home / ".skill-manager", symlinks=True)
        env = {
            k: v for k, v in os.environ.items()
            if not k.startswith(("DIRENV_", "VIRTUAL_ENV"))
        }
        env.update(
            HOME=str(home),
            XDG_DATA_HOME=str(home / ".local/share"),
            XDG_CONFIG_HOME=str(home / ".config"),
            # Reusing the real download cache only saves time.
            PIP_CACHE_DIR=str(Path.home() / ".cache/pip"),
        )
        return env

    def run_in_clone(self, *cmd):
        return subprocess.run(cmd, cwd=self.clone, env=self.env,
                              stdin=subprocess.DEVNULL,
                              capture_output=True, text=True)

    def run_init_dev(self):
        result = self.run_in_clone(sys.executable, "-m", "scripts.init_dev")
        self.assertEqual(result.returncode, 0,
                         f"init_dev failed:\n{result.stdout}{result.stderr}")

    def test_prepares_clone_and_can_run_again(self):
        self.run_init_dev()
        self.run_init_dev()

        manifest = json.loads((self.clone / ".skills.json").read_text())
        for skill in manifest["skills"]:
            self.assertTrue(
                (self.clone / ".claude/skills" / skill["name"] / "SKILL.md")
                .is_file(), f"skill {skill['name']} not deployed")

        prefix = self.run_in_clone(
            "direnv", "exec", str(self.clone),
            "python", "-c", "import sys; print(sys.prefix)")
        self.assertEqual(Path(prefix.stdout.strip()).resolve(),
                         (self.clone / ".venv").resolve(), prefix.stderr)

        # An import through the venv's python, not `ansible --version`: the
        # VM may also have a system-wide ansible on PATH.
        ansible = self.run_in_clone(
            "direnv", "exec", str(self.clone),
            "python", "-c", "import ansible")
        self.assertEqual(ansible.returncode, 0, ansible.stderr)

        untracked = self.run_in_clone(
            "git", "ls-files", "--others", "--exclude-standard")
        modified = self.run_in_clone("git", "diff", "--name-only")
        self.assertEqual(untracked.stdout + modified.stdout, "",
                         "initialization left files git would commit")
