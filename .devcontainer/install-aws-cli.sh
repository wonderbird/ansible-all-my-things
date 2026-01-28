#!/bin/sh
# Install AWS CLI v2
#
# Documentation:
#   - [AWS CLI install and update instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
#
# Always installs latest version:
#   For maximum compatibility with AWS services, the latest version is always installed.
#
set -euxf

ARCH=$(uname -m)
gpg --import /tmp/installers/awscliv2-public-key.asc
mkdir -p /tmp/awscli
curl -o "/tmp/awscli/awscliv2.zip" "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip"
curl -o "/tmp/awscli/awscliv2.sig" "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip.sig"
gpg --verify --trust-model always /tmp/awscli/awscliv2.sig /tmp/awscli/awscliv2.zip
unzip /tmp/awscli/awscliv2.zip -d /tmp/awscli
/tmp/awscli/aws/install
rm -rf /tmp/awscli
