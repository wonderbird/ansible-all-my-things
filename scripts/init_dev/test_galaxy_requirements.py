"""Uses a fake ansible-galaxy that logs its arguments and working directory,
so no test needs the network or a real venv."""

import subprocess
import tempfile
import unittest
from pathlib import Path

from . import galaxy_requirements
from .common import InitError
from .fakes import logged_calls, write_fake


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.requirements = self.repo / "requirements.yml"
        self.requirements.write_text("collections: []\n")
        self.log = self.tmp / "calls"
        self.venv_bin = self.tmp / "bin"
        self.venv_bin.mkdir()

    def test_installs_requirements_with_venv_galaxy_in_repo(self):
        self.run_galaxy_install_with()
        self.assertEqual(self.calls(), [f"{self.repo} install -r {self.requirements}"])

    def test_fails_when_requirements_missing(self):
        self.requirements.unlink()
        with self.assertRaisesRegex(InitError, "not found"):
            self.run_galaxy_install_with()
        self.assertEqual(self.calls(), [])

    def test_fails_when_galaxy_fails(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_galaxy_install_with(exit_code=1)

    def run_galaxy_install_with(self, exit_code=0):
        # Logs the working directory too, which makes ansible.cfg apply.
        write_fake(
            self.venv_bin / "ansible-galaxy",
            f"""\
            echo "$PWD $@" >> "{self.log}"
            exit {exit_code}
            """,
        )
        galaxy_requirements.install(self.venv_bin / "python", self.repo)

    def calls(self):
        return logged_calls(self.log)
