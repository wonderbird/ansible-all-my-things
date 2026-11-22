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
from .fakes import first_on_path, logged_calls, write_executable

# Stands in for sm: links each manifest skill into the store named by
# FAKE_SM_STORE, unless FAKE_SM_MODE says otherwise. Every call is logged to
# FAKE_SM_LOG, so tests can tell whether sm ran at all. Python, not sh,
# because it parses the manifest.
#
# Skills of scope user go below FAKE_SM_USER_HOME instead of the working directory.
#
# FAKE_SM_MODE:
#   link  links the skills like the real sm (default).
#   noop  exits 0 without linking, like the real sm when it only warns.
#   fail  exits 1.
FAKE_SM = textwrap.dedent(f"""\
    #!{sys.executable}
    import json
    import os
    import sys
    from pathlib import Path

    # Log the call.
    with open(os.environ["FAKE_SM_LOG"], "a") as log:
        print(*sys.argv[1:], file=log)

    # Fail if asked to. noop falls through to the exit 0 at the end.
    mode = os.environ.get("FAKE_SM_MODE", "link")
    if mode == "fail":
        sys.exit(1)

    # Link each manifest skill into the store. An existing link stays, so
    # a second run succeeds, as with the real sm.
    if mode == "link":
        skill_dirs = {{"cc": ".claude/skills", "codex": ".agents/skills"}}
        store = Path(os.environ["FAKE_SM_STORE"])
        home = Path(os.environ["FAKE_SM_USER_HOME"])
        manifest = json.loads(Path(".skills.json").read_text())
        for skill in manifest["skills"]:
            for tool in skill["tools"]:
                base = Path(".") if skill["scope"] == "project" else home
                link = base / skill_dirs[tool] / skill["name"]
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
        self.home = tmp / "home"
        self.store = self.sm_home / "skills"
        self.log = tmp / "sm-calls"
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
        write_executable(bin_dir / "sm", FAKE_SM)
        self.env = {
            **first_on_path(bin_dir),
            "FAKE_SM_STORE": str(self.store),
            "FAKE_SM_USER_HOME": str(self.home),
            "FAKE_SM_LOG": str(self.log),
        }

    def run_skills_install_with(self, sm_mode="link"):
        env = {**self.env, "FAKE_SM_MODE": sm_mode}
        with mock.patch.dict(os.environ, env):
            skills.install(repo_root=self.repo, sm_home=self.sm_home, home=self.home)


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture(Path(self.enterContext(tempfile.TemporaryDirectory())))

    def test_links_skill_into_store(self):
        self.fixture.run_skills_install_with()
        link = self.fixture.repo / ".claude/skills/demo"
        self.assertEqual(link.resolve(), (self.fixture.store / "demo").resolve())

    def test_links_user_skill_into_home_not_into_repo(self):
        (self.fixture.repo / ".skills.json").write_text(
            json_manifest("demo", scope="user", tools=("cc", "codex"))
        )
        self.fixture.run_skills_install_with()
        for link in (
            self.fixture.home / ".claude/skills/demo",
            self.fixture.home / ".agents/skills/demo",
        ):
            self.assertEqual(link.resolve(), (self.fixture.store / "demo").resolve())
        self.assertFalse((self.fixture.repo / ".claude/skills/demo").exists())
        self.assertTrue((self.fixture.home / ".claude/skills/demo").is_symlink())

    def test_user_skill_needs_no_gitignore_entry(self):
        (self.fixture.repo / ".skills.json").write_text(
            json_manifest("demo", scope="user")
        )
        (self.fixture.repo / ".gitignore").write_text("")
        self.fixture.run_skills_install_with()
        self.assertTrue((self.fixture.home / ".claude/skills/demo").is_symlink())

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
            json_manifest("demo", scope="team")
        )
        with self.assertRaisesRegex(InitError, "unsupported"):
            self.fixture.run_skills_install_with()
        self.assert_sm_not_called()

    def test_fails_on_skill_without_scope_or_tools(self):
        for key in ["scope", "tools"]:
            with self.subTest(missing=key):
                skill = {"name": "demo", "tools": ["cc"], "scope": "project"}
                del skill[key]
                (self.fixture.repo / ".skills.json").write_text(
                    json.dumps({"version": 1, "skills": [skill], "profiles": {}})
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

    def test_refuses_tracked_project_skill_in_mixed_manifest(self):
        # A tracked file where sm would place the project skill link.
        manifest = {
            "version": 1,
            "profiles": {},
            "skills": [
                {"name": "demo", "tools": ["cc"], "scope": "project"},
                {"name": "other", "tools": ["cc"], "scope": "user"},
            ],
        }
        (self.fixture.repo / ".skills.json").write_text(json.dumps(manifest))
        (self.fixture.store / "other").mkdir()
        (self.fixture.store / "other" / "SKILL.md").write_text("# other\n")
        tracked = self.fixture.repo / ".claude/skills/demo/SKILL.md"
        tracked.parent.mkdir(parents=True)
        tracked.write_text("tracked\n")
        subprocess.run(
            ["git", "add", "-f", str(tracked)], cwd=self.fixture.repo, check=True
        )

        with self.assertRaisesRegex(InitError, "collide"):
            self.fixture.run_skills_install_with()
        self.assert_sm_not_called()

    def test_user_skill_may_share_its_name_with_a_tracked_project_path(self):
        # A tracked file at the path a project link would take, but the
        # manifest lists the skill with scope user.
        (self.fixture.repo / ".skills.json").write_text(
            json_manifest("demo", scope="user")
        )
        tracked = self.fixture.repo / ".claude/skills/demo/SKILL.md"
        tracked.parent.mkdir(parents=True)
        tracked.write_text("tracked\n")
        subprocess.run(
            ["git", "add", "-f", str(tracked)], cwd=self.fixture.repo, check=True
        )

        self.fixture.run_skills_install_with()
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

    def test_fails_when_user_link_points_elsewhere(self):
        (self.fixture.repo / ".skills.json").write_text(
            json_manifest("demo", scope="user")
        )
        link = self.fixture.home / ".claude/skills/demo"
        link.parent.mkdir(parents=True)
        link.symlink_to(self.fixture.repo)
        with self.assertRaisesRegex(InitError, "not a symlink"):
            self.fixture.run_skills_install_with(sm_mode="noop")

    def test_fails_when_user_skill_not_linked(self):
        (self.fixture.repo / ".skills.json").write_text(
            json_manifest("demo", scope="user")
        )
        with self.assertRaisesRegex(InitError, "not a symlink"):
            self.fixture.run_skills_install_with(sm_mode="noop")

    def test_fails_when_link_not_gitignored(self):
        (self.fixture.repo / ".gitignore").write_text("")
        with self.assertRaisesRegex(InitError, "not gitignored"):
            self.fixture.run_skills_install_with()

    def assert_sm_not_called(self):
        self.assertEqual(
            logged_calls(self.fixture.log), [], "sm ran despite failed check"
        )
