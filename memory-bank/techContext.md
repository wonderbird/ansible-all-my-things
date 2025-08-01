# Technical Context: Ansible All My Things

## Core Technologies

### Ansible Ecosystem
- **Ansible Core**: Infrastructure automation and configuration management
- **Ansible Vault**: Encryption for sensitive data and credentials
- **Dynamic Inventory**: Multi-provider plugins for automatic host discovery
- **Collections**: Extended functionality for AWS, Hetzner Cloud, and Windows

### Multi-Provider Cloud Infrastructure
**Hetzner Cloud**: Primary provider for persistent development environments
  - **Linux**: Production implementation (Ubuntu 24.04 LTS)
  - **Authentication**: HCLOUD_TOKEN environment variable
  - **Region**: Helsinki, Finland (hel1) - EU-based

**AWS EC2**: Multi-platform provider for diverse workloads
  - **Linux**: Production implementation (Ubuntu 24.04 LTS)
  - **Windows**: Production implementation (Windows Server 2025)
  - **Authentication**: AWS credentials via environment variables
  - **Region**: eu-north-1

**Vagrant**: Local testing environments
  - **Docker Provider**: Ubuntu Linux testing environment
  - **Tart Provider**: macOS-compatible testing environment
  - **Authentication**: Local SSH keys

### Target Applications & Use Cases
**Cross-Provider Development**: Automated development environments across providers
**Platform-Specific Applications**: Access to Windows/Linux-only applications from any host
**Cost-Optimized Infrastructure**: Provider choice based on usage patterns (Hetzner ~$4/month, Vagrant free)
**Testing Infrastructure**: Comprehensive testing framework with Vagrant providers
**Current Focus**: Unified command patterns for consistent development workflow

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

### Environment Configuration
```bash
# Hetzner Cloud credentials (for hobbiton)
export HCLOUD_TOKEN="your-hcloud-token"

# AWS credentials (for rivendell and moria)
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export AWS_DEFAULT_REGION="eu-north-1"

# Ansible configuration (automated vault password handling)
export ANSIBLE_HOST_KEY_CHECKING=False
# Note: ansible.cfg includes vault_password_file = ansible-vault-password.txt

# Vagrant Testing - no additional credentials needed
# Uses unified inventory structure and same vault configuration
```

### Ansible Collections
```bash
# Core collections for current focus
hetzner.hcloud            # Hetzner Cloud provider support
community.general         # General utilities and modules
ansible.posix             # POSIX system utilities

# AWS collections (when needed)
amazon.aws                # AWS provider support

# Windows collections (when needed)
ansible.windows           # Windows platform support
community.windows         # Extended Windows functionality

# Installed via: ansible-galaxy collection install -r requirements.yml
```

### Project Structure (Current Focus)
```
ansible-all-my-things/
├── Core Provisioning:
│   └── provision.yml             # Unified provisioning (Hetzner working, Vagrant Docker target)
├── Configuration:
│   ├── configure.yml             # Hetzner Cloud configuration
│   └── configure-linux.yml       # Linux configuration (used by tests)
├── Unified Inventory:
│   ├── inventories/hcloud.yml    # Hetzner inventory (hobbiton)
│   ├── inventories/vagrant_docker.yml # Docker testing inventory (dagorlad)
│   └── inventories/group_vars/   # Provider-aware variables with vault secrets
├── Provider Provisioners:
│   ├── provisioners/hcloud.yml   # Hetzner provisioning (working)
│   └── provisioners/vagrant_docker-linux.yml # Vagrant Docker target (MVP)
├── Testing Infrastructure:
│   ├── test/docker/              # Vagrant Docker testing environment
│   └── test/README.md            # Testing framework documentation
├── Dependencies:
│   ├── requirements.txt          # Python dependencies
│   └── requirements.yml          # Ansible collections
└── memory-bank/                  # Project documentation
```

## Technical Requirements (Current Focus)

### Hetzner Cloud Linux (Production Reference)
- **Instance**: cx22 (2 vCPU, 4GB RAM, 40GB SSD) in Helsinki
- **OS**: Ubuntu 24.04 LTS with full GNOME desktop environment
- **Network**: SSH (22) access with public IPv4
- **Cost**: ~$4/month with predictable EU pricing

