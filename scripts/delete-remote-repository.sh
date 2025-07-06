#!/bin/bash
# Delete the remote repository created by create-remote-repository.sh.
#
# - remove the remote name from the local repository,
# - remove the remote checkout repository,
# - remove the remote bare repository.
#
# Usage
#
# ./delete-remote-repository.sh <local-repo> <remote-user> <remote-host> <remote-bare-repo-parent> <remote-checkout-parent> <remote-name>
#
# Parameters
#
# $1: path to the local repository to be cloned
# $2: user name on the remote computer
# $3: DNS name or IP address of the remote computer
# $4: path of parent folder for the remote bare repository
# $5: path to parent folder for the cloned remote repository
# $6: remote name to be used in the local repository
set -eEuxfo pipefail

if [ $# -ne 6 ]; then
    echo "Usage: $0 <local-repo> <remote-user> <remote-host> <remote-bare-repo-parent> <remote-checkout-parent> <remote-name>"
    exit 1
fi

LOCAL_REPO=$1
REMOTE_USER=$2
REMOTE_HOST=$3
REMOTE_BARE_REPO_PARENT=$4
REMOTE_CHECKOUT_PARENT=$5
REMOTE_NAME=$6

REPOSITORY_NAME=$(basename "$LOCAL_REPO")

echo "Removing remote $REMOTE_NAME from local repository ..."
cd "$LOCAL_REPO"
git remote remove "$REMOTE_NAME"

echo "Removing remote checkout repository $REMOTE_USER@$REMOTE_HOST:$REMOTE_CHECKOUT_PARENT/$REPOSITORY_NAME ..."
ssh "$REMOTE_USER@$REMOTE_HOST" "rm -rf $REMOTE_CHECKOUT_PARENT/$REPOSITORY_NAME"

echo "Removing remote bare repository $REMOTE_USER@$REMOTE_HOST:$REMOTE_BARE_REPO_PARENT/$REPOSITORY_NAME.git ..."
ssh "$REMOTE_USER@$REMOTE_HOST" "rm -rf $REMOTE_BARE_REPO_PARENT/$REPOSITORY_NAME.git"

echo "Remote repository deleted successfully."
