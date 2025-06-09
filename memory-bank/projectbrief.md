# Project Brief: Ansible All My Things

## Project Overview
An Ansible-based infrastructure automation system for personal IT environment management, inspired by the 36c3 talk "Ansible all the Things" by Heiko Borchers.

## Core Purpose
Automate the complete lifecycle of personal development environments across multiple cloud providers and local testing environments, with emphasis on:
- **Cross-Architecture Support**: Enable amd64 development from Apple Silicon (arm64) host systems
- **Platform Diversity**: Support Linux and Windows development environments
- Reproducible system configurations
- Secure credential management
- Multi-provider support
- Complete environment lifecycle management (provision → configure → backup → destroy)

## Key Requirements

### Multi-Provider Support
- **Hetzner Cloud**: Primary cloud provider for amd64 Linux environments
- **AWS EC2**: Target for both Linux and Windows development environments
  - Current: Linux (Ubuntu) for amd64 compatibility and secure testing
  - Future: Windows Server for Windows-specific development tools
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
**MVP AWS Development Environment**: Creating secure, isolated AWS EC2 environments that provide:
- **amd64 Architecture Access**: Run x86_64 tools unavailable on Apple Silicon
- **Secure Testing Environment**: Isolated environment for untrusted software (LLMs with MCP support)
- **Cross-Platform Foundation**: Linux implementation as stepping stone to Windows support
- **Cost Efficiency**: 10-15 minute provisioning with complete resource cleanup

**Long-term Vision**: Extend AWS support to include Windows Server instances for Windows-specific development tools and applications not available on macOS/Linux.

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
