#!/usr/bin/env bash
# Run the gates that must hold for EVERY commit of a version-update change.
#
# CI never runs either version-update playbook: both need the network and the
# unauthenticated GitHub API budget. A commit can therefore be green in CI and
# still be broken, so this script adds what CI cannot cover -- a syntax check of
# both playbooks and, once a fixture registry exists, a network-free smoke run
# of it.
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

for playbook in perform-updates query-versions; do
  run env -u ANSIBLE_VAULT_PASSWORD "$ansible_playbook" --syntax-check \
    "playbooks/update-versions/$playbook.yml"
done

for harness in test-write-pins test-tool-isolation test-tool-registry; do
  path="playbooks/update-versions/tests/$harness.yml"
  [ -e "$path" ] || continue
  run env -u ANSIBLE_VAULT_PASSWORD "$ansible_playbook" "$path"
done

smoke="playbooks/update-versions/tests/smoke-fixture-registry.yml"
if [ -e "$smoke" ]; then
  run env -u ANSIBLE_VAULT_PASSWORD "$ansible_playbook" "$smoke"
fi

echo "== ci-local: all gates passed"
