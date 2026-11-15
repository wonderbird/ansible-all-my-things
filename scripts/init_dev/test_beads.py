"""Each test builds a throwaway git repository and a fake `bd` binary, so no
test touches the real checkout or a beads database."""

import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from . import beads
from .common import InitError

# Stands in for bd: logs its arguments, and on `init` excludes .beads/ from
# git the way stealth mode does.
#
# FAKE_BD_MODE:
#   ok    succeeds (default).
#   fail  exits 1.
FAKE_BD = textwrap.dedent("""\
    #!/bin/sh
    echo "$@" >> "$FAKE_BD_LOG"
    if [ "$FAKE_BD_MODE" = fail ]; then
      exit 1
    fi
    if [ "$1" = init ]; then
      echo ".beads/" >> .git/info/exclude
    fi
    """)


class EnsureTest(unittest.TestCase):
    def setUp(self):
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))

        # A git repository whose .gitignore keeps .beads/issues.jsonl tracked.
        self.repo = tmp / "repo"
        self.beads_dir = self.repo / ".beads"
        self.issues = self.beads_dir / "issues.jsonl"
        self.beads_dir.mkdir(parents=True)
        self.beads_dir.chmod(0o775)
        self.issues.write_text('{"title": "demo"}\n')
        (self.repo / ".gitignore").write_text(".beads/*\n!.beads/issues.jsonl\n")
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self.exclude = self.repo / ".git/info/exclude"
        self.exclude.write_text("keep-me\n")

        # The fake bd, first on PATH.
        bin_dir = tmp / "bin"
        bin_dir.mkdir()
        bd = bin_dir / "bd"
        bd.write_text(FAKE_BD)
        bd.chmod(0o755)
        self.log = tmp / "calls"
        self.env = {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "FAKE_BD_LOG": str(self.log),
        }

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
        self.issues.unlink()
        with self.assertRaisesRegex(InitError, "not found"):
            self.run_beads_ensure_with()
        self.assertEqual(self.calls(), [])

    def test_fails_when_git_ignores_issues(self):
        (self.repo / ".gitignore").write_text(".beads/*\n")
        with self.assertRaisesRegex(InitError, "does not track"):
            self.run_beads_ensure_with()
        self.assertNotIn(f"import {self.issues}", self.calls())

    def test_fails_when_bd_fails(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_beads_ensure_with(bd_mode="fail")

    def run_beads_ensure_with(self, bd_mode="ok"):
        with mock.patch.dict(os.environ, {**self.env, "FAKE_BD_MODE": bd_mode}):
            beads.ensure(self.repo)

    def calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []
