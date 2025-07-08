# Create a Virtual Machine

Currently the following virtual machines can be created:

- Windows Server 2025 on Amazon AWS EC2,
- Ubuntu 24.04 LTS on Amazon AWS EC2 or on Hetzner Cloud.

## Prerequisites

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

Please follow the instructions in the [AWS](./aws/aws.md) documentation to create and configure an AWS account including an SSH key pair.

### 3. Provider-Specific Prerequisites

Some prerequisites differ by provider. Refer to the corresponding documentation to complete the setup:

- [AWS EC2](./aws/aws.md)
- [Hetzner Cloud](./hcloud/create-linux-vm.md)

The following provisioners create virtual machines on your localhost:

- [Vagrant with Docker](../test/docker/README.md)
- [Vagrant with Tart](../test/tart/README.md)

--

Next: [Work with a Virtual Machine](../work-with-vm.md)
