"""The version-update harnesses and the playbook syntax check as pytest gates.

pytest discovery is the only list of fast gates, so every
`playbooks/update-versions/tests/test-*.yml` harness runs here, found by
`gate_discovery.find_harnesses`, never named by hand.

These tests run the real `ansible-playbook` for about two minutes, yet a plain
`pytest` collects them. That is an accepted exception to the rule that such
tests live in `acceptance_*.py`: the harnesses are per-commit gates, need no
network and touch only temporary directories (ADR-008).

Fast developer path: `pytest scripts/init_dev`, or
`pytest -k 'not VersionUpdateHarness'` to skip this class.
"""

import os
import shutil
import subprocess
import unittest
from pathlib import Path

import gate_discovery

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK = REPO_ROOT / "playbooks" / "update-versions" / "perform-updates.yml"
TESTS_DIR = REPO_ROOT / "playbooks" / "update-versions" / "tests"


class VersionUpdateHarnessTest(unittest.TestCase):
    def setUp(self):
        self.ansible_playbook = self.find_ansible_playbook()

    def test_the_version_update_playbook_parses(self):
        self.assertAnsiblePlaybookPasses(
            PLAYBOOK.name, ["--syntax-check", str(PLAYBOOK)]
        )

    def test_every_harness_passes(self):
        for harness in gate_discovery.find_harnesses(TESTS_DIR):
            with self.subTest(harness=harness.name):
                self.assertAnsiblePlaybookPasses(harness.name, [str(harness)])

    def find_ansible_playbook(self):
        configured = os.environ.get("ANSIBLE_PLAYBOOK", "")
        if configured != "":
            return configured
        found = shutil.which("ansible-playbook")
        if found is None:
            self.fail(
                "ansible-playbook is not on PATH and ANSIBLE_PLAYBOOK is not "
                "set; put .venv/bin on PATH after `pip install -r "
                "requirements.txt`, or set ANSIBLE_PLAYBOOK to its path"
            )
        return found

    def assertAnsiblePlaybookPasses(self, name, arguments):
        command = [self.ansible_playbook, *arguments]
        result = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            env=harness_environment(),
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"{name} failed: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )


def harness_environment():
    """Return the child environment: the harness config and no vault secret.

    The repository ansible.cfg runs a vault password script that fails
    without a secret, so the harness config replaces it. The secret is
    dropped because no harness needs it; the harness config reads no vault,
    so dropping it changes no test result.
    """
    child_env = dict(os.environ)
    child_env["ANSIBLE_CONFIG"] = str(TESTS_DIR / "ansible.cfg")
    child_env.pop("ANSIBLE_VAULT_PASSWORD", None)
    return child_env
