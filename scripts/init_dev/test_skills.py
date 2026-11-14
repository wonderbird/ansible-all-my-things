"""Each test builds a throwaway git repository, sm store and fake `sm`
binary, so no test touches the real checkout or ~/.skill-manager."""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from . import skills
from .common import InitError

# Stands in for sm: links each manifest skill into the store named by
# FAKE_SM_STORE, unless FAKE_SM_MODE says otherwise. Every call leaves a
# marker so tests can tell whether sm ran at all.
FAKE_SM = textwrap.dedent(f"""\
    #!{sys.executable}
    import json, os, sys
    from pathlib import Path
    Path(os.environ["FAKE_SM_MARKER"]).touch()
    mode = os.environ.get("FAKE_SM_MODE", "link")
    if mode == "fail":
        sys.exit(1)
    if mode == "link":
        dirs = {{"cc": ".claude/skills", "codex": ".agents/skills"}}
        store = Path(os.environ["FAKE_SM_STORE"])
        for skill in json.loads(Path(".skills.json").read_text())["skills"]:
            for tool in skill["tools"]:
                link = Path(dirs[tool]) / skill["name"]
                link.parent.mkdir(parents=True, exist_ok=True)
                if not link.is_symlink():
                    link.symlink_to(store / skill["name"])
    """)


def json_manifest(name, scope="project", tools=("cc",)):
    skill = {"name": name, "tools": list(tools), "scope": scope}
    return json.dumps({"version": 1, "skills": [skill], "profiles": {}})


class Fixture:
    def __init__(self, tmp):
        # Name the parts of the fixture.
        self.repo = tmp / "repo"
        self.sm_home = tmp / "sm_home"
        self.store = self.sm_home / "skills"
        self.marker = tmp / "sm-called"
        bin_dir = tmp / "bin"

        # A git repository whose manifest lists one ignored skill, demo.
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        (self.repo / ".skills.json").write_text(json_manifest("demo"))
        (self.repo / ".gitignore").write_text(".claude/skills/demo\n")

        # An sm home with demo in its store and auto-adopt disabled.
        (self.store / "demo").mkdir(parents=True)
        (self.store / "demo" / "SKILL.md").write_text("# demo\n")
        (self.sm_home / "config.toml").write_text("autoAdopt = false\n")

        # The fake sm, first on PATH.
        bin_dir.mkdir()
        sm = bin_dir / "sm"
        sm.write_text(FAKE_SM)
        sm.chmod(0o755)
        self.env = {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "FAKE_SM_STORE": str(self.store),
            "FAKE_SM_MARKER": str(self.marker),
        }

    def run_skills_install_with(self, sm_mode="link"):
        env = {**self.env, "FAKE_SM_MODE": sm_mode}
        with mock.patch.dict(os.environ, env):
            skills.install(repo_root=self.repo, sm_home=self.sm_home)


class InstallTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.fixture = Fixture(Path(tmp.name))

    def assert_sm_not_called(self):
        self.assertFalse(self.fixture.marker.exists(), "sm ran despite failed check")

    def test_links_skill_into_store(self):
        self.fixture.run_skills_install_with()
        link = self.fixture.repo / ".claude/skills/demo"
        self.assertEqual(link.resolve(), (self.fixture.store / "demo").resolve())

    def test_second_run_succeeds(self):
        self.fixture.run_skills_install_with()
        self.fixture.run_skills_install_with()

    def test_fails_without_sm_on_path(self):
        with (
            mock.patch.object(skills.shutil, "which", return_value=None),
            self.assertRaisesRegex(InitError, "sm not on PATH"),
        ):
            self.fixture.run_skills_install_with()

    def test_fails_when_auto_adopt_enabled(self):
        (self.fixture.sm_home / "config.toml").write_text("autoAdopt = true\n")
        with self.assertRaisesRegex(InitError, "autoAdopt = false"):
            self.fixture.run_skills_install_with()
        self.assert_sm_not_called()

    def test_fails_when_auto_adopt_unset(self):
        (self.fixture.sm_home / "config.toml").write_text("")
        with self.assertRaisesRegex(InitError, "autoAdopt = false"):
            self.fixture.run_skills_install_with()
        self.assert_sm_not_called()

    def test_fails_when_config_missing(self):
        (self.fixture.sm_home / "config.toml").unlink()
        with self.assertRaisesRegex(InitError, "Cannot read"):
            self.fixture.run_skills_install_with()
        self.assert_sm_not_called()

    def test_fails_when_config_unparsable(self):
        (self.fixture.sm_home / "config.toml").write_text("autoAdopt = \n")
        with self.assertRaisesRegex(InitError, "Cannot read"):
            self.fixture.run_skills_install_with()
        self.assert_sm_not_called()

    def test_fails_on_unsupported_scope(self):
        (self.fixture.repo / ".skills.json").write_text(
            json_manifest("demo", scope="user")
        )
        with self.assertRaisesRegex(InitError, "unsupported"):
            self.fixture.run_skills_install_with()
        self.assert_sm_not_called()

    def test_fails_on_unparsable_manifest(self):
        (self.fixture.repo / ".skills.json").write_text("{")
        with self.assertRaisesRegex(InitError, "Cannot read skills"):
            self.fixture.run_skills_install_with()
        self.assert_sm_not_called()

    def test_fails_when_skill_missing_from_store(self):
        (self.fixture.store / "demo" / "SKILL.md").unlink()
        with self.assertRaisesRegex(InitError, "Not in .*demo"):
            self.fixture.run_skills_install_with()
        self.assert_sm_not_called()

    def test_refuses_to_overwrite_tracked_skill(self):
        # A tracked file where sm would place the demo link.
        tracked = self.fixture.repo / ".claude/skills/demo/SKILL.md"
        tracked.parent.mkdir(parents=True)
        tracked.write_text("tracked\n")
        subprocess.run(
            ["git", "add", "-f", str(tracked)], cwd=self.fixture.repo, check=True
        )

        with self.assertRaisesRegex(InitError, "collide"):
            self.fixture.run_skills_install_with()
        self.assert_sm_not_called()
        self.assertEqual(tracked.read_text(), "tracked\n")

    def test_fails_when_sm_exits_nonzero(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.fixture.run_skills_install_with(sm_mode="fail")

    def test_fails_when_sm_succeeds_without_linking(self):
        with self.assertRaisesRegex(InitError, "not a symlink"):
            self.fixture.run_skills_install_with(sm_mode="noop")

    def test_fails_when_link_points_elsewhere(self):
        link = self.fixture.repo / ".claude/skills/demo"
        link.parent.mkdir(parents=True)
        link.symlink_to(self.fixture.repo)
        with self.assertRaisesRegex(InitError, "not a symlink"):
            self.fixture.run_skills_install_with(sm_mode="noop")

    def test_fails_when_link_not_gitignored(self):
        (self.fixture.repo / ".gitignore").write_text("")
        with self.assertRaisesRegex(InitError, "not gitignored"):
            self.fixture.run_skills_install_with()
