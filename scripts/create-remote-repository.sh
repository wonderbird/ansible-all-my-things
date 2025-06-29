#!/bin/bash
# Bring a bare clone of the local repostory to a remote computer.
#
# - on the local compter, clone a normal repository into a temporary bare repository,
# - use rsync to copy the bare repository to the remote computer,
# - on the remote computer, create a new repository from the bare repository.
# - in the local repository, create a new remote pointing to the remote bare repository,
#   then fetch from it to synchronize the local repository.
#
# Prerequisites
#
# An SSH key for passwordless login to the remote computer is either
# loaded into the SSH agent or stored without password protection in the
# ~/.ssh directory.
#
# Usage
#
# ./create-remote-repository.sh <local-repo> <remote-user> <remote-host> <remote-bare-repo-parent> <remote-checkout-parent> <remote-name>
#
# Parameteres
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

echo "Creating temporary bare repository from $LOCAL_REPO ..."
TEMP_BARE_REPO=$(mktemp -d)/$REPOSITORY_NAME.git
git clone --bare "$LOCAL_REPO" "$TEMP_BARE_REPO"

echo "Copying bare repository to $REMOTE_USER@$REMOTE_HOST:$REMOTE_BARE_REPO_PARENT ..."
rsync -avz --stats --progress --delete --delete-during "$TEMP_BARE_REPO" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_BARE_REPO_PARENT"

echo "Cloning remote repository from remote bare repository ..."
ssh "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_CHECKOUT_PARENT && cd $REMOTE_CHECKOUT_PARENT && git clone $REMOTE_BARE_REPO_PARENT/$REPOSITORY_NAME.git $REPOSITORY_NAME"

echo "Cleaning up temporary bare repository ..."
rm -rf "$TEMP_BARE_REPO"

echo "Adding remote repository to local repository ..."
cd "$LOCAL_REPO"
git remote add "$REMOTE_NAME" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_BARE_REPO_PARENT/$REPOSITORY_NAME.git"
git fetch "$REMOTE_NAME"

echo "Remote repository created successfully at $REMOTE_USER@$REMOTE_HOST:$REMOTE_BARE_REPO_PARENT/$REPOSITORY_NAME.git"
