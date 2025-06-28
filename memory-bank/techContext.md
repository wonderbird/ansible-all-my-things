# Technical Context: Ansible All My Things

## Core Technologies

### Ansible Ecosystem
- **Ansible Core**: Infrastructure automation and configuration management
- **Ansible Vault**: Encryption for sensitive data and credentials
- **Dynamic Inventory**: AWS EC2 plugin for automatic host discovery
- **Collections**: Extended functionality for AWS and Windows

### Cloud Provider & Platform
- **AWS EC2**: Primary cloud provider for both Linux and Windows
  - **Linux**: Working implementation (Ubuntu 24.04 LTS)
  - **Windows**: Target implementation (Windows Server 2025)
  - **Authentication**: AWS credentials via environment variables
  - **Regions**: eu-north-1 (carbon footprint and latency optimization)

### Target Applications
- **Primary**: Claude Desktop Application (Windows-only)
- **Foundation**: Proven Linux development environment automation

## Development Setup

### Required Tools
```bash
# Core requirements
ansible >= 4.0
python >= 3.8
boto3 >= 1.0
botocore >= 1.0

# AWS tools
aws CLI (for credential management)

# Windows-specific (planned)
ansible.windows collection
community.windows collection
```

### Environment Configuration
```bash
# Required environment variables
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export AWS_DEFAULT_REGION="eu-north-1"

# Ansible configuration
export ANSIBLE_VAULT_PASSWORD_FILE="./ansible-vault-password.txt"
export ANSIBLE_HOST_KEY_CHECKING=False
```

### Project Structure (Windows Extension)
```
ansible-all-my-things/
├── provision-aws-windows.yml     # Windows Server provisioning
├── configure-aws-windows.yml     # Windows Server configuration
├── destroy-aws-windows.yml       # Windows Server cleanup
├── inventories/aws/              # Shared AWS inventory
├── provisioners/
│   ├── aws-ec2.yml              # Linux provisioning (working)
│   └── aws-windows.yml          # Windows provisioning (planned)
├── playbooks/
│   ├── setup-*.yml              # Linux playbooks (working)
│   └── setup-windows-*.yml      # Windows playbooks (planned)
└── memory-bank/                  # Streamlined documentation
```

## Technical Constraints

### Windows Server Requirements
- **Minimum Instance**: t3.medium (2 vCPU, 4GB RAM for GUI)
- **Storage**: 50GB GP3 EBS (Windows Server space requirements)
- **Network**: SSH (22) and RDP (3389) access with IP restrictions
- **AMI**: Windows Server 2025 with Desktop Experience

### Ansible Windows Support
```yaml
# requirements.yml (Windows collections)
collections:
  - name: ansible.windows
  - name: community.windows
  - name: amazon.aws

# Windows connection requirements (SSH preferred)
ansible_connection: ssh
ansible_user: Administrator
ansible_port: 22

# Alternative WinRM connection
# ansible_connection: winrm
# ansible_winrm_transport: basic
# ansible_port: 5985
```

### Cost Constraints
- **MVP Budget**: ~$60/month acceptable initially (t3.large for reliability)
- **Target Budget**: ~$15/month for typical usage (after optimization)
- **Usage Pattern**: 10-15 hours/week (not continuous)
- **Instance Costs**: t3.large ~$0.0832/hour (MVP), t3.medium ~$0.0416/hour (optimized)
- **Storage Costs**: 50GB GP3 ~$4/month

## Tool Usage Patterns

### Windows Server Configuration
```yaml
# Windows inventory configuration (current)
# inventories/aws/group_vars/aws_windows/vars.yml
admin_user_on_fresh_system: Administrator
ansible_user: Administrator
desktop_user: claude-user
ansible_connection: ssh
ansible_port: 22

# Alternative WinRM configuration
# ansible_connection: winrm
# ansible_winrm_transport: basic
# ansible_port: 5985
```

### Windows Package Management
```yaml
# Chocolatey installation pattern
- name: Install Chocolatey
  win_chocolatey:
    name: chocolatey
    state: present

- name: Install Claude Desktop
  win_chocolatey:
    name: claude-desktop
    state: present
```

### Windows Access Configuration
```yaml
# Security group for SSH and RDP access
- name: Create Windows security group
  amazon.aws.ec2_group:
    name: "{{ security_group_windows }}"
    description: "SSH and RDP access for Windows Server"
    rules:
      - proto: tcp
        ports:
          - 22
        cidr_ip: "{{ user_ip }}/32"
        rule_desc: "SSH from user IP"
      - proto: tcp
        ports:
          - 3389
        cidr_ip: "{{ user_ip }}/32"
        rule_desc: "RDP from user IP"
```

## Dependencies & Integration

### AWS Infrastructure (Reused from Linux)
- **Dynamic Inventory**: `amazon.aws.aws_ec2` plugin
- **Instance Management**: `amazon.aws.ec2_instance` module
- **Security Groups**: Automated firewall rule management
- **Resource Tagging**: Consistent naming and cleanup patterns

### Windows-Specific Dependencies
```yaml
# Windows Server configuration dependencies
1. setup-windows-users.yml      # Windows user management
2. setup-windows-ssh.yml        # OpenSSH Server configuration
3. setup-windows-desktop.yml    # Desktop experience configuration
4. setup-claude-desktop.yml     # Claude Desktop installation
5. setup-windows-rdp.yml        # RDP optimization
```

### Application Dependencies
- **Claude Desktop**: Primary target application
- **Supporting Software**: .NET runtime, Visual C++ redistributables
- **RDP Client**: For accessing Windows desktop environment

## Performance Considerations

### Windows Server Performance
- **Provisioning Time**: 15-20 minutes (Windows startup + configuration)
- **Instance Requirements**: t3.medium minimum for responsive GUI
- **RDP Performance**: Optimized for desktop application usage
- **Storage Performance**: GP3 for cost-effective disk I/O

### Cost Optimization
```yaml
# Target usage pattern
Provision: 5 minutes
Usage: 2-3 hours per session
Destroy: 2 minutes
Sessions: 3-5 per week
Monthly cost: ~$15 (vs $34 continuous)
```

## Security Architecture

### Windows Security Model
- **SSH Access**: Restricted to user's IP address only (port 22)
- **RDP Access**: Restricted to user's IP address only (port 3389)
- **Windows Firewall**: Configured for minimal exposure
- **User Accounts**: 
  - Administrator (initial setup and automation)
  - claude-user (desktop application usage)
- **Credential Management**: Windows passwords via Ansible Vault

### Network Security
- **Security Groups**: AWS-managed firewall rules
- **Port Access**: SSH (22), RDP (3389), and WinRM (5985) as needed
- **IP Restrictions**: User's IP address only
- **Encryption**: SSH with OpenSSH and RDP with TLS encryption

## Windows Server Implementation Plan

### Phase 1: Infrastructure (Current Priority)
- Research Windows Server 2025 AMI options
- Determine optimal instance type and storage configuration
- Plan RDP security group and access patterns
- Calculate actual costs vs. budget targets

### Phase 2: Provisioning
- Create `provisioners/aws-windows.yml`
- Implement Windows Server instance creation
- Configure WinRM for Ansible connectivity
- Test basic Windows Server provisioning

### Phase 3: Configuration
- Develop Windows-specific playbooks
- Implement Claude Desktop installation automation
- Configure RDP for optimal performance
- Test complete provision → configure → access workflow

### Phase 4: Integration
- Integrate with existing AWS infrastructure patterns
- Document Windows Server usage procedures
- Validate cost and performance targets
- Complete end-to-end testing
