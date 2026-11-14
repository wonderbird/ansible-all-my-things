import tempfile
import unittest
from pathlib import Path
from unittest import mock

from . import platform_check
from .common import InitError


class CheckTest(unittest.TestCase):
    def check(self, content):
        with tempfile.TemporaryDirectory() as tmp:
            os_release = Path(tmp) / "os-release"
            if content is not None:
                os_release.write_text(content)
            platform_check.check(os_release)

    def test_accepts_ubuntu(self):
        self.check('NAME="Ubuntu"\nID=ubuntu\nID_LIKE=debian\n')

    def test_rejects_other_distro(self):
        with self.assertRaisesRegex(InitError, "Ubuntu required"):
            self.check("ID=debian\n")

    def test_rejects_missing_os_release(self):
        with self.assertRaisesRegex(InitError, "Ubuntu required"):
            self.check(None)

    def test_rejects_root(self):
        with mock.patch.object(platform_check.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(InitError, "root"):
                self.check("ID=ubuntu\n")

