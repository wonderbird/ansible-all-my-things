#!/usr/bin/env bash
# Run every fast gate a commit must pass, locally and in CI.
#
# pytest is the gate list: pytest.ini makes a plain run collect every test
# under scripts/, and the tests in scripts/gate-discovery/ run each
# version-update harness and the syntax check of the version-update playbook.
# Tests also fail when a harness or a test file escapes discovery. CI runs
# this script and names no test of its own.
#
# CI also runs checks this script does not: the pre-commit hooks (they also
# run as the git pre-commit hook), the init_dev acceptance test (it needs the
# network and minutes, so it runs only in CI) and the zizmor workflow scan.
# Neither runs the version-update playbook against real upstreams, so a
# commit can pass every gate and still fail against one.
#
# Needs python3 with the packages of requirements.txt (put the repository's
# .venv/bin on PATH), and direnv and git, which the init_dev tests run.
#
# Usage, from the repository root:
#   ./scripts/ci-local.sh
#   git rebase -i --exec './scripts/ci-local.sh' <base>   # every commit
#
# ANSIBLE_PLAYBOOK may name an ansible-playbook outside PATH (a scratch venv).
set -euo pipefail

cd "$(dirname "$0")/.."

# Check every tool first: pytest would otherwise stop on an import error or a
# missing executable that does not say how to fix it.
if ! python3 -c 'import pytest, yaml' 2>/dev/null; then
  echo "ci-local: python3 lacks pytest or PyYAML. Put the repository's" \
       ".venv/bin on PATH, or run: python3 -m pip install -r requirements.txt" >&2
  exit 1
fi
for tool in direnv git; do
  if ! command -v "$tool" >/dev/null; then
    echo "ci-local: $tool is missing; the init_dev tests run it. Install it" \
         "as scripts/init_dev/ci_prerequisites.yml does." >&2
    exit 1
  fi
done

echo "== python3 -m pytest"
python3 -m pytest
echo "== ci-local: all gates passed"
