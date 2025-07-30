# Technical Context: Ansible All My Things

## Core Technologies

### Ansible Ecosystem
- **Ansible Core**: Infrastructure automation and configuration management
- **Ansible Vault**: Encryption for sensitive data and credentials
- **Dynamic Inventory**: Multi-provider plugins for automatic host discovery
- **Collections**: Extended functionality for AWS, Hetzner Cloud, and Windows

### Multi-Provider Cloud Infrastructure ✅ PRODUCTION-READY
**Hetzner Cloud**: Primary provider for persistent development environments
  - **Linux**: Production implementation (Ubuntu 24.04 LTS) ✅ MOST MATURE
  - **Authentication**: HCLOUD_TOKEN environment variable ✅ WORKING
  - **Region**: Helsinki, Finland (hel1) - EU-based ✅ IMPLEMENTED

**AWS EC2**: Multi-platform provider for diverse workloads
  - **Linux**: Production implementation (Ubuntu 24.04 LTS) ✅ WORKING
  - **Windows**: Production implementation (Windows Server 2025) ✅ WORKING
  - **Authentication**: AWS credentials via environment variables ✅ WORKING
  - **Region**: eu-north-1 (carbon footprint and latency optimization) ✅ IMPLEMENTED

### Target Applications & Use Cases
**Cross-Provider Development**: Automated development environments across providers ✅ ACHIEVED
**Windows Application Access**: Claude Desktop Application (Windows-only) ✅ ACHIEVED
**Cost-Optimized Infrastructure**: Provider choice based on usage patterns ✅ IMPLEMENTED
**Testing Infrastructure**: Comprehensive testing framework with Vagrant providers ✅ ACHIEVED
**Development Workflow Maturity**: Transition from "Genesis" to "Custom Built" stage ✅ COMPLETED

## Development Setup

### Required Tools
**Automated Installation:**
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Ansible collections
ansible-galaxy collection install -r requirements.yml
```

**Manual Requirements (if needed):**
```bash
# Core requirements
ansible >= 4.0
python >= 3.8

# Multi-provider support (installed via requirements.txt)
boto3 >= 1.26.0            # AWS support
botocore >= 1.29.0         # AWS support
hcloud >= 1.16.0           # Hetzner Cloud CLI (optional)

# Provider CLIs (for credential management)
aws CLI                    # AWS credential management
```

### Multi-Provider Environment Configuration
```bash
# Production Environment Credentials
# AWS credentials (for rivendell and moria)
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export AWS_DEFAULT_REGION="eu-north-1"

# Hetzner Cloud credentials (for hobbiton)
export HCLOUD_TOKEN="your-hcloud-token"

# Ansible configuration (unified across production and testing)
export ANSIBLE_VAULT_PASSWORD_FILE="./ansible-vault-password.txt"
export ANSIBLE_HOST_KEY_CHECKING=False

# Testing Environment Setup
# Vagrant-based testing requires fresh SSH keys (see test/README.md)
# No additional credentials needed for Docker/Tart providers
```

### Ansible Collections ✅ IMPLEMENTED & TESTED
```bash
# Multi-provider collections (production and testing)
ansible.windows           # ✅ INSTALLED - Windows platform support
community.windows         # ✅ AVAILABLE - Extended Windows functionality
amazon.aws                # ✅ INSTALLED - AWS provider support
hetzner.hcloud            # ✅ INSTALLED - Hetzner Cloud provider support

