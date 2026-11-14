import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from . import direnv_envrc
from .common import InitError


class EnsureTest(unittest.TestCase):
    def setUp(self):
        # Create an empty repository in a temporary directory.
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.envrc = self.repo / ".envrc"

        # Keep direnv's allow list out of the real ~/.local/share/direnv.
        env = mock.patch.dict(
            os.environ,
            {
                "XDG_DATA_HOME": str(self.tmp / "data"),
                "XDG_CONFIG_HOME": str(self.tmp / "config"),
            },
        )
        env.start()
        self.addCleanup(env.stop)

    def make_venv(self):
        # A pyvenv.cfg beside a python symlink is all sys.prefix needs, and
        # avoids the seconds a real `python -m venv` costs.
        venv = self.repo / ".venv"
        (venv / "bin").mkdir(parents=True)
        (venv / "pyvenv.cfg").write_text(f"home = {Path(sys.executable).parent}\n")
        (venv / "bin" / "python").symlink_to(sys.executable)

    def test_writes_envrc_that_activates_venv(self):
        self.make_venv()
        direnv_envrc.ensure(self.repo)
        self.assertEqual(self.envrc.read_text(), direnv_envrc.ENVRC)

    def test_second_run_succeeds(self):
        self.make_venv()
        direnv_envrc.ensure(self.repo)
        direnv_envrc.ensure(self.repo)

    def test_allows_own_envrc_that_direnv_has_not_approved(self):
        self.make_venv()
        self.envrc.write_text(direnv_envrc.ENVRC)
        direnv_envrc.ensure(self.repo)

    def test_refuses_foreign_envrc_and_keeps_it(self):
        self.make_venv()
        self.envrc.write_text("export SECRET=1\n")
        with self.assertRaisesRegex(InitError, "did not write"):
            direnv_envrc.ensure(self.repo)
        self.assertEqual(self.envrc.read_text(), "export SECRET=1\n")

    def test_refuses_envrc_that_is_a_directory(self):
        self.envrc.mkdir()
        with self.assertRaisesRegex(InitError, "did not write"):
            direnv_envrc.ensure(self.repo)

    def test_fails_when_python_runs_outside_venv(self):
        # Without pyvenv.cfg the python runs fine but reports the system
        # prefix, so only the prefix comparison can catch it.
        python = self.repo / ".venv" / "bin" / "python"
        python.parent.mkdir(parents=True)
        python.symlink_to(sys.executable)

        with self.assertRaisesRegex(InitError, "does not activate"):
            direnv_envrc.ensure(self.repo)

    def test_fails_when_venv_has_no_python(self):
        # Ubuntu ships no bare `python`, so direnv exec exits non-zero.
        (self.repo / ".venv").mkdir()
        with self.assertRaisesRegex(InitError, "does not activate"):
            direnv_envrc.ensure(self.repo)

    def test_fails_without_direnv_on_path(self):
        with (
            mock.patch.object(direnv_envrc.shutil, "which", return_value=None),
            self.assertRaisesRegex(InitError, "direnv not on"),
        ):
            direnv_envrc.ensure(self.repo)
        self.assertFalse(self.envrc.exists())
