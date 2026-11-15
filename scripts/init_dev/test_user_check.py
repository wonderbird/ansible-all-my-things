import unittest
from unittest import mock

from . import user_check
from .common import InitError


class CheckTest(unittest.TestCase):
    def test_accepts_regular_user(self):
        self.run_user_check_with(euid=1000)

    def test_rejects_root(self):
        with self.assertRaisesRegex(InitError, "root"):
            self.run_user_check_with(euid=0)

    def run_user_check_with(self, euid):
        with mock.patch.object(user_check.os, "geteuid", return_value=euid):
            user_check.check()
