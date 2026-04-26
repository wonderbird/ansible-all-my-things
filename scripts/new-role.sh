#!/usr/bin/env bash
set -euo pipefail
ROLE_NAME="${1:?Usage: new-role.sh <role-name>}"
cp -r role-template "roles/${ROLE_NAME}"
find "roles/${ROLE_NAME}" -type f | xargs sed -i "s/ROLE_NAME/${ROLE_NAME}/g"
echo "Created roles/${ROLE_NAME}"
