# SPDX-License-Identifier: MIT-0

import tempfile
import unittest
from pathlib import Path

from molecule_references import (
    FileReference,
    RoleReference,
    SelectionError,
    references,
    scenario_playbooks,
)


class MoleculeReferencesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_extracts_nested_role_entry_and_variable_file(self) -> None:
        source = self.write(
            "converge.yml",
            "- hosts: all\n"
            "  vars_files: [values.yml]\n"
            "  tasks:\n"
            "  - block:\n"
            "    - ansible.builtin.include_role: {name: git, tasks_from: setup}\n",
        )

        self.assertCountEqual(
            references(source),
            [
                FileReference("vars", "values.yml"),
                RoleReference("git", (("tasks", "setup"),)),
            ],
        )

    def test_custom_lifecycle_playbook_replaces_default(self) -> None:
        self.write("verify.yml", "[]\n")
        config = self.write(
            "molecule.yml", "provisioner:\n  playbooks: {verify: check.yml}\n"
        )

        self.assertEqual(list(scenario_playbooks(config)), ["check.yml"])

    def test_rejects_merge_keys_that_can_hide_references(self) -> None:
        for content in (
            "- block:\n  - <<: {include_role: {name: git}}\n",
            "- include_role: {name: git, <<: {tasks_from: setup}}\n",
            "- roles: [{role: git, <<: {tasks_from: setup}}]\n",
        ):
            with self.subTest(content=content):
                source = self.write("converge.yml", content)

                with self.assertRaises(SelectionError) as raised:
                    list(references(source))

                self.assertIn(str(source), str(raised.exception))
                self.assertIn("merge key", str(raised.exception))

    def test_rejects_merge_keys_in_scenario_playbook_mapping(self) -> None:
        config = self.write(
            "molecule.yml", "provisioner:\n  playbooks:\n    <<: {verify: check.yml}\n"
        )

        with self.assertRaises(SelectionError) as raised:
            list(scenario_playbooks(config))

        self.assertIn(str(config), str(raised.exception))
        self.assertIn("merge key", str(raised.exception))

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path
