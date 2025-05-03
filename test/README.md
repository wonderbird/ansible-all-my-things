# Test System

The test system uses the Vagrant / Docker Provider stack described in
[boos2025]. To test the playbooks, run the following command:

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

## Prerequisites

- I use a macOS system to test. Please let me know if you use a different system and need help.
- Install the Vagrant / Docker Provider stack as described in [boos2025].

## Run tests

```bash
cd test

# Initialize the local test system
vagrant up

# Verify Playbooks
ansible-playbook ../playbooks/ubuntu-developer-vm.yml

# Destroy the local test system
vagrant destroy -f
```

## Fixing SSH host key issues

Your SSH client might report that the host identification for `localhost` has
changed. This is expected.

One of the following methods fixes the issue:

- Delete the offending keys from `~/.ssh/known_hosts` and get the new key by
  connecting with `ssh -i ./ssh_user_key/id_ecdsa -p 2223 vagrant@localhost`

- Add the line `ansible_ssh_common_args='-o StrictHostKeyChecking=no'` into the
  `[dev:vars]` section of the inventory file
  [../test/hosts.ini](../test/hosts.ini)

## References

References are listed in [/README.md](../README.md).
