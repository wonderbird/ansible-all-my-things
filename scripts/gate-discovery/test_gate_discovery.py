"""Tests for gate_discovery.py.

Each guard is tested on a temporary tree that holds the loss it catches, and
once on the real tree, where it must find nothing to report.
"""

import tempfile
import unittest
from pathlib import Path

import gate_discovery

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_TESTS_DIR = REPO_ROOT / "playbooks" / "update-versions" / "tests"
REAL_SCRIPTS_DIR = REPO_ROOT / "scripts"

PLAY = """\
- name: A harness
  hosts: localhost
  tasks:
    - name: Run a case
      ansible.builtin.include_tasks: {target}
"""

TASK = """\
- name: A task
  ansible.builtin.debug:
    msg: hello
"""

TRIGGER_HARNESS = """\
- name: Trigger cases
  hosts: localhost
  vars:
    _cases:
      - id: one
        trigger: noop
  tasks:
    - name: Run a trigger case
      ansible.builtin.include_tasks: trigger-case.yml
      loop: "{{ _cases }}"
      loop_control:
        loop_var: _case
"""

TRIGGER_CASE = """\
- name: Induce the failure
  ansible.builtin.include_tasks: "trigger-{{ _case.trigger }}.yml"
"""


class HarnessDiscoveryTest(unittest.TestCase):
    def setUp(self):
        self.tests_dir = make_temporary_directory(self)

    def test_an_empty_harness_directory_raises_naming_the_glob(self):
        write_file(self.tests_dir, "helper.yml", TASK)

        with self.assertRaisesRegex(
            gate_discovery.GateDiscoveryError, r"tests/test-\*\.yml matches no"
        ):
            gate_discovery.find_harnesses(self.tests_dir)

    def test_only_top_level_test_playbooks_are_harnesses(self):
        write_file(self.tests_dir, "test-b.yml", PLAY.format(target="case.yml"))
        write_file(self.tests_dir, "test-a.yml", PLAY.format(target="case.yml"))
        write_file(self.tests_dir, "test-c.yaml", TASK)
        write_file(self.tests_dir, "case.yml", TASK)
        write_file(self.tests_dir, "fixtures/test-d.yml", TASK)

        harnesses = gate_discovery.find_harnesses(self.tests_dir)

        self.assertEqual(
            [path.name for path in harnesses], ["test-a.yml", "test-b.yml"]
        )

    def test_the_real_tree_has_a_harness(self):
        harnesses = gate_discovery.find_harnesses(REAL_TESTS_DIR)

        self.assertGreater(len(harnesses), 0)


class OrphanHarnessFileTest(unittest.TestCase):
    def setUp(self):
        self.tests_dir = make_temporary_directory(self)
        write_file(self.tests_dir, "test-main.yml", PLAY.format(target="case.yml"))
        write_file(self.tests_dir, "case.yml", TASK)
        write_file(self.tests_dir, "ansible.cfg", "[defaults]\n")

    def test_a_playbook_renamed_out_of_the_harness_glob_is_an_orphan(self):
        write_file(self.tests_dir, "other-harness.yml", PLAY.format(target="case.yml"))

        self.assertOrphans(["other-harness.yml"])

    def test_a_helper_no_harness_includes_is_an_orphan(self):
        write_file(self.tests_dir, "unused-case.yml", TASK)

        self.assertOrphans(["unused-case.yml"])

    def test_a_trigger_file_no_trigger_value_names_is_an_orphan(self):
        write_trigger_cases(self.tests_dir)
        write_file(self.tests_dir, "trigger-forgotten.yml", TASK)

        self.assertOrphans(["trigger-forgotten.yml"])

    def test_a_hosts_value_does_not_make_a_trigger_file_used(self):
        write_trigger_cases(self.tests_dir)
        write_file(self.tests_dir, "trigger-localhost.yml", TASK)

        self.assertOrphans(["trigger-localhost.yml"])

    def test_a_play_in_a_subdirectory_is_reported(self):
        write_file(self.tests_dir, "fixtures/data.yml", "- id: one\n  trigger: noop\n")
        write_file(
            self.tests_dir, "fixtures/old/test-hidden.yml", PLAY.format(target="x")
        )
        write_file(self.tests_dir, "fixtures/page.html", "<html></html>\n")

        self.assertOrphans(["fixtures/old/test-hidden.yml"])

    def test_literal_templated_and_helper_to_helper_includes_count_as_used(self):
        write_trigger_cases(self.tests_dir)
        write_file(
            self.tests_dir,
            "case.yml",
            "- name: Include a helper\n"
            "  ansible.builtin.import_tasks:\n"
            "    file: nested-helper.yml\n"
            "- name: Include shared tasks\n"
            "  include_tasks: ../tasks/shared.yml\n",
        )
        write_file(
            self.tests_dir,
            "nested-helper.yml",
            "- name: Include a deeper helper\n  import_tasks: deepest-helper.yaml\n",
        )
        write_file(self.tests_dir, "deepest-helper.yaml", TASK)

        self.assertOrphans([])

    def test_the_real_tree_has_no_orphan_harness_file(self):
        orphans = gate_discovery.find_orphan_harness_files(REAL_TESTS_DIR)

        self.assertEqual(orphans, [], f"files under {REAL_TESTS_DIR} no harness runs")

    def assertOrphans(self, expected):
        self.assertEqual(
            gate_discovery.find_orphan_harness_files(self.tests_dir), expected
        )


