# SPDX-License-Identifier: MIT-0

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class MoleculeSelectionTest(unittest.TestCase):
    def setUp(self) -> None:
        # Give git a private checkout and keep its hooks and config isolated.
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        self.env.update(
            HOME=str(self.root),
            XDG_CONFIG_HOME=str(self.root),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_NAME="Test",
            GIT_AUTHOR_EMAIL="test@example.invalid",
            GIT_COMMITTER_NAME="Test",
            GIT_COMMITTER_EMAIL="test@example.invalid",
        )
        self.git("init", "--quiet")

        # Couple the real discovery/runner to a fake Molecule boundary.
        self.record = self.root / "calls"
        self.write("scripts/with-molecule-lock.sh", '#!/bin/sh\nexec "$@"\n').chmod(
            0o755
        )
        self.write(
            "bin/molecule", '#!/bin/sh\nprintf "%s\\n" "${PWD##*/}" >> "$CALLS"\n'
        ).chmod(0o755)
        self.env.update(
            PATH=f"{self.root / 'bin'}:{self.env['PATH']}", CALLS=str(self.record)
        )
        self.runner = self.root / "scripts/test-molecule-all.sh"
        shutil.copy2(Path(__file__).with_name(self.runner.name), self.runner)
        self.selector = self.runner.with_name("select_molecule_roles.py")
        shutil.copy2(Path(__file__).with_name(self.selector.name), self.selector)
        shutil.copy2(
            Path(__file__).with_name("molecule_references.py"), self.runner.parent
        )

        # git is used through both metadata and a scenario-only import.
        for role in ("consumer", "git", "leaf", "scenario_consumer"):
            self.write(f"roles/{role}/molecule/default/molecule.yml", "{}\n")
        self.write("roles/git/tasks/main.yml", "[]\n")
        self.write("roles/consumer/meta/main.yml", "dependencies: [bridge]\n")
        self.write("roles/bridge/meta/main.yml", "dependencies: [{role: git}]\n")
        self.write(
            "roles/scenario_consumer/molecule/default/prepare.yml",
            "- hosts: all\n  roles: [{role: bridge}]\n",
        )
        self.write(
            "roles/scenario_consumer/molecule/default/tasks/setup.yml",
            "- block:\n  - ansible.builtin.import_role:\n      name: helper\n",
        )
        self.write(
            "roles/scenario_consumer/molecule/default/verify.yml",
            "- hosts: all\n  tasks:\n  - include_tasks: tasks/setup.yml\n",
        )
        self.write("roles/helper/tasks/main.yml", "[]\n")
        self.write("roles/bridge/tasks/main.yml", "- include_role:\n    name: gate\n")
        self.write("roles/gate/tasks/main.yml", "[]\n")
        self.base = self.commit()

    def test_skips_changes_outside_scenarios_and_role_docs(self) -> None:
        for path in (
            ".beads/issues.jsonl",
            "docs/guide.md",
            "roles/leaf/README.md",
            ".github/workflows/other.yml",
            "roles/unused/tasks/main.yml",
        ):
            with self.subTest(path=path):
                self.write(path, "changed\n")
                self.commit()

                self.assertEqual(self.run_selected(self.base), [])

    def test_runs_only_changed_leaf(self) -> None:
        self.write("roles/leaf/files/prompt.md", "payload, not documentation\n")
        self.commit()

        self.assertEqual(self.run_selected(self.base), ["leaf"])

    def test_runs_git_and_transitive_consumers_across_entire_diff(self) -> None:
        self.write("roles/git/tasks/main.yml", "# changed\n[]\n")
        self.commit()
        self.write("docs/guide.md", "latest commit only changes docs\n")
        self.commit()

        self.assertEqual(
            self.run_selected(self.base), ["consumer", "git", "scenario_consumer"]
        )

    def test_runs_consumer_for_role_imported_by_scenario_task(self) -> None:
        self.write("roles/helper/tasks/main.yml", "# changed\n[]\n")
        self.commit()

        self.assertEqual(self.run_selected(self.base), ["scenario_consumer"])

    def test_runs_transitive_consumers_for_role_included_by_role_task(self) -> None:
        self.write("roles/gate/tasks/main.yml", "# changed\n[]\n")
        self.commit()

        self.assertEqual(
            self.run_selected(self.base), ["consumer", "scenario_consumer"]
        )

    def test_stale_reference_to_renamed_role_fails_selection(self) -> None:
        self.git("mv", "roles/git", "roles/git_new")
        self.commit()

        result = self.select(self.base)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("roles/bridge/meta/main.yml", result.stderr)

    def test_runs_every_scenario_when_shared_input_changes(self) -> None:
        for path, content in (
            ("requirements.yml", "collections: []\n"),
            ("ansible.cfg", "[galaxy]\nserver_list = galaxy\n"),
        ):
            with self.subTest(path=path):
                base = self.git("rev-parse", "HEAD").strip()
                self.write(path, content)
                self.commit()

                self.assertEqual(
                    self.run_selected(base),
                    ["consumer", "git", "leaf", "scenario_consumer"],
                )

    def test_runs_only_importing_scenario_when_external_file_or_role_changes(
        self,
    ) -> None:
        self.write(
            "roles/leaf/molecule/default/converge.yml",
            "- ansible.builtin.import_playbook: ../../../../playbooks/leaf.yml\n",
        )
        play = "- hosts: all\n  roles: [external]\n  tasks:\n"
        play += "  - import_tasks: tasks/leaf.yml\n"
        task = "- ansible.builtin.include_tasks:\n    file: ../more.yml\n"
        self.write("playbooks/leaf.yml", play)
        self.write("playbooks/tasks/leaf.yml", task)
        self.write("playbooks/more.yml", "[]\n")
        self.write("roles/external/tasks/main.yml", "[]\n")
        base = self.commit()

        for path in (
            "playbooks/leaf.yml",
            "playbooks/tasks/leaf.yml",
            "playbooks/more.yml",
            "roles/external/tasks/main.yml",
        ):
            with self.subTest(path=path):
                self.write(path, (self.root / path).read_text() + "# changed\n")
                head = self.commit()

                self.assertEqual(self.run_selected(base), ["leaf"])
                base = head

    def test_runs_importer_when_playbook_adjacent_role_changes(self) -> None:
        self.write(
            "roles/leaf/molecule/default/converge.yml",
            "- import_playbook: ../../../../playbooks/leaf.yml\n",
        )
        self.write("playbooks/leaf.yml", "- hosts: all\n  roles: [colocated]\n")
        tasks = "playbooks/roles/colocated/tasks/main.yml"
        self.write(tasks, "[]\n")
        base = self.commit()
        self.write(tasks, "# changed\n[]\n")
        self.commit()

        self.assertEqual(self.run_selected(base), ["leaf"])

    def test_ambiguous_playbook_adjacent_role_fails_with_source(self) -> None:
        source = "playbooks/leaf.yml"
        self.write(
            "roles/leaf/molecule/default/converge.yml",
            "- import_playbook: ../../../../playbooks/leaf.yml\n",
        )
        self.write(source, "- hosts: all\n  roles: [git]\n")
        self.write("playbooks/roles/git/tasks/main.yml", "[]\n")
        self.commit()

        result = self.select(self.base)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(source, result.stderr)

    def test_follows_configured_playbook_and_role_entry(self) -> None:
        self.write(
            "roles/leaf/molecule/default/molecule.yml",
            "provisioner:\n  playbooks: {converge: ../../../../playbooks/leaf.yml}\n",
        )
        self.write(
            "roles/leaf/molecule/default/converge.yml",
            '- import_playbook: "{{ unused_default }}"\n',
        )
        self.write(
            "playbooks/leaf.yml",
            "- hosts: all\n  tasks:\n"
            "  - module: include_role name=bridge tasks_from=extra\n",
        )
        self.write("roles/bridge/tasks/extra.yml", "- include_role: {name: helper}\n")
        base = self.commit()
        self.write("roles/helper/tasks/main.yml", "# changed\n[]\n")
        self.commit()

        self.assertEqual(self.run_selected(base), ["leaf", "scenario_consumer"])

    def test_runs_importer_when_external_vars_change(self) -> None:
        self.write(
            "roles/leaf/molecule/default/converge.yml",
            "- hosts: all\n  vars_files: [../../../../playbooks/values.yml]\n",
        )
        self.write("playbooks/values.yml", "value: 1\n")
        base = self.commit()
        self.write("playbooks/values.yml", "value: 2\n")
        self.commit()

        self.assertEqual(self.run_selected(base), ["leaf"])

    def test_runs_consumer_of_role_invoked_in_free_form(self) -> None:
        for action in (
            "action: ansible.builtin.import_role name=git",
            "local_action: include_role name=git",
            "action: {module: 'ansible.legacy.include_role name=git'}",
            "local_action: {module: import_role, name: git}",
            "import_role: name=git",
        ):
            with self.subTest(action=action):
                self.write(
                    "roles/leaf/molecule/default/converge.yml",
                    f"- hosts: all\n  tasks:\n  - {action}\n",
                )
                base = self.commit()
                tasks = "roles/git/tasks/main.yml"
                self.write(tasks, (self.root / tasks).read_text() + "# changed\n")
                self.commit()

                self.assertEqual(
                    self.run_selected(base),
                    ["consumer", "git", "leaf", "scenario_consumer"],
                )

    def test_ignores_unreachable_templated_includes(self) -> None:
        for source in (
            "roles/leaf/tasks/unused.yml",
            "roles/leaf/molecule/default/unused.yml",
        ):
            self.write(source, '- include_tasks: "{{ unused_path }}"\n')
        base = self.commit()
        self.write("docs/guide.md", "changed\n")
        self.commit()

        self.assertEqual(self.run_selected(base), [])

    def test_runner_rejects_empty_explicit_selection(self) -> None:
        result = subprocess.run(
            [self.runner, "--roles"],
            cwd=self.root,
            env=self.env,
            check=False,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.record.exists())

    def test_unresolved_import_fails_even_when_only_docs_change(self) -> None:
        source = "roles/leaf/molecule/default/converge.yml"
        self.write(source, '- import_playbook: "{{ external_playbook }}"\n')
        base = self.commit()
        self.write("docs/guide.md", "changed\n")
        self.commit()

        result = self.select(base)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(source, result.stderr)

    def test_runs_every_scenario_without_a_base(self) -> None:
        self.assertEqual(
            self.run_selected(), ["consumer", "git", "leaf", "scenario_consumer"]
        )

    def test_invalid_base_fails_instead_of_skipping(self) -> None:
        result = self.select("missing-base")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing-base", result.stderr)

    def test_unresolvable_role_reference_fails_instead_of_skipping(self) -> None:
        self.write(
            "roles/bridge/tasks/main.yml", '- include_role:\n    name: "{{ name }}"\n'
        )
        self.commit()

        result = self.select(self.base)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("roles/bridge/tasks/main.yml", result.stderr)

    def run_selected(self, base: str | None = None) -> list[str]:
        selection = self.select(base)
        self.assertEqual(selection.returncode, 0, selection.stderr)
        roles = selection.stdout.split()
        if len(roles) == 0:
            return []
        self.record.unlink(missing_ok=True)
        subprocess.run(
            [self.runner, "--roles", *roles],
            cwd=self.root,
            env=self.env,
            check=True,
            capture_output=True,
        )
        return self.record.read_text().splitlines() if self.record.exists() else []

    def select(self, base: str | None) -> subprocess.CompletedProcess[str]:
        arguments = [] if base is None else ["--base", base]
        result = subprocess.run(
            [sys.executable, self.selector, *arguments],
            cwd=self.root,
            env=self.env,
            check=False,
            capture_output=True,
            text=True,
        )
        return result

    def write(self, path: str, content: str) -> Path:
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)
        return file

    def commit(self) -> str:
        self.git("add", "--", ".")
        self.git("commit", "--quiet", "-m", "fixture")
        return self.git("rev-parse", "HEAD").strip()

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            env=self.env,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
