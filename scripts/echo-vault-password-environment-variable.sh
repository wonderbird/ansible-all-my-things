#!/bin/sh
# Send ANSIBLE_VAULT_PASSWORD to stdout
#
# Use this script as the ansible-vault password file so that
# the vault password can be injected into docker containers via
# environment variables.
#
# See also:
#   https://forum.ansible.com/t/environment-variable-as-vault-key/40837
#
if [ -z "$ANSIBLE_VAULT_PASSWORD" ]; then
    echo "The environment variable ANSIBLE_VAULT_PASSWORD is not set" >&2
    exit 1
fi

echo "$ANSIBLE_VAULT_PASSWORD"
