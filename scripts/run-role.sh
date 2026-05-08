#!/usr/bin/env bash
set -euo pipefail

HOST="${1:?Usage: run-role.sh <host> <role>}"
ROLE="${2:?Usage: run-role.sh <host> <role>}"

ansible-playbook /dev/stdin --limit "${HOST}" <<EOF
- hosts: ${HOST}
  become: true
  gather_facts: true
  roles:
    - ${ROLE}
EOF
