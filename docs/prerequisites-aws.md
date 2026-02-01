# AWS Prerequisites

In addition to the common prerequisites listed in [Create a Virtual Machine](./create-vm.md), all AWS environments require

1. AWS CLI installed
2. AWS account with programmatic access configured
3. SSH key pairs
4. Ansible Vault setup for encrypted secrets

## 1. Install AWS CLI

Follow the instructions for your operating system to install the latest supported AWS CLI:

[Installing or updating to the latest version of the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## 2. AWS Credentials Setup

If you don't have an AWS account yet, follow these steps:

### 1. Create AWS Account

- Go to [aws.amazon.com](https://aws.amazon.com) and click "Create an AWS Account"
- Provide email, password, and account name
- Enter payment information (required even for free tier)
- Verify phone number and identity

### 2. Create IAM User for Programmatic Access

- Log into AWS Console → Go to IAM service
- Click "Users" → "Create user"
- Username: `ansible-automation` (or similar)
- Select "Programmatic access" (API access)

### 3. Set Permissions

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

### 4. Get Access Keys

- After user creation, **immediately download** the CSV file with:
  - Access Key ID
  - Secret Access Key
- Store these securely - you cannot retrieve the secret key again

### 5. Configure Credentials and Default Region Locally

Configure your AWS credentials using one of these methods:

> [!IMPORTANT]
> **Region Selection**: The `AWS_DEFAULT_REGION` environment variable determines which AWS region is used for:
>
> - Instance provisioning
> - Inventory queries (critical for performance)
> - Resource management
>
> **Performance Impact**: Setting `AWS_DEFAULT_REGION` to match your instance locations is essential for fast inventory operations (~1 second vs 16+ seconds). If not set, defaults to `eu-north-1`.

#### Option 1: Environment Variables (Recommended)

```shell
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="eu-north-1"  # or your preferred region
```

#### Option 2: AWS CLI Configuration

```shell
aws configure
```

> [!NOTE]
> When using `aws configure`, the region you specify is saved in your AWS configuration.

It is required to transfer the configuration to the environment variable `AWS_DEFAULT_REGION`:

```shell
# Extract region from AWS CLI config and set as environment variable
export AWS_DEFAULT_REGION=$(aws configure get region)

# Verify the region is set correctly
echo "Using AWS region: $AWS_DEFAULT_REGION"
```

This should match where you plan to create instances for optimal inventory performance.

## 3. SSH Key Pair Setup

Create or import an SSH key pair in the AWS EC2 console:

1. Go to EC2 → Key Pairs in your [AWS console](https://console.aws.amazon.com/ec2)
2. Either create a new key pair or import your existing public key
3. Configure the key pair name in [/inventories/group_vars/all/vars.yml](../../inventories/group_vars/all/vars.yml) (see section on Ansible Vault Setup below)
4. Ensure you have the corresponding private key file (`.pem` format) in your `~/.ssh/` directory with permissions restricted to 600: `chmod 600 ~/.ssh/*pem`
5. Set a password for the key file: `ssh-keygen -p -f ~/.ssh/YOUR_KEY_FILE.pem`

> [!IMPORTANT]
> **Windows AMI Limitation**: AWS does not support ED25519 key pairs for Windows AMIs. If you plan to use Windows Server instances, you must use RSA (minimum 2048-bit) or ECDSA key pairs. For Linux AMIs, all key types including ED25519 are supported.

## 4. Ansible Vault Setup for Encrypted Secrets

Follow the instructions in section [Important concepts](./important-concepts.md) to update your secrets in `.envrc` and in [./inventories/group_vars/all/vars.yml](./inventories/group_vars/all/vars.yml).

---

Next: [Work with a Virtual Machine](./work-with-vm.md)
Up: [Create a Virtual Machine](./create-vm.md)
