#!/usr/bin/env bash
# Run the gates that must hold for EVERY commit of a version-update change.
#
# Every gate below also runs as a job of .github/workflows/version-update-lint.yml,
# so this script adds no coverage of its own: it is the pre-push convenience
# that runs them all in one command, per commit rather than per branch, and
# without waiting for a runner. Keep the two in step -- a gate added here
# belongs in that workflow too.
#
# What neither can cover is the playbook run itself. It needs the network and
# the unauthenticated GitHub API budget of 60 requests an hour, so a commit can
# pass every gate here and still fail against a real upstream.
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
