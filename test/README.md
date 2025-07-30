# Tests

## Manual Tests

At the moment, automatic tests are missing 😔.

The reason is that this project has been in a "proof of concept phase" until 2025-07-11.

Now the project is transitioning from a "Genesis" stage to a more mature "Custom Built" stage [wardley2020], [harrer2023]. Thus, existing manual tests are documented in this directory. Automated tests are planned.

### Test Suite Overview
The test suite covers provisioning, configuration, and integration testing across multiple environments:
- **Local testing**: Vagrant with Docker and Tart providers
- **Cloud testing**: AWS EC2 instances
- **Integration testing**: Group vars loading, inventory management, provisioner configuration

Each test case is self-documenting with clear prerequisites, execution steps, and verification procedures.

## Test systems

The test systems use Vagrant.

- [docker](docker/README.md): Vagrant with Docker Provider
- [tart](tart/README.md): Vagrant with Tart Provider

## Warning: Refresh SSH Keys after cloning this repository

The SSH keys in [./docker/ssh_host_keys/](./docker/ssh_host_keys/) and [./ssh_user_key/](./ssh_user_key/) are published on GitHub. Thus, they are known to the entire world! If you use these keys, you risk being hacked.

Please generate fresh keys before building the Dockerfile in this directory:

```shell
cd ./test

# create new host keys before building the docker container(s)
ssh-keygen -q -N "" -t rsa -b 4096 -f ./docker/ssh_host_keys/ssh_host_rsa_key -C root@testlab
ssh-keygen -q -N "" -t ecdsa -f ./docker/ssh_host_keys/ssh_host_ecdsa_key -C root@testlab
ssh-keygen -q -N "" -t ed25519 -f ./docker/ssh_host_keys/ssh_host_ed25519_key -C root@testlab

# create a new key for the "vagrant" user
ssh-keygen -q -N "" -t ecdsa -b 521 -f ./ssh_user_key/id_ecdsa -C vagrant@testlab
```

### A note on incompatibility

The `Vagrantfile`s in each folder skip incompatible playbooks by tags.

Linux homebrew does not support the arm64 (Apple Silicon) architecture.
The tag `not-supported-on-vagrant-arm64` is intended for playbooks incompatible
with this architecture.

The Docker Ubuntu image does not support the XFCE desktop environment.
Because the playbook works for the Tart provider, it is tagged with
`not-supported-on-vagrant-docker`.

## Using the Vagrant VMs

The individual files [tart/README.md](./tart/README.md) and [docker/README.md](./docker/README.mde) describe how to provision the corresponding VM.

The section **Verify the Setup** in [/docs/create-vm.md](../docs/create-vm.md) describes how to use the VMs.

## Stopping or Destroying a Vagrant VM

To pause using a VM, enter

```shell
vagrant halt
```

To delete a VM completely, consider backing it up first, then enter

```shell
vagrant destroy -f
```

## Quick Test Execution Guide

### Prerequisites
- Generate fresh SSH keys (see warning above)
- Ensure vault password file exists: `ansible-vault-password.txt`
- For AWS tests: Configure AWS credentials and SSH key

### Running Tests
Execute the test cases in the test folders:
- `test/docker/` - Docker-based Vagrant tests
- `test/tart/` - Tart-based Vagrant tests  
- `test/test_*.md` - Individual test procedures

### Test Execution Checklist
- [ ] SSH keys refreshed after repository clone
- [ ] Vault password file available
- [ ] AWS credentials configured (for AWS tests)
- [ ] Test environment matches test requirements
- [ ] Clean up resources after testing

### Troubleshooting
- **SSH connection issues**: Verify SSH keys are loaded in agent
- **Vault errors**: Check vault password file path and permissions
- **AWS errors**: Verify credentials and region configuration
- **Vagrant errors**: Check provider installation and system requirements

## AWS Instance Type Guidelines

### Recommended Instance Types for Testing
- **t3.micro**: Default choice for all AWS tests
  - Free tier eligible (subject to account limits)
  - Sufficient for most testing scenarios
  - Cost: ~$0.0104/hour
- **t3.small**: Use only when t3.micro is insufficient
  - For tests requiring more resources
  - Cost: ~$0.0208/hour

### Cost Considerations
- Always destroy AWS instances after testing
- Monitor AWS billing dashboard for unexpected charges
- Consider using AWS free tier for development accounts
- Use spot instances for longer-running tests when appropriate

## References

[wardley2020] S. Wardley, “Wardley Maps,” Learn Wardley Mapping. Accessed: Sep. 29, 2022. [Online]. Available: [https://learnwardleymapping.com/book/](https://learnwardleymapping.com/book/)

[harrer2023] M. Harrer, “Evolutionäre Softwarequalität,” presented at the OOP Konferenz, Feb. 09, 2023. [Online]. Available: [https://sigs-new.scoocs.co/event/63/stage/206/session/1729](https://sigs-new.scoocs.co/event/63/stage/206/session/1729)
