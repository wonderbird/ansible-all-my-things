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

if [ -z "$HCLOUD_TOKEN" ]; then
    echo "hcloud API token: "
    stty -echo
    read -r HCLOUD_TOKEN
    stty echo
    export HCLOUD_TOKEN
fi

AWS_DEFAULT_REGION=$(aws configure get region)
export AWS_DEFAULT_REGION
echo ""
echo "Using AWS region: $AWS_DEFAULT_REGION"

IPV4_ADDRESS=$(ansible-inventory --list | jq --raw-output "._meta.hostvars.$HOSTNAME.ansible_host.__ansible_unsafe")
export IPV4_ADDRESS
echo "IP address of $HOSTNAME: $IPV4_ADDRESS"
