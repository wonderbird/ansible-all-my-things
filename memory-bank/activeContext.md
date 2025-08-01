# Active Context: Ansible All My Things

## Current Work Focus

### Unified Vagrant Docker Provisioning 🎯 CURRENT MVP
**Goal**: Enable unified provisioning command for Vagrant Docker environment (dagorlad) that matches AWS Linux pattern.

**Status**: 🎯 IN PROGRESS - Next development increment with 2-3 day timeline

**Business Context**: Urgent need for consistent provisioning commands across cloud VMs and Vagrant VMs - reducing cognitive load and maintenance complexity.

**Foundation**: Built on existing provider/platform parameter system and mature testing infrastructure.

**Target Command Pattern**: 
```bash
ansible-playbook provision.yml --extra-vars "provider=vagrant_docker platform=linux" --vault-password-file ansible-vault-password.txt
```

**Current State Gap**: 
- **AWS Linux (rivendell)**: Uses unified `provision.yml` with `provider=aws platform=linux`
- **Vagrant Docker (dagorlad)**: Uses separate `vagrant up` + `ansible-playbook configure-linux.yml`
- **Problem**: Inconsistent command patterns create maintenance complexity

**MVP Deliverables**:
1. **Vagrant Provisioner Module** (`provisioners/vagrant_docker-linux.yml`) - Handle `vagrant up` execution via Ansible
2. **Provider Extension** (Update `provision.yml`) - Support `provider=vagrant_docker platform=linux` parameters
3. **Documentation Updates** (`docs/create-vm.md`, `test/docker/README.md`) - Include vagrant_docker as provider option
4. **Test Suite** - Test-first approach with comprehensive validation

**Success Criteria**: Single command provisions dagorlad environment from clean state with same pattern as AWS Linux

**Timeline**: 2-3 days with test-first development approach

### Foundation: Idiomatic Ansible Configuration
**Completed**: Transitioned to idiomatic Ansible practices with proper inventory group_vars structure and automated vault password handling.

## Current Infrastructure Status

### Hetzner Cloud Linux (hobbiton)
**Status**: Production-ready persistent development environment
- Full GNOME desktop environment (~$4/month)
- Complete automation from provision to configured desktop
- Unified inventory patterns proven across production and test environments

### Vagrant Testing Environments
**Status**: Operational testing framework with proper variable management
- **Vagrant Docker (dagorlad)**: Ubuntu Linux testing with Docker backend
- **Vagrant Tart (lorien)**: macOS-compatible testing environment
- **Unified Variable Management**: Test environments use main project group_vars structure
- **Current Gap**: Requires separate `vagrant up` + configuration commands (target for unification)

### AWS Environments
**Status**: Multi-platform implementations operational
- **AWS Linux (rivendell)**: On-demand development server with unified command pattern
- **AWS Windows (moria)**: Windows application server for platform-specific applications
- **Pattern**: Uses consistent `provision.yml` with provider/platform parameters

## Architecture Patterns

### Multi-Provider Foundation
**Shared Patterns**:
- Dynamic inventory integration (AWS, Hetzner Cloud) and static inventory (Vagrant)
- Platform-based grouping (linux/windows) independent of provider
- Consistent SSH key management and credential patterns
- **Current Focus**: Extending unified command structure to Vagrant environments

**Provider-Specific Optimizations**:
- **Hetzner Cloud**: Persistent development environment with comprehensive desktop setup
- **AWS**: On-demand usage patterns with complete lifecycle management
- **Vagrant**: Local testing environments with Docker and Tart providers

### Key Implementation Specifications

**Hetzner Cloud Linux (hobbiton)**:
- cx22 (2 vCPU, 4GB RAM, 40GB SSD) in Helsinki
- Ubuntu 24.04 LTS with full GNOME desktop (~$4/month)
- Complete desktop applications, automatic backup/restore

**Vagrant Docker (dagorlad)**:
- Ubuntu Linux testing with Docker backend
- **Current Issue**: Uses separate `vagrant up` + `configure-linux.yml` commands
- **Target**: Unified `provision.yml` with `provider=vagrant_docker platform=linux`

## Current Inventory System

### Unified Multi-Provider Inventory
**Current Structure:**
```
inventories/
├── aws_ec2.yml                  # AWS dynamic inventory
├── hcloud.yml                   # Hetzner Cloud dynamic inventory  
├── vagrant_docker.yml           # Vagrant Docker static inventory
├── vagrant_tart.yml             # Vagrant Tart static inventory
└── group_vars/
    ├── all/vars.yml             # Global variables
    ├── linux/vars.yml           # Linux-specific variables
    ├── hcloud/vars.yml          # Hetzner-specific overrides
    ├── hcloud_linux/vars.yml    # Hetzner Linux-specific variables
    ├── vagrant_docker/vars.yml  # Vagrant Docker-specific variables
    └── vagrant_tart/vars.yml    # Vagrant Tart-specific variables
```

**Key Design Principles:**
- Single inventory directory with multiple provider files
- Cross-provider platform grouping (@linux, @windows) and provider-specific groups (@hcloud_linux, @vagrant_docker)
- Variable precedence: all → platform → provider → provider_platform
- Unified variable management across production and test environments

### Current Enhancement Opportunities
- **Unified Command Patterns**: Extend consistent `provision.yml` pattern to Vagrant environments
- **Testing Integration**: Leverage existing unified inventory for comprehensive testing workflows

## Key Technical Patterns

### Cross-Provider Patterns
- **Dynamic Inventory**: AWS EC2 and Hetzner Cloud plugins plus static Vagrant inventories
- **Platform Grouping**: Consistent linux/windows grouping across all providers
- **SSH Key Management**: Single SSH key pair working across environments
- **Credential Management**: Unified Ansible Vault patterns
- **Configuration Patterns**: Modular playbook structure reusable across providers

### Important Provider Specifics
**Hetzner Cloud Linux**: Complete GNOME desktop environment with backup/restore system (~$4/month)
**Vagrant Docker**: Ubuntu Linux testing environment requiring command pattern unification
**Testing Integration**: Unified variable management across production and test environments

## Next Steps
- **Current Focus**: Extend unified `provision.yml` pattern to Vagrant Docker environment
- **Pattern Target**: `ansible-playbook provision.yml --extra-vars "provider=vagrant_docker platform=linux"`
- **Foundation**: Leverage existing provider/platform parameter system and inventory structure
