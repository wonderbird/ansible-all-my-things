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
source ./configure.sh
```

## Create a Cloud VM

Create the server using the following command:

```shell
ansible-playbook provision.yml --vault-password-file ansible-vault-password.txt --extra-vars "provider=hcloud platform=linux"
```

The `provider` parameter can be one of

- `aws`
- `hcloud`

`platform` can be one of

- linux
- windows

> [!NOTE]
> Windows is only supported by AWS.

To pick a good combination, use the following guidelines:

- If you want to run Windows, choose `provider=aws platform=windows`
- If you want to run Linux, prefer `provider=hcloud platform=linux`
- If there are no virtual machines available on `hcloud`, then try aws: `provider=aws platform=linux`

After about 1 - 2 minutes, you will be asked to add the SSH key of the new server to your local `~/.ssh/known_hosts` file.

After that, the setup will take another 10 - 15 minutes.

### Note: Windows requires manual setup

The Windows Server provides a clean installation with SSH, RDP access, and the Chocolatey package manager. However, unlike the Linux systems, **it does not include**:

- Pre-installed development applications and tools
- Automated backup/restore of user configurations
- Keyring restoration with saved passwords
- Ready-to-use development environment

**Expected setup time**: 1-2 hours to manually install and configure your development tools and applications.

**Recommendation**: Use Windows Server when you specifically need Windows-only applications. For general development work, prefer the Linux systems which provide a complete, instantly-ready development environment with automatic configuration restoration.

## Verify the Setup

```shell
# Show the inventory
ansible-inventory --graph
```

The inventory will show the host name for the provisioned instance. The host name is unique for each provider and platform combination. Have a look at the table in the [/README.md](../README.md) to see the possible combinations of provider, platform and host name.

Before executing the other commands in this section, load the configured key into your SSH agent:

```shell
ssh-add ~/.ssh/user@host.pem
```

Then run the following commands to verify the setup:

```shell
# Check whether the server can be reached
# Linux variant:
ansible linux -m shell -a 'whoami' --extra-vars "ansible_user=galadriel"

# Windows variant using win_command
ansible windows -m win_command -a 'whoami'
```

>[!IMPORTANT]
> You might want to add additional SSH keys to the `authorized_keys` files on
> the server.

You can also SSH directly to the instance. `IPV4_ADDRESS` is set by sourcing [/configure.sh](../configure.sh):

```shell
# Configure your shell to work with the VM
source ./configure.sh

# On Linux, galadriel is the default desktop user
ssh galadriel@$IPV4_ADDRESS

# On Windows, only Administrator is configured as a user
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
ansible-playbook ./destroy.yml
```

--

Next: [Work with a Virtual Machine](./work-with-vm.md)
