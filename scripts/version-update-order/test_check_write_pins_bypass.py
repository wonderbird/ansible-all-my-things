#!/usr/bin/env python3
"""Tests for check-write-pins-bypass.py.

Each test writes a small tree and asserts what the check reports, so a
weakening of the pattern or the exclusions turns this red.
"""
import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_write_pins_bypass",
    Path(__file__).parent / "check-write-pins-bypass.py",
)
check_write_pins_bypass = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_write_pins_bypass)

TASK = """---
- name: Do something
  ansible.builtin.{module}:
    path: "{{{{ _roles_dir }}}}/tool/defaults/main.yml"
"""


class CheckWritePinsBypassTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "tasks").mkdir()
        (self.root / "tests").mkdir()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_check(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_write_pins_bypass.main([str(self.root)])
        return code, out.getvalue()

    def test_clean_tree_passes(self):
        self.write("tasks/fetch-thing.yml", "---\n- name: Fetch\n  ansible.builtin.uri:\n    url: x\n")
        code, out = self.run_check()
        self.assertIn("0 bypass violation(s)", out)
        self.assertEqual(code, 0)

    def test_replace_outside_write_pins_is_reported(self):
        self.write("tasks/sneaky.yml", TASK.format(module="replace"))
        code, out = self.run_check()
        self.assertIn("1 bypass violation(s)", out)
        self.assertIn("tasks/sneaky.yml", out)
        self.assertEqual(code, 1)

    def test_every_file_editing_module_is_reported(self):
        for module in ("replace", "lineinfile", "blockinfile", "copy", "template"):
            with self.subTest(module=module):
                self.setUp()
                self.write(f"tasks/edit-{module}.yml", TASK.format(module=module))
                code, out = self.run_check()
                self.assertIn("1 bypass violation(s)", out)
                self.assertEqual(code, 1)

    def test_short_module_name_is_reported(self):
        self.write("tasks/short.yml", "---\n- name: Edit\n  replace:\n    path: x\n")
        code, out = self.run_check()
        self.assertIn("1 bypass violation(s)", out)
        self.assertEqual(code, 1)

    def test_write_pins_itself_is_allowed(self):
        self.write("tasks/write-pins.yml", TASK.format(module="replace"))
        code, out = self.run_check()
        self.assertIn("0 bypass violation(s)", out)
        self.assertEqual(code, 0)

    def test_tests_directory_is_allowed(self):
        self.write("tests/some-harness.yml", TASK.format(module="copy"))
        code, out = self.run_check()
        self.assertIn("0 bypass violation(s)", out)
        self.assertEqual(code, 0)

    def test_commented_out_module_is_not_reported(self):
        self.write("tasks/commented.yml",
                   "---\n- name: Mention\n  # ansible.builtin.copy: not a task\n"
                   "  ansible.builtin.debug:\n    msg: copy: is only a word here\n")
        code, out = self.run_check()
        self.assertIn("0 bypass violation(s)", out)
        self.assertEqual(code, 0)

    def test_the_real_tree_is_clean(self):
        repo = Path(__file__).resolve().parent.parent.parent
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_write_pins_bypass.main([str(repo / "playbooks" / "update-versions")])
        self.assertEqual(code, 0, out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