# Testing framework collections
# Same collections used for production and testing environments
# Installed via: ansible-galaxy collection install -r requirements.yml
```

### Cross-Provider Project Structure (Implemented & Tested)
```
ansible-all-my-things/
├── Multi-Provider Provisioning:
│   ├── provision.yml             # Hetzner Cloud Linux ✅ WORKING
│   ├── provision-aws-linux.yml   # AWS Linux provisioning ✅ WORKING
│   └── provision-aws-windows.yml # AWS Windows provisioning ✅ WORKING
├── Configuration:
│   ├── configure.yml             # Hetzner Cloud configuration ✅ WORKING
│   ├── configure-linux.yml       # Linux configuration (used by tests) ✅ WORKING
│   └── configure-aws-windows.yml # AWS Windows configuration ✅ WORKING
├── Cleanup:
│   ├── destroy.yml               # Hetzner Cloud cleanup ✅ WORKING
│   └── destroy-aws.yml           # AWS unified cleanup ✅ WORKING
├── Unified Inventory:
│   ├── inventories/aws_ec2.yml   # AWS inventory (rivendell, moria) ✅ WORKING
│   ├── inventories/hcloud.yml    # Hetzner inventory (hobbiton) ✅ WORKING
│   ├── inventories/vagrant_docker.yml # Docker testing inventory (dagorlad) ✅ NEW
│   ├── inventories/vagrant_tart.yml   # Tart testing inventory (lorien) ✅ NEW
│   └── inventories/group_vars/   # Provider-aware variables including test providers ✅ ENHANCED
├── Provider Provisioners:
│   ├── provisioners/hcloud.yml   # Hetzner provisioning ✅ WORKING
│   ├── provisioners/aws-linux.yml  # AWS Linux provisioning ✅ WORKING
│   └── provisioners/aws-windows.yml # AWS Windows provisioning ✅ WORKING
├── Testing Infrastructure:
│   ├── test/docker/              # Vagrant Docker testing environment ✅ NEW
│   ├── test/tart/                # Vagrant Tart testing environment ✅ NEW
│   ├── test/README.md            # Testing framework documentation ✅ NEW
│   └── test/test_*.md            # Manual testing procedures ✅ NEW
├── Dependencies:
│   ├── requirements.txt          # Python dependencies ✅ COMPLETED
│   └── requirements.yml          # Ansible collections ✅ COMPLETED
├── Documentation:
│   ├── docs/aws/ & docs/hcloud/  # Provider-specific guides ✅ UPDATED
│   ├── docs/create-vm.md         # Unified entry point ✅ UPDATED
│   └── docs/problem-undefined-vars-in-test-providers/ # Problem documentation ✅ NEW
└── memory-bank/                  # Cross-provider documentation ✅ CURRENT
```

## Technical Constraints & Requirements

### Cross-Provider Infrastructure Requirements ✅ IMPLEMENTED & TESTED

#### Testing Environment Requirements
- **Vagrant Docker**: Ubuntu Linux container for testing Linux configurations ✅ IMPLEMENTED
- **Vagrant Tart**: macOS-compatible VM testing environment ✅ IMPLEMENTED
- **SSH Key Management**: Fresh SSH keys required for testing security (documented) ✅ IMPLEMENTED
- **Variable Loading**: Unified inventory integration with main project group_vars ✅ IMPLEMENTED

#### Hetzner Cloud Linux Requirements
- **Instance Type**: cx22 (2 vCPU, 4GB RAM, 40GB SSD) for development workloads ✅ IMPLEMENTED
- **Location**: Helsinki, Finland (hel1) for EU-based operations ✅ IMPLEMENTED
- **Network**: SSH (22) access with public IPv4 ✅ IMPLEMENTED
- **OS**: Ubuntu 24.04 LTS with full desktop environment ✅ IMPLEMENTED

#### AWS Multi-Platform Requirements
**Linux Specifications**:
- **Instance Type**: t3.micro/small for minimal server workloads ✅ IMPLEMENTED
- **Storage**: 20GB GP3 EBS for basic development ✅ IMPLEMENTED
- **OS**: Ubuntu 24.04 LTS with minimal configuration ✅ IMPLEMENTED

**Windows Specifications**:
- **Instance Type**: t3.large (4 vCPU, 8GB RAM) for optimal GUI performance ✅ IMPLEMENTED
- **Storage**: 50GB GP3 EBS optimized for Windows Server ✅ IMPLEMENTED
- **Network**: SSH (22) and RDP (3389) with IP restrictions ✅ IMPLEMENTED
- **AMI**: Windows Server 2025 with Desktop Experience ✅ IMPLEMENTED

### Multi-Provider Ansible Support (Implemented & Tested)
```yaml
# Cross-provider collections ✅ WORKING
collections:
  - name: hetzner.hcloud       # ✅ INSTALLED - Hetzner Cloud support
  - name: amazon.aws           # ✅ INSTALLED - AWS support
  - name: ansible.windows      # ✅ INSTALLED - Windows platform support
  - name: community.windows    # ✅ AVAILABLE - Extended Windows functionality

