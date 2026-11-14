import contextlib
import io
import subprocess
import unittest
from unittest import mock

from . import __main__ as entry
from . import (
    direnv_envrc,
    galaxy_requirements,
    git_hooks,
    pip_requirements,
    platform_check,
    python_venv,
    skills,
    user_check,
)
from .common import InitError


class MainTest(unittest.TestCase):
    def test_returns_1_and_reports_init_error(self):
        code, err = self.run_main(InitError("boom"))
        self.assertEqual(code, 1)
        self.assertIn("init-dev: boom", err)

    def test_returns_1_on_failed_command(self):
        code, _ = self.run_main(subprocess.CalledProcessError(1, ["sm"]))
        self.assertEqual(code, 1)

    def test_returns_0_on_success(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code, _ = self.run_main(None)
        self.assertEqual(code, 0)

    def run_main(self, error):
        stderr = io.StringIO()
        with (
            mock.patch.object(platform_check, "check"),
            mock.patch.object(user_check, "check"),
            mock.patch.object(skills, "install", side_effect=error),
            mock.patch.object(python_venv, "ensure"),
            mock.patch.object(direnv_envrc, "ensure"),
            mock.patch.object(pip_requirements, "install"),
            mock.patch.object(galaxy_requirements, "install"),
            mock.patch.object(git_hooks, "install"),
            contextlib.redirect_stderr(stderr),
        ):
            return entry.main(), stderr.getvalue()
