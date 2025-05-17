# Test systems

## Overview

The test systems use Vagrant.

- [docker](docker/README.md): Vagrant with Docker Provider
- [tart](tart/README.md): Vagrant with Tart Provider

## Incompatibility

The Vagrantfiles in each folder skip incompatible playbooks by tags.

Linux homebrew does not support the arm64 (Apple Silicon) architecture.
The tag `not-supported-on-vagrant-arm64` is intended for playbooks incompatible
with this architecture.

The Docker Ubuntu image does not support the XFCE desktop environment.
Because the playbook works for the Tart provider, it is tagged with
`not-supported-on-vagrant-docker`.

## Run a test system

```shell
cd test/tart

# Initialize the local test system
vagrant up

# Verify the configuration
# The following command should show that ansible uses the user
# "gandalf" and the host name is "lorien"
ansible dev -m shell -a "whoami"

# Destroy the local test system
vagrant destroy -f
```
