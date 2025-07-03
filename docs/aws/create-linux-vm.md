# AWS Linux Server Usage Guide

## Prerequisites

The section **Prerequisites** in the parent [AWS Documentation](./aws.md) file explains how to setup the prerequisites.

## Create the VM

```shell
ansible-playbook provision-aws-linux.yml --vault-password-file ansible-vault-password.txt
```

After provisioning, the setup will take approximately 10-15 minutes to complete the full configuration.

## Verify the Setup

```shell
# Show the inventory
ansible-inventory --graph
```

Before executing the other commands in this section, load the configured key into your SSH agent:

```shell
ssh-add ~/.ssh/user@host.pem
```

Then run the following commands to verify the setup:

```shell
# Check whether the server can be reached
ansible linux -m shell -a 'whoami'
```

You can also SSH directly to the instance. The value of `IPV4_ADDRESS` is described in [Obtain Remote IP Adress](../../obtain-remote-ip-address.md).

```shell
ssh ubuntu@$IPV4_ADDRESS
```

> [!IMPORTANT]
> The security group is configured to allow SSH access only from your current public IP address. If your IP changes, you may need to update the security group rules in the AWS console.

## Delete the VM

To delete the VM and all associated resources, use the following command:

```shell
ansible-playbook ./destroy-aws.yml
```

---

Next: [Work with a Virtual Machine](../work-with-vm.md)
Up: [AWS](./aws.md)
