#!/bin/sh
#
# Source this script to set up environment variables
#
# Usage: source configure.sh
#
AWS_DEFAULT_REGION=$(aws configure get region)
export AWS_DEFAULT_REGION
echo ""
echo "Using AWS region: $AWS_DEFAULT_REGION"

export HOSTNAME=lorien
IPV4_ADDRESS=$(ansible-inventory --list --vault-password-file ./ansible-vault-password.txt | jq --raw-output "._meta.hostvars.$HOSTNAME.ansible_host")
export IPV4_ADDRESS
echo "IP address of $HOSTNAME: $IPV4_ADDRESS"
