"""Uses a fake venv python that logs its arguments, so no test needs the
network or a real venv."""

import contextlib
import io
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from . import pip_requirements
from .common import InitError


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.requirements = self.repo / "requirements.txt"
        self.requirements.write_text("demo\n")
        self.log = self.tmp / "calls"
        self.python = self.tmp / "python"

    def test_installs_into_venv_then_checks(self):
        self.run_pip_install_with()
        install, check = self.calls()
        self.assertIn(f"install --no-input -r {self.requirements}", install)
        self.assertTrue(install.startswith("-m pip "))
        self.assertTrue(check.endswith("check"))

    def test_fails_when_requirements_missing(self):
        self.requirements.unlink()
        with self.assertRaisesRegex(InitError, "not found"):
            self.run_pip_install_with()
        self.assertEqual(self.calls(), [])

    def test_fails_when_install_fails(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_pip_install_with(install_rc=1)

    def test_fails_on_conflicting_packages(self):
        with self.assertRaisesRegex(InitError, "x>2"):
            self.run_pip_install_with(check_rc=1)

    def fake_python(self, install_rc=0, check_rc=0):
        self.python.write_text(
            textwrap.dedent(f"""\
            #!/bin/sh
            echo "$@" >> "{self.log}"
            case "$*" in
              *" install "*) exit {install_rc} ;;
              *" check") echo "demo 1.0 has requirement x>2"; exit {check_rc} ;;
            esac
            """)
        )
        self.python.chmod(0o755)

    def calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []

    def run_pip_install_with(self, install_rc=0, check_rc=0):
        self.fake_python(install_rc, check_rc)
        with contextlib.redirect_stdout(io.StringIO()):
            pip_requirements.install(self.python, self.repo)
