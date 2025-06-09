# Create a developer VM with AWS EC2

## Prerequisites

You need an AWS account with programmatic access configured.

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
- Attach existing policy: `AmazonEC2FullAccess`

**For production (minimal permissions):**
- Create custom policy with these permissions:
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

**Option 1: Environment Variables (Recommended)**
```shell
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-east-1"  # or your preferred region
```

**Option 2: AWS CLI Configuration**
```shell
# Install AWS CLI if needed
pip install awscli

# Configure credentials
aws configure
```

#### 6. Test Access
```shell
# Test connection
aws ec2 describe-regions
```

>[!NOTE]
> The free tier includes 750 hours/month of t3.micro instances for the first 12 months, which covers this project's usage perfectly.

### SSH Key Pair Setup

Create or import an SSH key pair in the AWS EC2 console:

1. Go to EC2 → Key Pairs in your AWS console
2. Either create a new key pair or import your existing public key
3. Note the key pair name for configuration
4. Ensure you have the corresponding private key file (`.pem` format) in your `~/.ssh/` directory

### Install AWS Ansible Collection

Install the required Ansible collection:

```shell
ansible-galaxy collection install amazon.aws
```

### Configure Secrets

Follow the instructions in section [Important concepts](./important-concepts.md) to update your secrets in [./ansible-vault-password.txt](./ansible-vault-password.txt) and in [./playbooks/vars-secrets.yml](./playbooks/vars-secrets.yml).

## Create the VM

Create the EC2 instance using the following command, specifying your AWS SSH key name:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt \
  -e "aws_ssh_key_name=your-key-pair-name" \
  ./provision-aws.yml
```

Replace `your-key-pair-name` with the name of your AWS key pair (without the `.pem` extension).

The provisioner will:
- Automatically detect your current public IP for security group access
- Create a security group allowing SSH access from your IP only
- Launch a t3.micro Ubuntu 24.04 LTS instance (free tier eligible)
- Configure 20GB GP3 storage with automatic deletion on termination
- Wait for SSH to become available

After provisioning, the setup will take approximately 10-15 minutes to complete the full configuration.

## Verify the Setup

Once provisioning is complete, verify the setup:

```shell
# Show the inventory
ansible-inventory -i inventories/aws/aws_ec2.yml --graph

# Check whether the server can be reached
ansible aws_dev -i inventories/aws/aws_ec2.yml -m shell -a 'whoami'

# Test with your desktop user
ansible aws_dev -i inventories/aws/aws_ec2.yml -m shell -a 'whoami' --extra-vars "ansible_user=gandalf"
```

You can also SSH directly to the instance:

```shell
ssh -i ~/.ssh/your-key-pair-name.pem ubuntu@<instance-public-ip>
```

The instance public IP will be displayed in the provisioning output.

>[!IMPORTANT]
> The security group is configured to allow SSH access only from your current public IP address. If your IP changes, you may need to update the security group rules in the AWS console.

## Architecture Benefits

This AWS EC2 environment provides:

- **Cross-Architecture Access**: Run amd64 (x86_64) tools unavailable on Apple Silicon
- **Secure Isolation**: Test untrusted software safely away from your local machine
- **Cost Efficiency**: t3.micro instances are free tier eligible, with complete resource cleanup
- **Development Foundation**: Stepping stone for future Windows Server support

## Delete the VM

To delete the VM and all associated resources, use the following command:

```shell
# Backup your configuration (optional)
ansible-playbook --vault-password-file ansible-vault-password.txt ./backup.yml

# Destroy all AWS resources
ansible-playbook ./destroy-aws.yml
```

The destroy playbook will:
- Terminate all EC2 instances created by Ansible
- Delete the associated security group
- Verify complete resource cleanup
- Ensure zero ongoing AWS costs

You can verify that all resources are deleted in your [AWS EC2 console](https://console.aws.amazon.com/ec2/).

## Cost Information

**Estimated monthly costs (when actively used):**
- t3.micro instance: ~$6.50/month (free tier: first 750 hours/month for 12 months)
- 20GB GP3 storage: ~$1.60/month (only when instance is running)
- Data transfer: Minimal for development use

**Total: ~$8-10/month maximum, $0 when not in use**

The complete destroy process ensures no ongoing costs when the environment is not needed.
