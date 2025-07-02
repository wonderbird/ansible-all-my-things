# Linux Server Usage Guide

## Prerequisites

The section **Prerequisites** in the parent [AWS Documentation](../../aws.md) file explains how to setup the prerequisites.

## Create the VM

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./provision-aws.yml
```

Replace `stefan@fangorn` with the name of your AWS key pair (without the `.pem` extension).

After provisioning, the setup will take approximately 10-15 minutes to complete the full configuration.

## Verify the Setup

```shell
# Show the inventory
ansible-inventory -i inventories/aws/aws_ec2.yml --graph

# Check whether the server can be reached
ansible aws_dev -i inventories/aws/aws_ec2.yml -m shell -a 'whoami' --extra-vars "ansible_user=ubuntu aws_ssh_key_name=stefan@fangorn"
```

You can also SSH directly to the instance. The value of `IPV4_ADDRESS` is described in [Obtain Remote IP Adress](../../obtain-remote-ip-address.md).

```shell
ssh -i ~/.ssh/stefan@fangorn.pem ubuntu@$IPV4_ADDRESS
```

> [!IMPORTANT]
> The security group is configured to allow SSH access only from your current public IP address. If your IP changes, you may need to update the security group rules in the AWS console.

## Delete the VM

To delete the VM and all associated resources, use the following command:

```shell
# Backup your configuration (optional)
ansible-playbook --vault-password-file ansible-vault-password.txt ./backup.yml

# Destroy all AWS resources
ansible-playbook ./destroy-aws.yml
```

---

Up: [AWS](../../aws.md)
