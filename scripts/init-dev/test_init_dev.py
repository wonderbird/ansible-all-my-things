#!/usr/bin/env python3
"""Tests for init-dev.py.

Each test builds a throwaway git repository, sm store and fake `sm` binary,
so no test touches the real checkout or ~/.skill-manager.
"""
import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

_spec = importlib.util.spec_from_file_location(
    "init_dev", Path(__file__).parent / "init-dev.py"
)
init_dev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(init_dev)

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
        for s in json.loads(Path(".skills.json").read_text())["skills"]:
            for t in s["tools"]:
                link = Path(dirs[t]) / s["name"]
                link.parent.mkdir(parents=True, exist_ok=True)
                if not link.is_symlink():
                    link.symlink_to(store / s["name"])
    """)


class Fixture:
    def __init__(self, tmp):
        self.repo = tmp / "repo"
        self.sm_home = tmp / "sm_home"
        self.store = self.sm_home / "skills"
        self.marker = tmp / "sm-called"
        bin_dir = tmp / "bin"

        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        (self.repo / ".skills.json").write_text(json_manifest("demo"))
        (self.repo / ".gitignore").write_text(".claude/skills/demo\n")

        (self.store / "demo").mkdir(parents=True)
        (self.store / "demo" / "SKILL.md").write_text("# demo\n")
        (self.sm_home / "config.toml").write_text("autoAdopt = false\n")

        bin_dir.mkdir()
        sm = bin_dir / "sm"
        sm.write_text(FAKE_SM)
        sm.chmod(0o755)

        self.env = {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "FAKE_SM_STORE": str(self.store),
            "FAKE_SM_MARKER": str(self.marker),
        }

    def install(self, mode="link"):
        with mock.patch.dict(os.environ, {**self.env, "FAKE_SM_MODE": mode}):
            init_dev.install_skills(repo_root=self.repo, sm_home=self.sm_home)


def json_manifest(name, scope="project", tools=("cc",)):
    return (
        '{"version": 1, "skills": [{"name": "%s", "tools": [%s], '
        '"scope": "%s"}], "profiles": {}}'
        % (name, ", ".join(f'"{t}"' for t in tools), scope)
    )


class CheckPlatformTest(unittest.TestCase):
    def check(self, content):
        with tempfile.TemporaryDirectory() as tmp:
            os_release = Path(tmp) / "os-release"
            if content is not None:
                os_release.write_text(content)
            init_dev.check_platform(os_release)

    def test_accepts_ubuntu(self):
        self.check('NAME="Ubuntu"\nID=ubuntu\nID_LIKE=debian\n')

    def test_rejects_other_distro(self):
        with self.assertRaisesRegex(init_dev.InitError, "Ubuntu required"):
            self.check("ID=debian\n")

    def test_rejects_missing_os_release(self):
        with self.assertRaisesRegex(init_dev.InitError, "Ubuntu required"):
            self.check(None)

    def test_rejects_root(self):
        with mock.patch.object(init_dev.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(init_dev.InitError, "root"):
                self.check("ID=ubuntu\n")


class InstallSkillsTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.f = Fixture(Path(tmp.name))

    def assert_sm_not_called(self):
        self.assertFalse(self.f.marker.exists(), "sm ran despite failed check")

    def test_links_skill_into_store(self):
        self.f.install()
        link = self.f.repo / ".claude/skills/demo"
        self.assertEqual(link.resolve(), (self.f.store / "demo").resolve())

    def test_second_run_succeeds(self):
        self.f.install()
        self.f.install()

    def test_fails_without_sm_on_path(self):
        with mock.patch.object(init_dev.shutil, "which", return_value=None):
            with self.assertRaisesRegex(init_dev.InitError, "sm not on PATH"):
                self.f.install()

    def test_fails_when_auto_adopt_enabled(self):
        (self.f.sm_home / "config.toml").write_text("autoAdopt = true\n")
        with self.assertRaisesRegex(init_dev.InitError, "autoAdopt = false"):
            self.f.install()
        self.assert_sm_not_called()

    def test_fails_when_auto_adopt_unset(self):
        (self.f.sm_home / "config.toml").write_text("")
        with self.assertRaisesRegex(init_dev.InitError, "autoAdopt = false"):
            self.f.install()
        self.assert_sm_not_called()

    def test_fails_when_config_missing(self):
        (self.f.sm_home / "config.toml").unlink()
        with self.assertRaisesRegex(init_dev.InitError, "Cannot read"):
            self.f.install()
        self.assert_sm_not_called()

    def test_fails_when_config_unparsable(self):
        (self.f.sm_home / "config.toml").write_text("autoAdopt = \n")
        with self.assertRaisesRegex(init_dev.InitError, "Cannot read"):
            self.f.install()
        self.assert_sm_not_called()

    def test_fails_on_unsupported_scope(self):
        (self.f.repo / ".skills.json").write_text(
            json_manifest("demo", scope="user"))
        with self.assertRaisesRegex(init_dev.InitError, "unsupported"):
            self.f.install()
        self.assert_sm_not_called()

    def test_fails_on_unparsable_manifest(self):
        (self.f.repo / ".skills.json").write_text("{")
        with self.assertRaisesRegex(init_dev.InitError, "Cannot read skills"):
            self.f.install()
        self.assert_sm_not_called()

    def test_fails_when_skill_missing_from_store(self):
        (self.f.store / "demo" / "SKILL.md").unlink()
        with self.assertRaisesRegex(init_dev.InitError, "Not in .*demo"):
            self.f.install()
        self.assert_sm_not_called()

    def test_refuses_to_overwrite_tracked_skill(self):
        tracked = self.f.repo / ".claude/skills/demo/SKILL.md"
        tracked.parent.mkdir(parents=True)
        tracked.write_text("tracked\n")
        subprocess.run(["git", "add", "-f", str(tracked)],
                       cwd=self.f.repo, check=True)
        with self.assertRaisesRegex(init_dev.InitError, "collide"):
            self.f.install()
        self.assert_sm_not_called()
        self.assertEqual(tracked.read_text(), "tracked\n")

    def test_fails_when_sm_exits_nonzero(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.f.install(mode="fail")

    def test_fails_when_sm_succeeds_without_linking(self):
        with self.assertRaisesRegex(init_dev.InitError, "not a symlink"):
            self.f.install(mode="noop")

    def test_fails_when_link_points_elsewhere(self):
        link = self.f.repo / ".claude/skills/demo"
        link.parent.mkdir(parents=True)
        link.symlink_to(self.f.repo)
        with self.assertRaisesRegex(init_dev.InitError, "not a symlink"):
            self.f.install(mode="noop")

    def test_fails_when_link_not_gitignored(self):
        (self.f.repo / ".gitignore").write_text("")
        with self.assertRaisesRegex(init_dev.InitError, "not gitignored"):
            self.f.install()


class EnsureVenvTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.venv = self.repo / ".venv"

    def test_creates_working_venv_and_reuses_it(self):
        python = init_dev.ensure_venv(self.repo)
        self.assertEqual(python, self.venv / "bin" / "python")
        marker = self.venv / "kept"
        marker.touch()
        self.assertEqual(init_dev.ensure_venv(self.repo), python)
        self.assertTrue(marker.exists(), "existing venv was recreated")

    def test_removes_partial_venv_when_creation_fails(self):
        # Mimics Ubuntu without python3-venv: the directory is half-built,
        # then ensurepip fails.
        fake = self.tmp / "python"
        fake.write_text(textwrap.dedent("""\
            #!/bin/sh
            mkdir -p "$3/bin"
            echo "ensurepip is not available" >&2
            exit 1
            """))
        fake.chmod(0o755)
        with self.assertRaisesRegex(init_dev.InitError, "python3-venv"):
            init_dev.ensure_venv(self.repo, python=str(fake))
        self.assertFalse(os.path.lexists(self.venv))

    def test_rejects_venv_without_python(self):
        (self.venv / "bin").mkdir(parents=True)
        with self.assertRaisesRegex(init_dev.InitError, "rm -rf"):
            init_dev.ensure_venv(self.repo)
        self.assertTrue(self.venv.exists(), "user's .venv was deleted")

    def test_rejects_venv_that_is_a_file(self):
        self.venv.write_text("")
        with self.assertRaisesRegex(init_dev.InitError, "rm -rf"):
            init_dev.ensure_venv(self.repo)

    def test_rejects_dangling_venv_symlink(self):
        self.venv.symlink_to(self.tmp / "gone")
        with self.assertRaisesRegex(init_dev.InitError, "rm -rf"):
            init_dev.ensure_venv(self.repo)

    def test_rejects_venv_whose_python_lacks_pip(self):
        python = self.venv / "bin" / "python"
        python.parent.mkdir(parents=True)
        python.write_text("#!/bin/sh\nexit 1\n")
        python.chmod(0o755)
        with self.assertRaisesRegex(init_dev.InitError, "rm -rf"):
            init_dev.ensure_venv(self.repo)


class EnsureEnvrcTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.envrc = self.repo / ".envrc"
        # Keep direnv's allow list out of the real ~/.local/share/direnv.
        env = mock.patch.dict(os.environ, {
            "XDG_DATA_HOME": str(self.tmp / "data"),
            "XDG_CONFIG_HOME": str(self.tmp / "config"),
        })
        env.start()
        self.addCleanup(env.stop)

    def make_venv(self):
        # A pyvenv.cfg beside a python symlink is all sys.prefix needs, and
        # avoids the seconds a real `python -m venv` costs.
        venv = self.repo / ".venv"
        (venv / "bin").mkdir(parents=True)
        (venv / "pyvenv.cfg").write_text(
            f"home = {Path(sys.executable).parent}\n")
        (venv / "bin" / "python").symlink_to(sys.executable)

    def test_writes_envrc_that_activates_venv(self):
        self.make_venv()
        init_dev.ensure_envrc(self.repo)
        self.assertEqual(self.envrc.read_text(), init_dev.ENVRC)

    def test_second_run_succeeds(self):
        self.make_venv()
        init_dev.ensure_envrc(self.repo)
        init_dev.ensure_envrc(self.repo)

    def test_allows_own_envrc_that_direnv_has_not_approved(self):
        self.make_venv()
        self.envrc.write_text(init_dev.ENVRC)
        init_dev.ensure_envrc(self.repo)

    def test_refuses_foreign_envrc_and_keeps_it(self):
        self.make_venv()
        self.envrc.write_text("export SECRET=1\n")
        with self.assertRaisesRegex(init_dev.InitError, "did not write"):
            init_dev.ensure_envrc(self.repo)
        self.assertEqual(self.envrc.read_text(), "export SECRET=1\n")

    def test_refuses_envrc_that_is_a_directory(self):
        self.envrc.mkdir()
        with self.assertRaisesRegex(init_dev.InitError, "did not write"):
            init_dev.ensure_envrc(self.repo)

    def test_fails_when_python_runs_outside_venv(self):
        # Without pyvenv.cfg the python runs fine but reports the system
        # prefix, so only the prefix comparison can catch it.
        python = self.repo / ".venv" / "bin" / "python"
        python.parent.mkdir(parents=True)
        python.symlink_to(sys.executable)
        with self.assertRaisesRegex(init_dev.InitError, "does not activate"):
            init_dev.ensure_envrc(self.repo)

    def test_fails_when_venv_has_no_python(self):
        # Ubuntu ships no bare `python`, so direnv exec exits non-zero.
        (self.repo / ".venv").mkdir()
        with self.assertRaisesRegex(init_dev.InitError, "does not activate"):
            init_dev.ensure_envrc(self.repo)

    def test_fails_without_direnv_on_path(self):
        with mock.patch.object(init_dev.shutil, "which", return_value=None):
            with self.assertRaisesRegex(init_dev.InitError, "direnv not on"):
                init_dev.ensure_envrc(self.repo)
        self.assertFalse(self.envrc.exists())


class InstallRequirementsTest(unittest.TestCase):
    """Uses a fake venv python that logs its arguments, so no test needs
    the network or a real venv."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.requirements = self.repo / "requirements.txt"
        self.requirements.write_text("demo\n")
        self.log = self.tmp / "calls"
        self.python = self.tmp / "python"

    def fake_python(self, install_rc=0, check_rc=0):
        self.python.write_text(textwrap.dedent(f"""\
            #!/bin/sh
            echo "$@" >> "{self.log}"
            case "$*" in
              *" install "*) exit {install_rc} ;;
              *" check") echo "demo 1.0 has requirement x>2"; exit {check_rc} ;;
            esac
            """))
        self.python.chmod(0o755)

    def calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []

    def install(self):
        with contextlib.redirect_stdout(io.StringIO()):
            init_dev.install_requirements(self.python, self.repo)

    def test_installs_into_venv_then_checks(self):
        self.fake_python()
        self.install()
        install, check = self.calls()
        self.assertIn(f"install --no-input -r {self.requirements}", install)
        self.assertTrue(install.startswith("-m pip "))
        self.assertTrue(check.endswith("check"))

    def test_fails_when_requirements_missing(self):
        self.fake_python()
        self.requirements.unlink()
        with self.assertRaisesRegex(init_dev.InitError, "not found"):
            self.install()
        self.assertEqual(self.calls(), [])

    def test_fails_when_install_fails(self):
        self.fake_python(install_rc=1)
        with self.assertRaises(subprocess.CalledProcessError):
            self.install()

    def test_fails_on_conflicting_packages(self):
        self.fake_python(check_rc=1)
        with self.assertRaisesRegex(init_dev.InitError, "x>2"):
            self.install()


class MainTest(unittest.TestCase):
    def run_main(self, error):
        stderr = io.StringIO()
        with mock.patch.object(init_dev, "check_platform"), \
                mock.patch.object(init_dev, "install_skills",
                                  side_effect=error), \
                mock.patch.object(init_dev, "ensure_venv"), \
                mock.patch.object(init_dev, "ensure_envrc"), \
                mock.patch.object(init_dev, "install_requirements"), \
                contextlib.redirect_stderr(stderr):
            return init_dev.main(), stderr.getvalue()

    def test_returns_1_and_reports_init_error(self):
        code, err = self.run_main(init_dev.InitError("boom"))
        self.assertEqual(code, 1)
        self.assertIn("init-dev: boom", err)

    def test_returns_1_on_failed_command(self):
        code, _ = self.run_main(subprocess.CalledProcessError(1, ["sm"]))
        self.assertEqual(code, 1)

    def test_returns_0_on_success(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code, _ = self.run_main(None)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
