#!/bin/sh
# Clone and set up ansible-all-my-things
#
set -euxf

cd /root
git clone https://github.com/wonderbird/ansible-all-my-things.git

cd /root/ansible-all-my-things
pip3 install --root-user-action=ignore -r requirements.txt
ansible-galaxy collection install -r requirements.yml
