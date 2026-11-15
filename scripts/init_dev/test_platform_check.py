import unittest
from unittest import mock

from . import platform_check
from .common import InitError


class CheckTest(unittest.TestCase):
    def test_accepts_ubuntu(self):
        self.run_platform_check_with({"ID": "ubuntu"})

    def test_rejects_other_distro(self):
        with self.assertRaisesRegex(InitError, "Ubuntu required"):
            self.run_platform_check_with({"ID": "debian"})

    def test_rejects_missing_os_release(self):
        with self.assertRaisesRegex(InitError, "Ubuntu required"):
            self.run_platform_check_with(error=OSError("no os-release"))

    def run_platform_check_with(self, os_release=None, error=None):
        with mock.patch.object(
            platform_check.platform,
            "freedesktop_os_release",
            return_value=os_release,
            side_effect=error,
        ):
            platform_check.check()
