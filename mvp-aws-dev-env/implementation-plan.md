# Implementation Plan: AWS Development Environment

## Architecture Overview

Following the existing Hetzner Cloud pattern, the AWS implementation will consist of:

```
ansible-all-my-things/
├── provision-aws.yml              # Main provisioning playbook (mirrors provision.yml)
├── destroy-aws.yml               # Destruction playbook (mirrors destroy.yml)
├── configure-aws.yml             # Configuration playbook (mirrors configure.yml)
├── provisioners/
│   └── aws-ec2.yml              # AWS EC2 provisioning logic (mirrors hcloud.yml)
└── inventories/
    └── aws/
        ├── aws_ec2.yml          # Dynamic inventory plugin config
        └── group_vars/
            └── aws_dev/
                └── vars.yml     # AWS-specific variables
```

## Implementation Steps

### Step 1: Create AWS Provisioner
**File**: `provisioners/aws-ec2.yml`
- Use `amazon.aws.ec2_instance` module to create EC2 instance
- Configure security group for SSH access
- Set up key pair for SSH authentication
- Tag instance with `ansible_group: aws_dev` for inventory grouping
- Wait for instance to become reachable

### Step 2: Create Dynamic Inventory
**File**: `inventories/aws/aws_ec2.yml`
- Configure `amazon.aws.aws_ec2` inventory plugin
- Group instances by `ansible_group` tag
- Set hostnames to use public IP addresses

### Step 3: Create Main Playbooks
**Files**: `provision-aws.yml`, `configure-aws.yml`, `destroy-aws.yml`
- `provision-aws.yml`: Import aws-ec2.yml provisioner + configure-aws.yml
- `configure-aws.yml`: Reuse existing setup playbooks with AWS-specific vars
- `destroy-aws.yml`: Clean up EC2 instance, security group, and SSH keys

### Step 4: AWS-Specific Configuration
**File**: `inventories/aws/group_vars/aws_dev/vars.yml`
- Define AWS region, instance type, AMI ID
- Configure SSH key name and security group settings
- Set user variables for Ubuntu (default user: ubuntu)

## Required AWS Permissions

The AWS IAM user/role needs these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:RunInstances",
                "ec2:TerminateInstances",
                "ec2:DescribeInstances",
                "ec2:DescribeImages",
                "ec2:DescribeKeyPairs",
                "ec2:DescribeSecurityGroups",
                "ec2:CreateSecurityGroup",
                "ec2:DeleteSecurityGroup",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:CreateTags",
                "ec2:DescribeTags"
            ],
            "Resource": "*"
        }
    ]
}
```

## Environment Setup

### Prerequisites
1. AWS account with programmatic access
2. AWS CLI configured or environment variables set:
   ```bash
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"
   export AWS_DEFAULT_REGION="eu-north-1"  # or preferred region
   ```
3. Install AWS Ansible collection:
   ```bash
   ansible-galaxy collection install amazon.aws
   ```

### SSH Key Setup
- Create or import SSH key pair in AWS EC2 console
- Note the key pair name for configuration
- Ensure local private key is available for SSH access

## Usage Workflow

### Provision Environment
```bash
# Set AWS credentials (if not already configured)
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="eu-north-1"

# Provision and configure the AWS development environment
ansible-playbook --vault-password-file ansible-vault-password.txt ./provision-aws.yml
```

### Verify Setup
```bash
# Show the inventory
ansible-inventory -i inventories/aws/aws_ec2.yml --graph

# Check connectivity
ansible aws_dev -i inventories/aws/aws_ec2.yml -m shell -a 'whoami' --extra-vars "ansible_user=ubuntu"
```

### Work Session
```bash
# SSH into the instance
ssh -i ~/.ssh/your-aws-key.pem ubuntu@$(ansible-inventory -i inventories/aws/aws_ec2.yml --list | jq -r '.aws_dev.hosts[0]')
```

### Destroy Environment
```bash
# Destroy all AWS resources
ansible-playbook -i inventories/aws/aws_ec2.yml ./destroy-aws.yml
```

## Cost Optimization Features

1. **Automatic Termination**: Destroy playbook removes all billable resources
2. **Small Instance**: t3.micro eligible for free tier (first 12 months)
3. **GP3 Storage**: More cost-effective than GP2
4. **No Elastic IP**: Use dynamic public IP to avoid charges
5. **Single AZ**: No multi-AZ redundancy needed for development

## Security Considerations

1. **Security Group**: Restrict SSH access to user's current IP
2. **Key-based Auth**: No password authentication
3. **Default VPC**: Leverage AWS default security settings
4. **Instance Metadata**: Use IMDSv2 for enhanced security
5. **Regular Destruction**: Minimize attack surface by not keeping instances running

## Differences from Hetzner Implementation

| Aspect | Hetzner Cloud | AWS EC2 |
|--------|---------------|---------|
| Inventory Plugin | `hetzner.hcloud.hcloud` | `amazon.aws.aws_ec2` |
| Instance Module | `hetzner.hcloud.server` | `amazon.aws.ec2_instance` |
| Default User | `root` | `ubuntu` |
| SSH Key | Hetzner SSH key name | AWS key pair name |
| Networking | Automatic | Security group required |
| Tagging | Labels | Tags |
| Cost Model | Hourly billing | Per-second billing (min 60s) |

## Testing Strategy

1. **Dry Run**: Test provisioning with `--check` flag
2. **Minimal Config**: Start with t3.micro in free tier
3. **Automated Cleanup**: Ensure destroy playbook works reliably
4. **Cost Monitoring**: Set up AWS billing alerts
5. **Integration Test**: Verify existing playbooks work with AWS instances
