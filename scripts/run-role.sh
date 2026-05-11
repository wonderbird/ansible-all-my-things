#!/usr/bin/env bash
set -euo pipefail

HOST="${1:?Usage: run-role.sh <host> <role>}"
ROLE="${2:?Usage: run-role.sh <host> <role>}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ANSIBLE_ROLES_PATH="${SCRIPT_DIR}/../roles"

ansible-playbook /dev/stdin --limit "${HOST}" <<EOF
- hosts: ${HOST}
  become: true
  gather_facts: true
  vars:
    ansible_user: "{{ my_ansible_user }}"
    desktop_user_names: "{{ desktop_users | map(attribute='name') | list }}"
  roles:
    - ${ROLE}
EOF
