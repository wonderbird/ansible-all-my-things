# Test system using the Vagrant Docker Provider

This test system uses the Vagrant / Docker Provider stack described in
[boos2025b](../../README.md#references).

## Warning: Refresh SSH Keys after cloning this repository

The SSH keys in [./ssh_host_keys/](./ssh_host_keys/) and [../ssh_user_key/](../ssh_user_key/) are published on GitHub. Thus, they are known to the entire world! If you use these keys, you risk being hacked.

Please generate fresh keys before building the Dockerfile in this directory:

```shell
cd ./test

# create new host keys before building the docker container(s)
ssh-keygen -q -N "" -t rsa -b 4096 -f ./ssh_host_keys/ssh_host_rsa_key -C root@testlab
ssh-keygen -q -N "" -t ecdsa -f ./ssh_host_keys/ssh_host_ecdsa_key -C root@testlab
ssh-keygen -q -N "" -t ed25519 -f ./ssh_host_keys/ssh_host_ed25519_key -C root@testlab

# create a new key for the "vagrant"user
ssh-keygen -q -N "" -t ecdsa -b 521 -f ../ssh_user_key/id_ecdsa -C vagrant@testlab
```

## Prerequisites

Install the Vagrant / Docker Provider stack as described in
[boos2025b](../../README.md#references).

Configure your public key for connecting to the VM as described in the section about secrets in [/docs/important-concepts.md](../../docs/important-concepts.md).

Load the SSH key matching the `my_ssh_public_key` configured in [/inventories/group_vars/all/vars.yml](../../inventories/group_vars/all/vars.yml) into your SSH agent.

## Running the test system

Launch the test system with

```shell
vagrant up
```

Once everything is installed, you can connect to the test system with

```shell
ssh -i ../ssh_user_key/id_ecdsa galadriel@localhost -p 2223
```

(note that you can also use the `vagrant ssh` command).

When you are done, stop the test system with

```shell
vagrant halt
```

## References

References are listed in [/README.md](../../README.md#references).