# Provider-specific connection configurations ✅ IMPLEMENTED & TESTED
# Production Environments:
# Hetzner Cloud: SSH to root, then gandalf user
# AWS Linux: SSH to ubuntu, then gandalf user  
# AWS Windows: SSH to Administrator with PowerShell shell

# Testing Environments:
# Vagrant Docker: SSH to vagrant user (admin_user_on_fresh_system: vagrant)
# Vagrant Tart: SSH to admin user (admin_user_on_fresh_system: admin)
```

### Cost Analysis Across Providers (Achieved)
**Hetzner Cloud**: ~$4/month with predictable EU pricing ✅ COST LEADER
**AWS Linux**: ~$8-10/month with on-demand usage ✅ IMPLEMENTED
**AWS Windows**: ~$60/month base with on-demand reducing actual costs ✅ IMPLEMENTED
**Usage Patterns**: Provider choice optimized for specific use cases ✅ ACHIEVED
**Testing Environments**: Local/free testing with Vagrant Docker and Tart providers ✅ COST-FREE
**AWS Testing Guidelines**: t3.micro recommended for cost-effective testing ✅ DOCUMENTED

## Tool Usage Patterns

### Testing Infrastructure Patterns (Implemented)
```yaml
# Testing environment variable management ✅ WORKING
# inventories/group_vars/vagrant_docker/vars.yml
admin_user_on_fresh_system: "vagrant"

# inventories/group_vars/vagrant_tart/vars.yml  
admin_user_on_fresh_system: "admin"

# Unified inventory integration ✅ IMPLEMENTED
# Test environments use main project inventory structure: ../../inventories
# Vagrant configurations updated to use ansible.inventory_path = "../../inventories"
```

### Windows Server Configuration (Implemented)
```yaml
# Windows inventory configuration ✅ WORKING
# inventories/aws_ec2/group_vars/windows/vars.yml
admin_user_on_fresh_system: "Administrator"
ansible_shell_type: powershell
ansible_shell_executable: powershell

# SSH connection working with PowerShell integration
# SSH key authentication via icacls permissions
# Administrator account with RDP access enabled
```

### Windows Package Management (Implemented)
```yaml
# Chocolatey installation pattern ✅ WORKING
- name: Install Chocolatey package manager
  win_shell: |
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  args:
    creates: C:\ProgramData\chocolatey\bin\choco.exe

# Ready for Claude Desktop and other applications
# Framework established for automated software installation
```

### Windows Access Configuration (Implemented)
```yaml
# Security group for SSH and RDP access ✅ WORKING
- name: Create security group
  amazon.aws.ec2_group:
    name: "{{ aws_security_group_name }}"
    description: "Security group for Ansible development environment"
    rules:
      - proto: tcp
        ports:
          - 22    # SSH
        cidr_ip: "{{ current_public_ip }}/32"
        rule_desc: "SSH access from current IP"
      - proto: tcp
        ports:
          - 3389  # RDP
        cidr_ip: "{{ current_public_ip }}/32"
        rule_desc: "RDP access from current IP"

# Shared security group "ansible-sg" for both Linux and Windows
# Dynamic IP detection via ipinfo.io API
```

## Dependencies & Integration

### Testing Infrastructure Integration (Implemented)
- **Vagrant Integration**: Docker and Tart providers with unified variable management ✅ WORKING
- **Problem Resolution**: Fixed undefined group_vars by integrating test environments with main inventory ✅ COMPLETED
- **Variable Loading**: Test environments use main project group_vars structure ✅ IMPLEMENTED
- **Provider Abstraction**: Same inventory patterns across production and testing ✅ ACHIEVED
- **Documentation**: Comprehensive testing procedures and troubleshooting guides ✅ COMPLETED

### AWS Infrastructure (Successfully Extended from Linux)
- **Dynamic Inventory**: `amazon.aws.aws_ec2` plugin ✅ WORKING FOR BOTH PLATFORMS
- **Instance Management**: `amazon.aws.ec2_instance` module ✅ WORKING FOR WINDOWS
- **Security Groups**: Automated firewall rule management ✅ EXTENDED FOR RDP
- **Resource Tagging**: Consistent naming and cleanup patterns ✅ UNIFIED APPROACH

### Windows-Specific Dependencies (Implemented)
```yaml
# Windows Server configuration achieved ✅ WORKING
configure-aws-windows.yml:
  - Chocolatey package manager installation
  - RDP performance optimization (32-bit color, clipboard)
  - PowerShell execution environment

