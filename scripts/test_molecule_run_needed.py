# SPDX-License-Identifier: MIT-0

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from molecule_run_needed import is_skipped

SCRIPT = Path(__file__).with_name("molecule_run_needed.py")


class SkipListTest(unittest.TestCase):
    def test_tracker_export_is_skipped(self) -> None:
        self.assertTrue(is_skipped(".beads/issues.jsonl"))

    def test_documentation_and_specs_are_skipped(self) -> None:
        self.assertTrue(is_skipped("docs/architecture/concepts/testing.md"))
        self.assertTrue(is_skipped("specs/015-aws-windows-profile/plan.md"))

    def test_markdown_outside_roles_is_skipped(self) -> None:
        self.assertTrue(is_skipped("README.md"))
        self.assertTrue(is_skipped("playbooks/README.md"))

    def test_agent_configuration_is_skipped(self) -> None:
        for path in (
            ".agents/skills/x/SKILL.md",
            ".claude/settings.json",
            ".codex/config.toml",
            ".omc/plans/plan.md",
            ".rtk/filters.toml",
            ".specify/memory/constitution.md",
        ):
            with self.subTest(path=path):
                self.assertTrue(is_skipped(path))

    def test_other_github_files_are_skipped(self) -> None:
        self.assertTrue(is_skipped(".github/workflows/docker-publish.yml"))
        self.assertTrue(is_skipped(".github/dependabot.yml"))

    def test_lint_and_meta_files_are_skipped(self) -> None:
        for path in (
            ".gitignore",
            ".markdownlint.json",
            ".pre-commit-config.yaml",
            ".shellcheckrc",
            ".skills.json",
            "LICENSE",
            "ruff.toml",
            "skills-lock.json",
        ):
            with self.subTest(path=path):
                self.assertTrue(is_skipped(path))

    def test_container_image_files_and_role_template_are_skipped(self) -> None:
        self.assertTrue(is_skipped(".devcontainer/Dockerfile"))
        self.assertTrue(is_skipped("container-structure-test-linux-arm64"))
        self.assertTrue(is_skipped("role-template/tasks/main.yml"))

    def test_molecule_workflow_is_tested(self) -> None:
        self.assertFalse(is_skipped(".github/workflows/molecule.yml"))

    def test_role_files_are_tested_including_markdown(self) -> None:
        self.assertFalse(is_skipped("roles/git/tasks/main.yml"))
        self.assertFalse(is_skipped("roles/git/README.md"))
        self.assertFalse(is_skipped("roles/git/molecule/default/verify.yml"))

    def test_shared_inputs_and_unknown_paths_are_tested(self) -> None:
        for path in (
            "ansible.cfg",
            "requirements.txt",
            "requirements.yml",
            "scripts/test-molecule-all.sh",
            "scripts/with-molecule-lock.sh",
            "scripts/molecule_run_needed.py",
            "playbooks/configure-profile.yml",
            "inventories/hcloud.yml",
            "new-top-level-file.yml",
            "docsx/notes.txt",
        ):
            with self.subTest(path=path):
                self.assertFalse(is_skipped(path))


class RunNeededTest(unittest.TestCase):
    def setUp(self) -> None:
        # Keep git's hooks and config isolated from the developer's.
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

        # Commit one file per area as the base.
        self.git("init", "--quiet")
        self.write("roles/git/tasks/main.yml", "[]\n")
        self.write("docs/index.md", "# Docs\n")
        self.write(".beads/issues.jsonl", "{}\n")
        self.base = self.commit("base")

    def test_tracker_export_only_skips_molecule(self) -> None:
        self.write(".beads/issues.jsonl", "{}\n{}\n")
        self.commit("export")

        self.assertEqual(self.run_molecule_run_needed("--base", self.base), "false")

    def test_documentation_only_skips_molecule(self) -> None:
        self.write("docs/index.md", "# Changed\n")
        self.write("README.md", "# New\n")
        self.commit("docs")

        self.assertEqual(self.run_molecule_run_needed("--base", self.base), "false")

    def test_role_change_runs_molecule(self) -> None:
        self.write("docs/index.md", "# Changed\n")
        self.write("roles/git/tasks/main.yml", "- debug: {}\n")
        self.commit("role")

        self.assertEqual(self.run_molecule_run_needed("--base", self.base), "true")

    def test_moving_a_role_file_out_of_roles_runs_molecule(self) -> None:
        self.git("mv", "roles/git/tasks/main.yml", "docs/main.yml")
        self.commit("move")

        self.assertEqual(self.run_molecule_run_needed("--base", self.base), "true")

    def test_unchanged_tree_skips_molecule(self) -> None:
        result = self.run_script("--base", self.base)

        self.assertEqual(result.stdout.strip(), "false")
        self.assertIn("No changed files", result.stderr)

    def test_missing_base_runs_molecule(self) -> None:
        self.assertEqual(self.run_molecule_run_needed(), "true")

    def test_unknown_base_fails(self) -> None:
        result = self.run_script("--base", "0" * 40)

        self.assert_fails_with_git_error(result)

    def assert_fails_with_git_error(
        self, result: subprocess.CompletedProcess[str]
    ) -> None:
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        # git's own message, not the command line in the exception text.
        self.assertIn("fatal: bad object", result.stderr)

    def run_molecule_run_needed(self, *args: str) -> str:
        result = self.run_script(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.root,
            env=self.env,
            check=False,
            capture_output=True,
            text=True,
        )

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.root,
            env=self.env,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def commit(self, message: str) -> str:
        self.git("add", "--all")
        self.git("commit", "--quiet", "--message", message)
        return self.git("rev-parse", "HEAD")


if __name__ == "__main__":
    unittest.main()
