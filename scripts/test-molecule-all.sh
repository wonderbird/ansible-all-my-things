#!/usr/bin/env bash
# SPDX-License-Identifier: MIT-0
#
# Run `molecule test` for all discovered roles or for the roles passed in.
# A discovered role has a
# molecule/default/molecule.yml scenario. Roles without a scenario
# (e.g. desktop, Windows) are skipped.
#
# All roles are tested even if one fails. A summary is printed at the end.
# Exit status is 1 if any role failed, 0 otherwise. This is the canonical
# role-discovery mechanism for CI — call it rather than reimplementing the
# scenario scan.
#
# Usage: run from the project root
#   ./scripts/test-molecule-all.sh
#   ./scripts/test-molecule-all.sh --list
#   ./scripts/test-molecule-all.sh --roles git tmux

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

roles=()
for role in "${PROJECT_ROOT}"/roles/*/; do
  if [ -f "${role}molecule/default/molecule.yml" ]; then
    role="${role%/}"
    roles+=("${role##*/}")
  fi
done

if [ ${#roles[@]} -eq 0 ]; then
  echo "ERROR: no default Molecule scenarios found under ${PROJECT_ROOT}/roles" >&2
  exit 1
fi

case "${1:-}" in
  --list)
    if [ "$#" -ne 1 ]; then
      echo "ERROR: --list takes no arguments" >&2
      exit 1
    fi
    printf '%s\n' "${roles[@]}"
    exit 0
    ;;
  --roles)
    shift
    if [ "$#" -eq 0 ]; then
      echo "No affected Molecule roles; skipping tests."
      exit 0
    fi
    for name in "$@"; do
      found=false
      for role in "${roles[@]}"; do
        if [ "${role}" = "${name}" ]; then
          found=true
          break
        fi
      done
      if [ "${found}" = false ]; then
        echo "ERROR: no default Molecule scenario found for role ${name}" >&2
        exit 1
      fi
    done
    roles=("$@")
    ;;
  *)
    if [ "$#" -ne 0 ]; then
      echo "Usage: $0 [--list | --roles [role ...]]" >&2
      exit 1
    fi
    ;;
esac

passed=()
failed=()
for name in "${roles[@]}"; do
  echo "==> Testing ${name}"
  if (cd "${PROJECT_ROOT}/roles/${name}" && "${PROJECT_ROOT}/scripts/with-molecule-lock.sh" molecule test); then
    passed+=("${name}")
  else
    failed+=("${name}")
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
