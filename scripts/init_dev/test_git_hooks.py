"""Uses a fake venv python that logs its arguments, so no test needs the
network or a real venv."""

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from . import git_hooks


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.log = self.tmp / "calls"
        self.python = self.tmp / "python"

    def test_installs_hooks_with_venv_pre_commit(self):
        self.run_git_hooks_install_with()
        self.assertEqual(
            self.log.read_text(), "-m pre_commit install --install-hooks\n"
        )

    def test_fails_when_pre_commit_fails(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_git_hooks_install_with(exit_code=1)

    def run_git_hooks_install_with(self, exit_code=0):
        self.python.write_text(
            textwrap.dedent(f"""\
            #!/bin/sh
            echo "$@" >> "{self.log}"
            exit {exit_code}
            """)
        )
        self.python.chmod(0o755)
        git_hooks.install(self.python, self.tmp)
