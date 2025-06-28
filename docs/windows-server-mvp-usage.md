# Windows Server MVP Usage Guide

## Overview

This guide covers the Windows Server MVP implementation for accessing Claude Desktop Application via AWS EC2 Windows Server 2025 instances.

## Prerequisites

1. **AWS Credentials**: Set up AWS credentials in environment variables
2. **Ansible Vault**: Configure secrets in `playbooks/vars-secrets.yml`
3. **SSH Key**: AWS SSH key pair configured

### Setup Secrets

If you haven't already set up the secrets file:

```bash
# Create ansible vault password file (if not exists)
echo -n "New ansible vault password: " \
  && read -s ANSIBLE_VAULT_PASSWORD \
  && echo "$ANSIBLE_VAULT_PASSWORD" > ./ansible-vault-password.txt

# Create secrets file from template (if not exists)
cp -v ./playbooks/vars-secrets-template.yml ./playbooks/vars-secrets.yml \
  && ansible-vault encrypt --vault-password-file ./ansible-vault-password.txt ./playbooks/vars-secrets.yml

# Edit secrets file to add Windows password
ansible-vault edit --vault-password-file ./ansible-vault-password.txt ./playbooks/vars-secrets.yml
```

**Important**: Set a strong password for `windows_admin_password` in the secrets file.

## Usage Workflow

### 1. Provision Windows Server

```bash
# Provision Windows Server 2025 with t3.large instance
ansible-playbook provision-aws-windows.yml -e "aws_ssh_key_name=stefan@fangorn" --vault-password-file ansible-vault-password.txt -vvv
```

**Expected time**: 15-20 minutes (Windows takes longer to boot than Linux)

### 2. Verify the Setup

Once provisioning is complete, verify the setup:

```shell
# Show the inventory
ansible-inventory -i inventories/aws/aws_ec2.yml --graph

# Check whether the server can be reached
ansible aws_dev -i inventories/aws/aws_ec2.yml -m shell -a 'whoami' --extra-vars "ansible_user=ubuntu aws_ssh_key_name=stefan@fangorn"
```

You can get the instance IP address:

```shell
# Get Windows Server IP address
export AWS_INSTANCE=lorien-windows
export IPV4_ADDRESS=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=$AWS_INSTANCE" "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].PublicIpAddress' --output text)
echo "IP of AWS instance $AWS_INSTANCE: $IPV4_ADDRESS"
```

> [!IMPORTANT]
> The security group is configured to allow both SSH (port 22) and RDP (port 3389) access only from your current public IP address. If your IP changes, you may need to update the security group rules in the AWS console.

### 3. Configure Windows Server

```bash
# Configure Windows Server and prepare for Claude Desktop
ansible-playbook -i inventories/aws/aws_ec2.yml configure-aws-windows.yml
```

**Expected time**: 5-10 minutes

### 4. Connect to Windows Server

You can connect using either SSH or RDP:

#### Option A: SSH Connection (Command Line Access)

```bash
# Connect via SSH
ssh Administrator@$IPV4_ADDRESS
# Or using the AWS instance name directly from inventory
ssh Administrator@$(aws ec2 describe-instances --filters "Name=tag:Name,Values=lorien-windows" "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].PublicIpAddress' --output text)
```

- **Server**: IP address shown in provision output
- **Username**: `Administrator`
- **Password**: From your `playbooks/vars-secrets.yml` file
- **Port**: `22` (SSH, enabled by default)

#### Option B: RDP Connection (Desktop Access)

Use any RDP client to connect:

- **Server**: IP address shown in provision output
- **Username**: `Administrator`
- **Password**: From your `playbooks/vars-secrets.yml` file
- **Port**: `3389` (RDP)

#### RDP Client Options

**Linux (Remmina)**:

```bash
# Install if not available
sudo apt install remmina remmina-plugin-rdp

# Connect
remmina
# Enter server IP, username: Administrator, password from vault
```

**macOS (Microsoft Remote Desktop)**:

- Download from Mac App Store
- Add PC with server IP
- Username: Administrator, password from vault

**Windows (Built-in)**:

```cmd
mstsc
# Enter server IP, username: Administrator, password from vault
```

### 5. Install Claude Desktop (Manual Step)

Once connected via RDP (SSH cannot be used for GUI applications):

1. Open Microsoft Edge browser
2. Navigate to: `https://claude.ai/download`
3. Download the Windows installer
4. Run the installer
5. Claude Desktop will be available in Start Menu

### 6. Use Claude Desktop

- Launch Claude Desktop from Start Menu
- Sign in with your Claude account
- Application is ready for use

### 7. Destroy Environment (Important!)

When finished, destroy the environment to stop costs:

```bash
ansible-playbook destroy-aws-windows.yml
```

**Expected time**: 2-5 minutes

## Cost Information

### MVP Costs (t3.large)

- **Instance**: ~$0.0832/hour
- **Storage**: ~$4/month (50GB)
- **Total if running 24/7**: ~$64/month

### Typical Usage Costs

- **2-3 hour session**: ~$0.25
- **10-15 hours/week**: ~$15/month
- **Always destroy when not in use**

## Troubleshooting

### SSH Connection Issues

1. **Check security group**: Ensure your IP is allowed for port 22
2. **Wait for boot**: Windows takes 10-15 minutes to fully boot and enable SSH
3. **Authentication**: Use Administrator username and password from vault
4. **Test connectivity**: `ssh Administrator@$IPV4_ADDRESS 'whoami'`

### RDP Connection Issues

1. **Check security group**: Ensure your IP is allowed for port 3389
2. **Wait for boot**: Windows takes 10-15 minutes to fully boot
3. **Check instance status**: Verify instance is running in AWS Console

### Ansible Connection Issues

1. **SSH/WinRM not ready**: Wait additional 5 minutes after SSH is available
2. **Password issues**: Verify `windows_admin_password` in vault
3. **Inventory issues**: Check `ansible-inventory -i inventories/aws/aws_ec2.yml --list`
4. **Connection method**: Ansible can use both SSH and WinRM for Windows management

### Performance Issues

1. **Instance size**: MVP uses t3.large for reliability
2. **RDP settings**: Configured for optimal performance
3. **Network**: Ensure good internet connection for RDP

## Security Notes

- **IP Restriction**: Both SSH (port 22) and RDP (port 3389) access limited to your current IP
- **Strong Password**: Use complex password in vault
- **Temporary Access**: Destroy instances when not needed
- **Dual Access**: Windows Server supports both SSH (command line) and RDP (desktop)
- **SSH Benefits**: SSH provides secure command-line access and works with Ansible
- **RDP Benefits**: RDP provides full desktop environment for GUI applications like Claude Desktop

## Next Steps After MVP

The MVP provides basic Claude Desktop access. Future optimizations will include:

1. **Cost Optimization**: Smaller instances and usage patterns
2. **Automated Installation**: Full Claude Desktop automation
3. **Advanced Security**: Enhanced security configurations
4. **Performance Tuning**: RDP and application optimization

## Files Created

This MVP implementation creates:

- `provision-aws-windows.yml` - Main provisioning playbook
- `configure-aws-windows.yml` - Configuration playbook
- `destroy-aws-windows.yml` - Cleanup playbook
- `provisioners/aws-windows.yml` - Windows Server provisioner
- `inventories/aws/group_vars/aws_windows/vars.yml` - Windows variables
- Updated `inventories/aws/aws_ec2.yml` - Multi-OS inventory
- Updated `playbooks/vars-secrets-template.yml` - Windows password template

## Support

For issues or improvements, refer to the project documentation or create an issue in the repository.
