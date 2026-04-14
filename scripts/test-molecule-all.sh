#!/usr/bin/env bash
# SPDX-License-Identifier: MIT-0
#
# Run `molecule test` for every role that has a
# molecule/default/molecule.yml scenario. Roles without a scenario
# (e.g. desktop, Windows) are skipped.
#
# All roles are tested even if one fails. A summary is printed at the end.
#
# Usage: run from the project root
#   ./scripts/test-molecule-all.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

passed=()
failed=()

for role in "${PROJECT_ROOT}"/roles/*/; do
  if [ -f "${role}molecule/default/molecule.yml" ]; then
    name="$(basename "${role}")"
    echo "==> Testing ${name}"
    if (cd "${role}" && molecule test); then
      passed+=("${name}")
    else
      failed+=("${name}")
    fi
  fi
done

echo ""
echo "Results: ${#passed[@]} passed, ${#failed[@]} failed"

if [ ${#passed[@]} -gt 0 ]; then
  for name in "${passed[@]}"; do
    echo "  PASS  ${name}"
  done
fi

if [ ${#failed[@]} -gt 0 ]; then
  for name in "${failed[@]}"; do
    echo "  FAIL  ${name}"
  done
  exit 1
fi
