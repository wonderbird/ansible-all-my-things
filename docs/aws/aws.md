# AWS Documentation

This section covers using Amazon Web Services (AWS) EC2 for development environments.

## Available Environments

- [Create Linux VM](./create-linux-vm.md) - Complete setup guide for Ubuntu 24.04 LTS on AWS EC2
- [Create Windows VM](./create-windows-vm.md) - Provisioning and usage instructions for Windows Server 2025 on AWS EC2

## Prerequisites

In addition to the common prerequisites listed in [Create a Virtual Machine](../create-vm.md), all AWS environments require

1. AWS account with programmatic access configured
2. SSH key pairs
3. Ansible Vault setup for encrypted secrets

### AWS Credentials Setup

If you don't have an AWS account yet, follow these steps:

#### 1. Create AWS Account

- Go to [aws.amazon.com](https://aws.amazon.com) and click "Create an AWS Account"
- Provide email, password, and account name
- Enter payment information (required even for free tier)
- Verify phone number and identity

#### 2. Create IAM User for Programmatic Access

- Log into AWS Console → Go to IAM service
- Click "Users" → "Create user"
- Username: `ansible-automation` (or similar)
- Select "Programmatic access" (API access)

#### 3. Set Permissions

**For quick setup (broader permissions):**

Attach existing policy: `AmazonEC2FullAccess`

**For minimal permissions:**

Create custom policy with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances", "ec2:TerminateInstances",
        "ec2:DescribeInstances", "ec2:DescribeImages",
        "ec2:DescribeKeyPairs", "ec2:DescribeSecurityGroups",
        "ec2:CreateSecurityGroup", "ec2:DeleteSecurityGroup",
        "ec2:AuthorizeSecurityGroupIngress", "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

#### 4. Get Access Keys

- After user creation, **immediately download** the CSV file with:
  - Access Key ID
  - Secret Access Key
- Store these securely - you cannot retrieve the secret key again

#### 5. Configure Credentials Locally

Configure your AWS credentials using one of these methods:

##### Option 1: Environment Variables (Recommended)

```shell
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="eu-north-1"  # or your preferred region
```

##### Option 2: AWS CLI Configuration

```shell
# Configure credentials
# NOTE: I currently use eu-north-1 as the default region
#       and leave the default output format as None.
aws configure
```

#### 6. Test Access

```shell
# Test connection
aws ec2 describe-regions
```

> [!NOTE]
> The free tier includes 750 hours/month of t3.micro instances for the first 12 months, which covers this project's usage perfectly.

### 2. SSH Key Pair Setup

Create or import an SSH key pair in the AWS EC2 console:

1. Go to EC2 → Key Pairs in your AWS console
2. Either create a new key pair or import your existing public key
3. Configure the key pair name in [/playbooks/vars-secrets.yml](../../playbooks/vars-secrets.yml) (see section on Ansible Vault Setup below)
4. Ensure you have the corresponding private key file (`.pem` format) in your `~/.ssh/` directory with permissions restricted to 600: `chmod 600 ~/.ssh/*pem`

> [!IMPORTANT]
> **Windows AMI Limitation**: AWS does not support ED25519 key pairs for Windows AMIs. If you plan to use Windows Server instances, you must use RSA (minimum 2048-bit) or ECDSA key pairs. For Linux AMIs, all key types including ED25519 are supported.

### 3. Ansible Vault Setup for Encrypted Secrets

Follow the instructions in section [Important concepts](./important-concepts.md) to update your secrets in [./ansible-vault-password.txt](./ansible-vault-password.txt) and in [./playbooks/vars-secrets.yml](./playbooks/vars-secrets.yml).

## Status of Running VMs

You can check for running VMs in several ways:

### Unified Inventory (Recommended)

View all instances across all providers with:

```shell
ansible-inventory --graph
```

### AWS Console

Check the [AWS EC2 Console](https://console.aws.amazon.com/ec2/)

### AWS CLI

```shell
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"
```

---

Next: [Work with a Virtual Machine](../work-with-vm.md)
Up: [Create a Virtual Machine](../create-vm.md)