# Ready for extension with additional applications
```

### Application Framework (Ready)
- **Chocolatey Framework**: Ready for Claude Desktop and other Windows applications
- **RDP Access**: Optimized desktop environment for applications
- **SSH Access**: Command-line access with PowerShell integration

## Performance Achievements

### Windows Server Performance (Achieved)
- **Provisioning Time**: ~5 minutes (significantly better than target) ✅ ACHIEVED
- **Instance Performance**: t3.large provides optimal GUI responsiveness ✅ IMPLEMENTED
- **RDP Performance**: Optimized with 32-bit color and clipboard sharing ✅ IMPLEMENTED
- **Storage Performance**: 50GB GP3 provides effective disk I/O ✅ IMPLEMENTED

### Cost Optimization (Achieved)
```yaml
# Actual usage pattern ✅ WORKING
Provision: ~5 minutes
Usage: On-demand sessions (2-3 hours typical)
Destroy: ~2 minutes
Cost: $60/month base, significantly reduced with on-demand usage
Future: t3.medium downgrade available for $15/month target
```

## Security Architecture

### Implemented Windows Security Model
- **SSH Access**: Restricted to user's IP address only (port 22) ✅ IMPLEMENTED
- **RDP Access**: Restricted to user's IP address only (port 3389) ✅ IMPLEMENTED
- **Windows Firewall**: Configured for minimal exposure via PowerShell ✅ IMPLEMENTED
- **User Accounts**: Administrator with SSH key authentication ✅ IMPLEMENTED
- **Credential Management**: SSH keys and Windows passwords via Ansible Vault ✅ WORKING

### Network Security (Implemented)
- **Security Groups**: AWS-managed firewall rules ✅ WORKING
- **Port Access**: SSH (22) and RDP (3389) only ✅ IMPLEMENTED
- **IP Restrictions**: User's current public IP only ✅ IMPLEMENTED
- **Encryption**: SSH with OpenSSH and RDP with TLS encryption ✅ WORKING

## Testing Infrastructure Implementation Success

### Problem Resolution ✅ COMPLETED
- **Root Cause**: Vagrant inventory bypassed main project group_vars structure
- **Solution**: Updated Vagrant configurations to use main inventory directory (../../inventories)
- **Variable Loading**: Fixed undefined `my_ansible_user` variable in test environments
- **Testing Validation**: Manual testing procedures verify fix effectiveness

### Testing Framework ✅ COMPLETED
- **Vagrant Docker**: Ubuntu Linux testing environment with proper SSH key management
- **Vagrant Tart**: macOS-compatible testing environment with unified variable loading
- **Provider Integration**: Test environments follow same patterns as production
- **Documentation**: Comprehensive testing procedures and troubleshooting guides

### Technical Implementation ✅ COMPLETED
- **Inventory Integration**: Created vagrant_docker.yml and vagrant_tart.yml inventory files
- **Variable Management**: Added vagrant_docker and vagrant_tart specific group_vars
- **Configuration Updates**: Updated Vagrantfiles and ansible.cfg for unified inventory approach
- **Security Guidelines**: SSH key refresh procedures for safe testing environments

### Project Maturity ✅ COMPLETED
- **Stage Transition**: Successfully moved from "Genesis" to "Custom Built" stage
- **Testing Foundation**: Established comprehensive testing framework for reliable development
- **Documentation Excellence**: Step-by-step testing procedures and troubleshooting guides
- **Future Ready**: Foundation established for automated testing and CI/CD integration
