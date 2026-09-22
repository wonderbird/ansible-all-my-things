#!/usr/bin/env bash
# Run the gates that must hold for EVERY commit of a version-update change.
#
# CI never runs the version-update playbook: it needs the network and the
# unauthenticated GitHub API budget. A commit can therefore be green in CI and
# still be broken, so this script adds what CI cannot cover -- a syntax check of
# the playbook, and a network-free run of the real task files over a fixture
# registry.
#
# Usage, from the repository root:
#   ./scripts/ci-local.sh
#   git rebase -i --exec './scripts/ci-local.sh' <base>   # every commit
#
# ANSIBLE_PLAYBOOK may name an interpreter outside PATH (a scratch venv).
set -euo pipefail

cd "$(dirname "$0")/.."

ansible_playbook="${ANSIBLE_PLAYBOOK:-ansible-playbook}"
config="playbooks/update-versions/tests/ansible.cfg"
export ANSIBLE_CONFIG="$config"

run() {
  echo "== $*"
  "$@"
}

for script in scripts/version-update-order/test_*.py; do
  [ -e "$script" ] || continue
  run python3 "$script"
done

if [ -e scripts/version-update-order/check-version-update-order.py ]; then
  run python3 scripts/version-update-order/check-version-update-order.py \
    playbooks/update-versions/perform-updates.yml
fi

if [ -e scripts/version-update-order/check-write-pins-bypass.py ]; then
  run python3 scripts/version-update-order/check-write-pins-bypass.py \
    playbooks/update-versions
fi

run env -u ANSIBLE_VAULT_PASSWORD "$ansible_playbook" --syntax-check \
  playbooks/update-versions/perform-updates.yml

for harness in test-write-pins test-tool-isolation test-tool-registry \
               test-fixture-registry-smoke test-failure-source; do
  path="playbooks/update-versions/tests/$harness.yml"
  [ -e "$path" ] || continue
  run env -u ANSIBLE_VAULT_PASSWORD "$ansible_playbook" "$path"
done

echo "== ci-local: all gates passed"
