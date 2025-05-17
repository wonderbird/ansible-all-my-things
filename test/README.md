# Test System

The test system uses the Vagrant / Docker Provider stack described in
[boos2025b](../README.md#references).

## Warning

The SSH keys in this project are known to the entire world! If you use these
keys, you risk being hacked.

Please generate fresh keys before building the Dockerfile in this directory:

```bash
cd ./test

# create new host keys before building the docker container(s)
ssh-keygen -q -N "" -t rsa -b 4096 -f ./ssh_host_keys/ssh_host_rsa_key -C root@testlab
ssh-keygen -q -N "" -t ecdsa -f ./ssh_host_keys/ssh_host_ecdsa_key -C root@testlab
ssh-keygen -q -N "" -t ed25519 -f ./ssh_host_keys/ssh_host_ed25519_key -C root@testlab

# create a new key for the "vagrant"user
ssh-keygen -q -N "" -t ecdsa -b 521 -f ./ssh_user_key/id_ecdsa -C vagrant@testlab
```

## Incompatibility

If a playbook is incompatible with my macOS arm64 (Apple Silicon) system,
it is tagged with `not-supported-on-vagrant-arm64` in
[../configure.yml](../configure.yml). The
[Vagrantfile](./Vagrantfile) skips these playbooks.

Unfortunately, the linux homebrew edition does not support the arm64
architecture. This means that you cannot use this test environment with
homebrew an Apple Silicon Macs.

Further it seems as if the docker Ubuntu image does not support the XFCE
desktop environment.

## Prerequisites

- I use a macOS system to test. Please let me know if you use a different
  system and need help.
- Install the Vagrant / Docker Provider stack as described in
  [boos2025b](../README.md#references).

## Run tests

```bash
cd test

# Initialize the local test system
vagrant up

# Verify the configuration
# The following command should show that ansible uses the user
# "gandalf" and the host name is "lorien"
ansible dev -m shell -a "whoami"

# Destroy the local test system
vagrant destroy -f
```

## References

References are listed in [/README.md](../README.md#references).
