#!/bin/sh
# Install Hetzner hcloud CLI
#
# Documentation:
#   - [hcloud CLI GitHub repository](https://github.com/hetznercloud/cli)
#
set -euxf

ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    HCLOUD_RELEASE_ARCH="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    HCLOUD_RELEASE_ARCH="arm64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

# Fetch the latest release version from GitHub API
HCLOUD_VERSION=$(curl -s https://api.github.com/repos/hetznercloud/cli/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$HCLOUD_VERSION" ]; then
    echo "Failed to fetch latest hcloud version"
    exit 1
fi

echo "Installing hcloud ${HCLOUD_VERSION}..."

mkdir -p /root/hcloud
wget "https://github.com/hetznercloud/cli/releases/download/${HCLOUD_VERSION}/hcloud-linux-${HCLOUD_RELEASE_ARCH}.tar.gz" -O "/root/hcloud.tar.gz"
tar -xvzf /root/hcloud.tar.gz -C /root/hcloud
rm /root/hcloud.tar.gz
ln -s /root/hcloud/hcloud /usr/local/bin/hcloud
