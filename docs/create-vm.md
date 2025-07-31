# Create a Virtual Machine

## Virtual Machines on localhost

The following provisioners create virtual machines running Ubuntu on your localhost:

- [Vagrant with Docker](../test/docker/README.md)
- [Vagrant with Tart](../test/tart/README.md)

## Virtual Machines on Cloud Providers

Currently the following virtual machines can be created:

- Windows Server 2025 on Amazon AWS EC2,
- Ubuntu 24.04 LTS on Amazon AWS EC2 or on Hetzner Cloud.

> [!IMPORTANT]
> For AWS, the security group is configured to allow SSH access only from your current public IP address. If your IP changes, you may need to update the security group rules in the AWS console.

## Prerequisites for Cloud VMs

### 1. Install Dependencies

First, install the required Python packages and Ansible collections:

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Ansible collections
ansible-galaxy collection install -r requirements.yml
```

### 2. SSH Key Pair Setup

You need an SSH key pair to log into the VMs.

All providers allow registering a public key and associate it with an identifier. Recommendation: Use an ID like `user@host` where `user` and `host` are associated with your user account on the computer running your ansible commands.

Because Windows instances hosted on Amazon AWS EC2 only support RSA and ECDSA keys, the recommended approach is to set up Amazon AWS first. Amazon allows to create an RSA key which you can reuse for your Hetzner Cloud project.

Please follow the instructions in the [AWS](./prerequisites-aws.md) documentation to create and configure an AWS account including an SSH key pair.

### 3. Provider-Specific Prerequisites

Some prerequisites differ by provider. Refer to the corresponding documentation to complete the setup:

- [AWS EC2](./prerequisites-aws.md)
- [Hetzner Cloud](./prerequisites-hcloud.md)

Once you have configured the prerequisites for both providers, you can set the required environment variables as follows:

```shell
# This statement assumes that you are using the aws cli to configure your provider defaults
echo -n "hcloud API token: "; read -s HCLOUD_TOKEN; export HCLOUD_TOKEN; export AWS_DEFAULT_REGION=$(aws configure get region); echo "\nUsing AWS region: $AWS_DEFAULT_REGION"
```

## Create a Cloud VM

Create the server using the following command:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./provision.yml --extra-vars "provider=hcloud platform=linux"
```

The `provider` parameter can be one of

- `aws`
- `hcloud`

`platform` can be one of

- linux
- windows

> [!NOTE]
> Windows is only supported by AWS.

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
# Linux variant:
ansible linux -m shell -a 'whoami' --extra-vars "ansible_user=gandalf" --vault-password-file "ansible-vault-password.txt"

# Windows variant using win_command
ansible windows -m win_command -a 'whoami' --vault-password-file "ansible-vault-password.txt"
```

>[!IMPORTANT]
> You might want to add additional SSH keys to the `authorized_keys` files on
> the server.

You can also SSH directly to the instance. `IPV4_ADDRESS` is set by sourcing [/configure.sh](../configure.sh):

```shell
# Configure your shell to work with the VM
source ./configure.sh HOSTNAME

# On Linux, galadriel is the default desktop user
ssh galadriel@$IPV4_ADDRESS

# On Windows, only Administrator is configured
ssh Administrator@$IPV4_ADDRESS
```

## Connect using RDP

Connect via an RDP compatible client. For Linux, use the `galadriel` user, on Windows connect as `Administrator`.

## Delete the VM

To delete the VM and all associated resources, use the following command:

```shell
# Backup your configuration
ansible-playbook --vault-password-file ansible-vault-password.txt ./backup.yml

# Destroy
ansible-playbook --vault-password-file ansible-vault-password.txt ./destroy.yml
```

--

Next: [Work with a Virtual Machine](./work-with-vm.md)
