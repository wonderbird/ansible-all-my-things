#!/bin/sh
# Clone and set up ansible-all-my-things
#
set -euxf

# Install ansible-core into isolated pipx venv so the runtime stage
# can copy /root/.local without needing pip or git at runtime.
pipx install ansible-core

cd /root
git clone https://github.com/wonderbird/ansible-all-my-things.git

cd /root/ansible-all-my-things
pipx inject ansible-core -r requirements.txt
ansible-galaxy collection install -r requirements.yml