class UncollectedTestFileTest(unittest.TestCase):
    def setUp(self):
        self.scripts_dir = make_temporary_directory(self)

    def test_a_misnamed_file_with_a_test_case_subclass_is_reported(self):
        write_file(
            self.scripts_dir,
            "tool/tool_checks.py",
            "import unittest\n\n"
            "class ToolTest(unittest.TestCase):\n"
            "    def check_tool(self):\n"
            "        pass\n",
        )

        self.assertUncollected(["tool/tool_checks.py"], collected=[])

    def test_a_misnamed_file_with_a_test_function_is_reported(self):
        write_file(
            self.scripts_dir,
            "tool/tool_checks.py",
            "def test_tool():\n    pass\n",
        )

        self.assertUncollected(["tool/tool_checks.py"], collected=[])

    def test_a_misnamed_file_deriving_from_a_same_file_test_case_is_reported(self):
        write_file(
            self.scripts_dir,
            "tool/tool_checks.py",
            "from unittest import IsolatedAsyncioTestCase\n\n"
            "class ToolBase(IsolatedAsyncioTestCase):\n"
            "    pass\n\n"
            "class ToolChecks(ToolBase):\n"
            "    def check_tool(self):\n"
            "        pass\n",
        )
        write_file(
            self.scripts_dir,
            "tool/tool_derived.py",
            "import unittest\n\n"
            "class ToolBase(unittest.TestCase):\n"
            "    pass\n\n"
            "class ToolChecks(ToolBase):\n"
            "    pass\n",
        )

        self.assertUncollected(
            ["tool/tool_checks.py", "tool/tool_derived.py"], collected=[]
        )

    def test_collected_acceptance_and_plain_modules_are_not_reported(self):
        test_body = "def test_tool():\n    pass\n"
        collected = write_file(self.scripts_dir, "tool/test_tool.py", test_body)
        write_file(self.scripts_dir, "tool/acceptance_tool.py", test_body)
        write_file(self.scripts_dir, "tool/tool.py", "def run_tool():\n    pass\n")
        write_file(self.scripts_dir, "tool/__pycache__/stale_checks.py", test_body)
        write_file(self.scripts_dir, ".hidden/hidden_checks.py", test_body)

        self.assertUncollected([], collected=[collected])

    def test_the_real_tree_has_no_uncollected_test_file(self):
        collected = gate_discovery.collect_test_files(REPO_ROOT)

        uncollected = gate_discovery.find_uncollected_test_files(
            REAL_SCRIPTS_DIR, collected
        )

        self.assertEqual(
            uncollected, [], f"test files under {REAL_SCRIPTS_DIR} pytest misses"
        )

    def assertUncollected(self, expected, collected):
        self.assertEqual(
            gate_discovery.find_uncollected_test_files(self.scripts_dir, collected),
            expected,
        )


def make_temporary_directory(test_case):
    directory = tempfile.TemporaryDirectory()
    test_case.addCleanup(directory.cleanup)
    tests_dir = Path(directory.name) / "tests"
    tests_dir.mkdir()
    return tests_dir


def write_file(directory, relative, text):
    path = directory / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def write_trigger_cases(tests_dir):
    write_file(tests_dir, "test-trigger.yml", TRIGGER_HARNESS)
    write_file(tests_dir, "trigger-case.yml", TRIGGER_CASE)
    write_file(tests_dir, "trigger-noop.yml", TASK)


if __name__ == "__main__":
    unittest.main(verbosity=2)
