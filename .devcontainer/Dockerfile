# syntax=docker/dockerfile:1

ARG ARCH=aarch64
#ARG ARCH=x86_64

# The latest version of the aws cli v2 is incompatible with alpine,
# thus we use the slim python image instead.
# An alternative would be to install an older version using the alpine
# package manager.
FROM docker.io/python:slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        openssh-client \
        gpg \
        unzip \
    && rm -rf /var/lib/apt/lists/*

# Follow the prerequisistes for cloud vms
# as described in docs/create-vm.md:
#
#   rm -rf ./venv-in-docker
#   python -m venv ./venv-in-docker
#   source ./venv-in-docker/bin/activate
#   pip3 install -r requirements.txt
#   ansible-galaxy collection install -r requirements.yml

# Install the aws cli and set up AWS
# as described in docs/prerequisistes-aws.md
# which delegates the installation to
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html#getting-started-install-instructions
#
#   mkdir -p /tmp/awscli
#   cd /tmp/awscli
#   curl "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip" -o "awscliv2.zip"
#   gpg --import /workspaces/ansible-all-my-things/.devcontainer/awscliv2-public-key.asc
#   curl -o awscliv2.sig https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip.sig
#   gpg --verify awscliv2.sig awscliv2.zip
#   unzip awscliv2.zip
#   ./aws/install

# Load the private SSH key for AWS EC2 instances
#
#   ssh-add /workspaces/ansible-all-my-things/.devcontainer/root@docker.boos.local.pem