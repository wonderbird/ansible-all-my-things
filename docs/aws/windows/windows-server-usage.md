# Windows Server Usage Guide

## Prerequisites

The section **Prerequisites** in the parent [AWS Documentation](../../aws.md) file explains how to setup the prerequisites.

## Create the VM

```bash
ansible-playbook provision-aws-windows.yml -e "aws_ssh_key_name=user@host" --vault-password-file ansible-vault-password.txt -vvv
```

Replace `user@host` with the name of your AWS key pair (without the `.pem` extension).

**Expected time**: 15-20 minutes (Windows takes longer to boot than Linux)

## Verify the Setup

```shell
# Show the inventory
ansible-inventory -i inventories/aws/aws_ec2.yml --graph

# Check whether the server can be reached
ansible aws_dev -i inventories/aws/aws_ec2.yml -m shell -a 'whoami' --extra-vars "ansible_user=ubuntu aws_ssh_key_name=user@host"
```

You can also SSH directly to the instance. The value of `IPV4_ADDRESS` is described in [Obtain Remote IP Adress](../../obtain-remote-ip-address.md).

```shell
ssh Administrator@$IPV4_ADDRESS
```

> [!IMPORTANT]
> The security group is configured to allow both SSH (port 22) and RDP (port 3389) access only from your current public IP address. If your IP changes, you may need to update the security group rules in the AWS console.

## Configure Windows Server

```shell
# Configure Windows Server and prepare for Claude Desktop
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
