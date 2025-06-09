# Project Brief: Ansible All My Things

## Project Overview
An Ansible-based infrastructure automation system for personal IT environment management, inspired by the 36c3 talk "Ansible all the Things" by Heiko Borchers.

## Core Purpose
Automate the complete lifecycle of personal development environments across multiple cloud providers and local testing environments, with emphasis on:
- Reproducible system configurations
- Secure credential management
- Multi-provider support
- Complete environment lifecycle management (provision → configure → backup → destroy)

## Key Requirements

### Multi-Provider Support
- **Hetzner Cloud**: Primary cloud provider for production environments
- **AWS EC2**: New target for secure development environments (MVP in progress)
- **Local Testing**: Vagrant with Docker, Tart, and VirtualBox providers

### Complete Lifecycle Management
1. **Provision**: Create infrastructure (VMs, networking, storage)
2. **Configure**: Set up users, install software, configure desktop environments
3. **Backup**: Save critical settings and data
4. **Restore**: Apply backed-up configurations to new systems
5. **Destroy**: Complete teardown to eliminate costs

### Security & Credential Management
- Ansible Vault encryption for all secrets
- Separate admin and desktop users
- SSH key-based authentication
- Provider-specific credential handling (HCLOUD_TOKEN, AWS credentials)

### System Configuration Capabilities
- User account management with sudo privileges
- Basic system setup (packages, security, networking)
- Development environment (Node.js, TypeScript, Homebrew)
- Desktop environment setup (when supported)
- Application installation and configuration (VS Code, Chromium)
- Keyring and settings backup/restore

## Current Development Focus
**MVP AWS Development Environment**: Creating a secure, isolated AWS EC2 environment for testing untrusted software (LLMs with MCP support) that can be provisioned in 10-15 minutes and completely destroyed to eliminate ongoing costs.

## Success Metrics
- Environments can be provisioned in 10-15 minutes
- Complete configuration automation with zero manual intervention
- Secure credential management with no secrets in version control
- Cost-effective operation through complete resource cleanup
- Consistent experience across all supported providers

## Technical Constraints
- All secrets encrypted with Ansible Vault
- No persistent infrastructure (except during active use)
- Provider-agnostic playbook design where possible
- Support for both headless and desktop environments
