import unittest
from unittest import mock

from . import platform_check
from .common import InitError


class CheckTest(unittest.TestCase):
    def check(self, os_release=None, error=None, euid=1000):
        with mock.patch.object(platform_check.platform,
                               "freedesktop_os_release",
                               return_value=os_release, side_effect=error), \
                mock.patch.object(platform_check.os, "geteuid",
                                  return_value=euid):
            platform_check.check()

    def test_accepts_ubuntu(self):
        self.check({"ID": "ubuntu"})

    def test_rejects_other_distro(self):
        with self.assertRaisesRegex(InitError, "Ubuntu required"):
            self.check({"ID": "debian"})

    def test_rejects_missing_os_release(self):
        with self.assertRaisesRegex(InitError, "Ubuntu required"):
            self.check(error=OSError("no os-release"))

    def test_rejects_root(self):
        with self.assertRaisesRegex(InitError, "root"):
            self.check({"ID": "ubuntu"}, euid=0)
