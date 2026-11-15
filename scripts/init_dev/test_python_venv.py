import os
import tempfile
import unittest
from pathlib import Path

from . import python_venv
from .common import InitError
from .fakes import write_fake


class EnsureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.venv = self.repo / ".venv"

    def test_creates_working_venv_and_reuses_it(self):
        # The first run creates the venv.
        python = python_venv.ensure(self.repo)
        self.assertEqual(python, self.venv / "bin" / "python")

        # The second run keeps it: a marker file survives.
        marker = self.venv / "kept"
        marker.touch()
        self.assertEqual(python_venv.ensure(self.repo), python)
        self.assertTrue(marker.exists(), "existing venv was recreated")

    def test_removes_partial_venv_when_creation_fails(self):
        # Mimics Ubuntu without python3-venv: the directory is half-built,
        # then ensurepip fails.
        fake = write_fake(
            self.tmp / "python",
            """\
            mkdir -p "$3/bin"
            echo "ensurepip is not available" >&2
            exit 1
            """,
        )

        with self.assertRaisesRegex(InitError, "python3-venv"):
            python_venv.ensure(self.repo, python=str(fake))
        self.assertFalse(os.path.lexists(self.venv))

    def test_rejects_venv_without_python(self):
        (self.venv / "bin").mkdir(parents=True)
        with self.assertRaisesRegex(InitError, "rm -rf"):
            python_venv.ensure(self.repo)
        self.assertTrue(self.venv.exists(), "user's .venv was deleted")

    def test_rejects_venv_that_is_a_file(self):
        self.venv.write_text("")
        with self.assertRaisesRegex(InitError, "rm -rf"):
            python_venv.ensure(self.repo)

    def test_rejects_dangling_venv_symlink(self):
        self.venv.symlink_to(self.tmp / "gone")
        with self.assertRaisesRegex(InitError, "rm -rf"):
            python_venv.ensure(self.repo)

    def test_rejects_venv_whose_python_lacks_pip(self):
        # A python that fails every command, `-m pip` included.
        python = self.venv / "bin" / "python"
        python.parent.mkdir(parents=True)
        write_fake(python, "exit 1\n")

        with self.assertRaisesRegex(InitError, "rm -rf"):
            python_venv.ensure(self.repo)
