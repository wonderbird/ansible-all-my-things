#!/bin/sh
#
# Source this script to set up environment variables
#
# Usage: source configure.sh HOSTNAME
#
# Parameters:
#
#   HOSTNAME    The hostname of the machine to configure (default: lorien)
#
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

HOSTNAME=${1}
export HOSTNAME
if [ -z "$HOSTNAME" ]; then
  echo "Error: HOSTNAME is not set. Please provide a hostname as an argument."
  echo ""
  echo "Usage: source configure.sh HOSTNAME"
  return 1
fi

echo -n "hcloud API token: "
read -rs HCLOUD_TOKEN
export HCLOUD_TOKEN

AWS_DEFAULT_REGION=$(aws configure get region)
export AWS_DEFAULT_REGION
echo ""
echo "Using AWS region: $AWS_DEFAULT_REGION"

IPV4_ADDRESS=$(ansible-inventory --list --vault-password-file "$SCRIPT_DIR/ansible-vault-password.txt" | jq --raw-output "._meta.hostvars.$HOSTNAME.ansible_host")
export IPV4_ADDRESS
echo "IP address of $HOSTNAME: $IPV4_ADDRESS"
