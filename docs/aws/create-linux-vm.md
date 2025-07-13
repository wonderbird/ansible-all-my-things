# AWS Linux Server Usage Guide

> [!IMPORTANT]
> The security group is configured to allow SSH access only from your current public IP address. If your IP changes, you may need to update the security group rules in the AWS console.

## Prerequisites

The section **Prerequisites** in the parent [AWS Documentation](./aws.md) file explains how to setup the prerequisites.

## Create the VM

Create the server using the following command:

```shell
ansible-playbook provision.yml --vault-password-file ansible-vault-password.txt --extra-vars "provider=aws"
```

You will be asked to add the SSH key of the new server to your local
`~/.ssh/known_hosts` file.

After that, the setup will take some 10 - 15 minutes.

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
ansible dev -m shell -a 'whoami' --extra-vars "ansible_user=gandalf"

# Source .bash_profile to load the environment variables
ansible dev -m shell -a '. $HOME/.bash_profile; mob moo' --extra-vars "ansible_user=gandalf"
```

>[!IMPORTANT]
> You might want to add additional SSH keys to the `authorized_keys` files on
> the server.

You can also SSH directly to the instance. The value of `IPV4_ADDRESS` is described in [Obtain Remote IP Adress](../../obtain-remote-ip-address.md).

```shell
ssh galadriel@$IPV4_ADDRESS
```

## Delete the VM

To delete the VM and all associated resources, use the following command:

```shell
# Backup your configuration
ansible-playbook --vault-password-file ansible-vault-password.txt ./backup.yml

# Destroy
ansible-playbook ./destroy-aws.yml
```

---

Next: [Work with a Virtual Machine](../work-with-vm.md)
Up: [AWS](./aws.md)
