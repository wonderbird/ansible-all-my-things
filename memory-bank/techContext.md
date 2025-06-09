# Technical Context: Ansible All My Things

## Core Technologies

### Ansible Ecosystem
- **Ansible Core**: Infrastructure automation and configuration management
- **Ansible Vault**: Encryption for sensitive data and credentials
- **Dynamic Inventory**: Provider-specific inventory plugins
- **Collections**: Extended functionality for cloud providers

### Cloud Providers & APIs
- **Hetzner Cloud**: Primary production environment provider
  - API: Hetzner Cloud API via `hetzner.hcloud` collection
  - Authentication: `HCLOUD_TOKEN` environment variable
- **AWS EC2**: Secure development environment (MVP in progress)
  - API: AWS EC2 API via `amazon.aws` collection
  - Authentication: AWS credentials via environment variables
- **Local Testing**: Vagrant with multiple providers

### Operating Systems
- **Primary Target**: Ubuntu 24.04 LTS
- **Testing Environments**: 
  - Docker containers (minimal Ubuntu)
  - Tart VMs (macOS virtualization)
  - VirtualBox VMs (cross-platform)

## Development Setup

### Required Tools
```bash
# Core requirements
ansible >= 2.9
python >= 3.8
vagrant >= 2.0 (for testing)

# Cloud provider tools
hcloud CLI (for Hetzner)
aws CLI (for AWS)

# Testing tools
docker (for container testing)
virtualbox (for VM testing)
```

### Environment Configuration
```bash
# Required environment variables
export HCLOUD_TOKEN="your-hetzner-token"
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"

# Ansible configuration
export ANSIBLE_VAULT_PASSWORD_FILE="./ansible-vault-password.txt"
export ANSIBLE_HOST_KEY_CHECKING=False
```

### Project Structure
```
ansible-all-my-things/
├── ansible.cfg                 # Ansible configuration
├── provision.yml              # Main provisioning entry point
├── configure.yml              # Main configuration entry point
├── backup.yml                 # Backup operations
├── restore.yml                # Restore operations
├── destroy.yml                # Resource cleanup
├── inventories/               # Provider-specific inventories
│   ├── hcloud/               # Hetzner Cloud
│   ├── aws/                  # AWS EC2 (planned)
│   └── local/                # Local testing
├── playbooks/                # Functional playbooks
├── provisioners/             # Provider-specific provisioning
├── configuration/            # Backup storage
├── test/                     # Testing environments
└── memory-bank/              # Project documentation
```

## Technical Constraints

### Ansible Version Compatibility
- **Minimum**: Ansible 2.9 (for collection support)
- **Recommended**: Ansible 4.0+ (for latest cloud provider features)
- **Collections Required**:
  - `community.general`
  - `hetzner.hcloud`
  - `amazon.aws` (planned)

### Python Dependencies
```yaml
# requirements.yml (Ansible collections)
collections:
  - name: community.general
  - name: hetzner.hcloud
  - name: amazon.aws

# requirements.txt (Python packages)
ansible>=4.0
hcloud>=1.0
boto3>=1.0 (for AWS)
```

### Provider-Specific Limitations

#### Hetzner Cloud
- **Regions**: Limited to available Hetzner regions
- **Instance Types**: cx11, cx21, cx31, etc.
- **Images**: Ubuntu 20.04/22.04/24.04 LTS
- **Networking**: Default VPC with SSH access

#### AWS EC2
- **Instance Types**: t3.micro, t3.small (cost-optimized)
- **Regions**: Configurable, default to us-east-1
- **Images**: Ubuntu 24.04 LTS AMI
- **Storage**: GP3 EBS volumes (cost-effective)

#### Local Testing
- **Docker**: No desktop environment support
- **Vagrant**: Full desktop support with VirtualBox/Tart
- **Limitations**: Provider-specific admin users

## Tool Usage Patterns

### Ansible Configuration
```ini
# ansible.cfg
[defaults]
host_key_checking = False
inventory = inventories/
vault_password_file = ansible-vault-password.txt
roles_path = roles/
collections_paths = collections/

[inventory]
enable_plugins = hetzner.hcloud.hcloud, amazon.aws.aws_ec2

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
```

### Dynamic Inventory Configuration
```yaml
# inventories/hcloud/hcloud.yml
plugin: hetzner.hcloud.hcloud
regions:
  - eu-central
types:
  - cx11
  - cx21
keyed_groups:
  - key: hcloud_type
    prefix: type
  - key: hcloud_datacenter
    prefix: datacenter
```

### Vault Management
```bash
# Create encrypted secrets file
ansible-vault create playbooks/vars-secrets.yml

# Edit encrypted secrets
ansible-vault edit playbooks/vars-secrets.yml

# View encrypted content
ansible-vault view playbooks/vars-secrets.yml
```

## Dependencies & Integration

### External Services
- **Hetzner Cloud API**: Infrastructure provisioning
- **AWS EC2 API**: Alternative infrastructure provisioning
- **Package Repositories**: Ubuntu APT, Homebrew
- **Application Sources**: VS Code, Chromium, Node.js

### Internal Dependencies
```yaml
# Playbook execution order (configure.yml)
1. setup-users.yml          # User management
2. setup-basics.yml         # System packages
3. setup-homebrew.yml       # Package manager
4. setup-nodejs-typescript.yml # Development tools
5. setup-desktop.yml        # GUI environment
6. setup-keyring.yml        # Credential storage
7. setup-desktop-apps.yml   # Applications
8. restore.yml              # Configuration restore
9. reboot-if-required.yml   # System restart
```

### Testing Dependencies
```yaml
# Vagrant providers
- virtualbox: Cross-platform VM testing
- docker: Lightweight container testing
- tart: macOS-specific VM testing (Apple Silicon)

# Test environments
- test/docker/: Minimal Ubuntu container
- test/tart/: Full Ubuntu desktop VM
- test/vagrant/: Standard VirtualBox VM
```

## Performance Considerations

### Provisioning Time Targets
- **Infrastructure**: 2-5 minutes (cloud provider dependent)
- **Configuration**: 10-15 minutes (full desktop setup)
- **Backup/Restore**: 1-3 minutes (configuration files only)

### Resource Requirements
```yaml
# Minimum instance specifications
CPU: 1 vCPU
RAM: 1GB (2GB recommended for desktop)
Storage: 20GB (adequate for development)
Network: Standard cloud networking
```

### Optimization Strategies
- **Parallel Execution**: Ansible parallelism where possible
- **Package Caching**: APT cache updates only when needed
- **Conditional Tasks**: Skip unnecessary operations
- **Efficient Transfers**: Rsync for large file operations

## Security Architecture

### Credential Management
- **Ansible Vault**: All secrets encrypted at rest
- **Environment Variables**: Provider API credentials
- **SSH Keys**: Automated key pair management
- **No Hardcoded Secrets**: All sensitive data externalized

### Network Security
- **SSH Only**: No password authentication
- **Minimal Exposure**: Only required ports open
- **Provider Security**: Leverage cloud provider security groups
- **Key Rotation**: Support for SSH key updates

### System Security
- **Sudo Access**: Limited to ansible user
- **Package Updates**: Automatic security updates
- **Firewall**: Basic UFW configuration
- **User Isolation**: Separate admin, ansible, and desktop users
