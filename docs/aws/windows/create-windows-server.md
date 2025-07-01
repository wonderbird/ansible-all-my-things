# Windows Server Usage Guide

## Prerequisites

The section **Prerequisites** in the parent [AWS Documentation](../../aws.md) file explains how to setup the prerequisites.

## Create the VM

```bash
ansible-playbook provision-aws-windows.yml --vault-password-file ansible-vault-password.txt
```

> [!IMPORTANT]
> Only after some 3 minutes, SSH will ask you to confirm the host key.
>
> The delay is caused by the long time a Windows instance requires to boot.

**Expected time**: 5 minutes

## Verify the Setup

```shell
# Show the inventory
ansible-inventory --graph
```

Before executing the other commands in this section, load the configured key into your SSH agent:

```shell
ssh-add ~/.ssh/stefan@fangorn.pem
```

Then run the following commands to verify the setup:

```shell
# Check whether the server can be reached
ansible windows -m win_command -a 'whoami'
```

You can also SSH directly to the instance. The value of `IPV4_ADDRESS` is described in [Obtain Remote IP Adress](../../obtain-remote-ip-address.md).

```shell
ssh Administrator@$IPV4_ADDRESS
```

> [!IMPORTANT]
> The security group is configured to allow both SSH (port 22) and RDP (port 3389) access only from your current public IP address. If your IP changes, you may need to update the security group rules in the AWS console.

## Connect using RDP

Use the `Administrator` account to connect via an RDP compatible client.

## Delete teh VM

To delete the VM, use the following command:

```shell
ansible-playbook destroy-aws-windows.yml
```

You can verify that all resources are deleted in your [AWS EC2 console](https://console.aws.amazon.com/ec2/).
