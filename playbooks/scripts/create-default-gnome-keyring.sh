#!/bin/bash
# Setup a default GNOME keyring for the given user
#
# This script must be run as the user for whom the keyring is being created.
#
# USAGE: ./create-default-gnome-keyring.sh PASSWORD
#
# Adopted from
# https://unix.stackexchange.com/questions/473528/how-do-you-enable-the-secret-tool-command-backed-by-gnome-keyring-libsecret-an
set -Eeuxfo pipefail

USER_PASSWORD="$1"
if [ -z "$USER_PASSWORD" ]; then
    echo "Usage: $0 PASSWORD"
    exit 1
fi

echo "Creating default GNOME keyring for user: ${USER} with password: ${USER_PASSWORD}"

echo "Ensure the keyring directories exist"
DIRS=(
    "${HOME}/.cache"
    "${HOME}/.local/share/keyrings"
)

for dir in "${DIRS[@]}"; do
    mkdir -p "$dir"
    chown "${USER}:${USER}" "$dir"
    chmod 0700 "$dir"
done

echo "Start dbus message bus"
eval "$(dbus-launch --sh-syntax)"
export DBUS_SESSION_BUS_ADDRESS
export DBUS_SESSION_BUS_PID

echo "Create default keyring"
eval $(printf "${USER_PASSWORD}" | gnome-keyring-daemon --unlock)

echo "Start gnome-keyring-daemon"
eval $(printf "${USER_PASSWORD}" | /usr/bin/gnome-keyring-daemon --start)
