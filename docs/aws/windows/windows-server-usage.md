# Windows Server Usage Guide

## Prerequisites

The section **Prerequisites** in the parent [AWS Documentation](../../aws.md) file explains how to setup the prerequisites.

## Create the VM

```bash
ansible-playbook provision-aws-windows.yml --vault-password-file ansible-vault-password.txt
```

Replace `stefan@fangorn` with the name of your AWS key pair (without the `.pem` extension).

**Expected time**: 15-20 minutes (Windows takes longer to boot than Linux)

## Verify the Setup

```shell
# Show the inventory
ansible-inventory -i inventories/aws/aws_ec2.yml --graph
```

Before executing the other commands in this section, load your AWS key into your SSH agent:

```shell
ssh-add ~/.ssh/stefan@fangorn.pem
```

Then run the following commands to verify the setup:

```shell
# Check whether the server can be reached
ansible aws_windows -i ./inventories/aws/aws_ec2.yml -m win_command -a 'whoami'
```

You can also SSH directly to the instance. The value of `IPV4_ADDRESS` is described in [Obtain Remote IP Adress](../../obtain-remote-ip-address.md).

```shell
ssh Administrator@$IPV4_ADDRESS
```

> [!IMPORTANT]
> The security group is configured to allow both SSH (port 22) and RDP (port 3389) access only from your current public IP address. If your IP changes, you may need to update the security group rules in the AWS console.

## Configure Windows Server

```shell
ansible-playbook -i inventories/aws/aws_ec2.yml  --vault-password-file ansible-vault-password.txt configure-aws-windows.yml
```

**Expected time**: 5-10 minutes

## Connect to the Windows Desktop using RDP

Use the `Administrator` account to connect via an RDP compatible client.

## Delete teh VM

To delete the VM, use the following command:

```shell
ansible-playbook destroy-aws-windows.yml
```

You can verify that all resources are deleted in your [AWS EC2 console](https://console.aws.amazon.com/ec2/).
