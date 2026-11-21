"""Each test builds a throwaway git repository and a fake `bd` binary, so no
test touches the real checkout or a beads database."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from . import beads
from .common import InitError
from .fakes import first_on_path, logged_calls, write_fake

# What the fake bd does: on `init`, it excludes .beads/ from git the way
# stealth mode does.
#
# FAKE_BD_MODE:
#   ok    succeeds (default).
#   fail  exits 1.
FAKE_BD_BEHAVIOUR = """\
    if [ "$FAKE_BD_MODE" = fail ]; then
      exit 1
    fi
    if [ "$1" = init ]; then
      echo ".beads/" >> .git/info/exclude
    fi
    """

TRACKING_GITIGNORE = (
    ".beads/*\n!.beads/issues.jsonl\n!.beads/config.yaml\n!.beads/metadata.json\n"
)


class EnsureTest(unittest.TestCase):
    def setUp(self):
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))

        # A git repository whose .gitignore keeps the three tracked files of
        # .beads/ tracked.
        self.repo = tmp / "repo"
        self.beads_dir = self.repo / ".beads"
        self.issues = self.beads_dir / "issues.jsonl"
        self.beads_dir.mkdir(parents=True)
        self.beads_dir.chmod(0o775)
        self.issues.write_text('{"title": "demo"}\n')
        (self.beads_dir / "config.yaml").write_text("issue-prefix: demo\n")
        (self.beads_dir / "metadata.json").write_text("{}\n")
        (self.repo / ".gitignore").write_text(TRACKING_GITIGNORE)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self.exclude = self.repo / ".git/info/exclude"
        self.exclude.write_text("keep-me\n")

        # The fake bd, first on PATH.
        bin_dir = tmp / "bin"
        bin_dir.mkdir()
        self.log = tmp / "calls"
        write_fake(bin_dir / "bd", FAKE_BD_BEHAVIOUR, log=self.log)
        self.env = first_on_path(bin_dir)

    def test_initializes_beads_and_imports_issues(self):
        self.run_beads_ensure_with()
        self.assertEqual(
            self.calls(),
            [
                "init --stealth --init-if-missing --non-interactive",
                f"import {self.issues}",
            ],
        )

    def test_restricts_beads_dir_to_owner(self):
        self.run_beads_ensure_with()
        self.assertEqual(self.beads_dir.stat().st_mode & 0o777, 0o700)

    def test_removes_only_the_stealth_exclude(self):
        self.run_beads_ensure_with()
        self.assertEqual(self.exclude.read_text(), "keep-me\n")

    def test_second_run_succeeds(self):
        self.run_beads_ensure_with()
        self.run_beads_ensure_with()

    def test_fails_without_bd_on_path(self):
        with (
            mock.patch.object(beads.shutil, "which", return_value=None),
            self.assertRaisesRegex(InitError, "bd not on PATH"),
        ):
            self.run_beads_ensure_with()

    def test_fails_when_issues_missing(self):
        self.assert_fails_when_missing("issues.jsonl")

    def test_fails_when_config_missing(self):
        self.assert_fails_when_missing("config.yaml")

    def test_fails_when_metadata_missing(self):
        self.assert_fails_when_missing("metadata.json")

    def test_fails_when_git_ignores_a_tracked_file(self):
        for name in ["issues.jsonl", "config.yaml", "metadata.json"]:
            with self.subTest(name=name):
                keep = TRACKING_GITIGNORE.replace(f"!.beads/{name}\n", "")
                (self.repo / ".gitignore").write_text(keep)
                with self.assertRaisesRegex(InitError, f"does not track .*{name}"):
                    self.run_beads_ensure_with()
                self.assertNotIn(f"import {self.issues}", self.calls())

    def test_fails_when_git_check_ignore_fails(self):
        # A git that fails like outside a repository, instead of answering.
        real_git = shutil.which("git")
        bin_dir = self.repo.parent / "bin"
        write_fake(
            bin_dir / "git",
            f"""\
            if [ "$1" = check-ignore ]; then
              echo "fatal: boom" >&2
              exit 128
            fi
            exec {real_git} "$@"
            """,
        )
        with self.assertRaisesRegex(InitError, "check-ignore failed.*128.*boom"):
            self.run_beads_ensure_with()
        self.assertNotIn(f"import {self.issues}", self.calls())

    def test_fails_when_bd_fails(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_beads_ensure_with(bd_mode="fail")

    def assert_fails_when_missing(self, name):
        (self.beads_dir / name).unlink()
        with self.assertRaisesRegex(InitError, f"Not found: .*{name}.*git checkout"):
            self.run_beads_ensure_with()
        self.assertEqual(self.calls(), [])

    def run_beads_ensure_with(self, bd_mode="ok"):
        with mock.patch.dict(os.environ, {**self.env, "FAKE_BD_MODE": bd_mode}):
            beads.ensure(self.repo)

    def calls(self):
        return logged_calls(self.log)