### Vagrant Docker (MVP Target)
- **Environment**: Ubuntu Linux container for testing Linux configurations
- **Provider**: Docker backend for fast provisioning
- **SSH Access**: SSH to vagrant user (admin_user_on_fresh_system: vagrant)
- **Variable Loading**: Unified inventory integration with main project group_vars
- **Current Gap**: Requires separate `vagrant up` + configuration commands

### Key Technical Patterns
```yaml
# Connection configurations for current focus
# Hetzner Cloud: SSH to root, then gandalf user
# Vagrant Docker: SSH to vagrant user (admin_user_on_fresh_system: vagrant)

# Unified inventory integration
# Test environments use main project inventory structure: ../../inventories
# Vagrant configurations use ansible.inventory_path = "../../inventories"
```

### Cost Analysis (Focus Areas)
**Hetzner Cloud**: ~$4/month - cost leader for persistent environments
**Vagrant Docker**: Free - ideal for local testing and development
**Target**: Unified command patterns across both cost-effective and free environments

## Tool Usage Patterns (Current Focus)

### Testing Infrastructure Patterns
```yaml
# Current variable management for MVP
# inventories/group_vars/vagrant_docker/vars.yml
admin_user_on_fresh_system: "vagrant"

# Unified inventory integration (key for MVP)
# Test environments use main project inventory structure: ../../inventories
# Vagrant configurations use ansible.inventory_path = "../../inventories"
```

### Target Vagrant Docker Integration
```yaml
# Target provisioner pattern (MVP deliverable)
# provisioners/vagrant_docker-linux.yml
- name: Start Vagrant Docker environment
  shell: vagrant up
  args:
    chdir: "{{ vagrant_docker_path }}"
    creates: "{{ vagrant_docker_status_file }}"

- name: Refresh inventory to include Vagrant instance
  meta: refresh_inventory
```

### Hetzner Cloud Integration (Reference Pattern)
```yaml
# Hetzner Cloud provisioning pattern
- name: Create Hetzner Cloud server
  hetzner.hcloud.hcloud_server:
    name: "{{ hcloud_server_name }}"
    image: "{{ hcloud_image }}"
    server_type: "{{ hcloud_server_type }}"
    location: "{{ hcloud_location }}"
    ssh_keys:
      - "{{ hcloud_ssh_key_name }}"
    state: present
```

## Dependencies & Integration (Current Focus)

### Testing Infrastructure Integration
- **Vagrant Integration**: Docker provider with unified variable management
- **Variable Loading**: Test environments use main project group_vars structure
- **Provider Abstraction**: Same inventory patterns across production and testing
- **Current Target**: Extend unified command patterns to Vagrant environments

### Key Dependencies for MVP
```yaml
# Required for Vagrant Docker integration
requirements.txt:
  - ansible>=4.0
  - hcloud>=1.16.0  # Hetzner Cloud support

requirements.yml:
  - name: hetzner.hcloud
  - name: community.general
  - name: ansible.posix
```

## Performance & Security (Current Focus)

### Hetzner Cloud Performance
- **Provisioning Time**: ~10-15 minutes for complete desktop environment
- **Instance Performance**: cx22 provides good development environment responsiveness
- **Cost Optimization**: ~$4/month - most cost-effective for persistent environments

### Vagrant Docker Performance
- **Provisioning Time**: ~2-3 minutes for container startup
- **Instance Performance**: Fast container-based testing environment
- **Cost**: Free - ideal for local development and testing

### Security Model (Current Focus)
- **SSH Key Management**: Single SSH key pair across environments
- **Credential Management**: Vault-encrypted secrets with automated access
- **Environment Isolation**: Clean separation between production and testing environments
- **Testing Security**: SSH key refresh procedures for safe testing

## Current MVP Implementation Status

### Vagrant Docker Integration Target
- **Goal**: Unified command pattern matching Hetzner Cloud approach
- **Current State**: Separate `vagrant up` + configuration commands
- **Target State**: `provision.yml --extra-vars "provider=vagrant_docker platform=linux"`
- **Foundation**: Established inventory integration and variable management patterns
