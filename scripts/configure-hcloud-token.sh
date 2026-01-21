#!/bin/sh
#
# Source this script to set the HCLOUD_TOKEN environment variable
#
# Usage: source configure-hcloud-token.sh
#
if [ -z "$HCLOUD_TOKEN" ]; then
    echo "hcloud API token: "
    stty -echo
    read -r HCLOUD_TOKEN
    stty echo
    export HCLOUD_TOKEN
fi
