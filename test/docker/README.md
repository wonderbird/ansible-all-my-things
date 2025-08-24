# Test system using the Vagrant Docker Provider

This test system uses the Vagrant / Docker Provider stack described in
[boos2025b](../../README.md#references).

## Prerequisites

Install the Vagrant / Docker Provider stack as described in
[boos2025b](../../README.md#references).

Configure your public key for connecting to the VM as described in the section about secrets in [/docs/important-concepts.md](../../docs/important-concepts.md).

Load the SSH key matching the `my_ssh_public_key` configured in [/inventories/group_vars/all/vars.yml](../../inventories/group_vars/all/vars.yml) into your SSH agent.

## Provisioning the Test System

Launch and install the test system with

```shell
# Provision the system
vagrant up

cd ../..

# Install packages for this particular system type
ansible-playbook ./configure-linux.yml --skip-tags "not-supported-on-vagrant-arm64,not-supported-on-vagrant-docker"
```

## Limitations

### Feature Validation Restrictions

This Docker environment provides **fast testing for basic automation** but cannot validate all system features due to container limitations.

**What's Limited**: [AI agent safety features](../../docs/use_cases.md#ai-agent-safety-on-development-systems) that require kernel-level security cannot be tested in containers.

**For Complete Testing**: Use [VM-based testing](../../docs/use_cases.md#vm-based-testing-complete--local) or [cloud-based testing](../../docs/use_cases.md#cloud-based-testing-production-identical) environments instead.

See [Development Environment Options](../../docs/use_cases.md#development-environment-options) for guidance on choosing the right testing approach.

## References

References are listed in [/README.md](../../README.md#references).
