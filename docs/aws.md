# AWS Documentation

This section covers using Amazon Web Services (AWS) EC2 for development environments.

## Available Environments

### Linux Development Environment
- [Create Linux VM](./aws/linux/create-linux-vm.md) - Complete setup guide for Ubuntu 24.04 LTS on AWS EC2

### Windows Server Environment  
- [Windows Server Usage Guide](./aws/windows/windows-server-usage.md) - Provisioning and usage instructions for Windows Server 2025
- [Windows Server Development Plan](./aws/windows/windows-server-development-plan.md) - Technical implementation details and timeline

## Prerequisites

All AWS environments require:
1. AWS account with programmatic access configured
2. Ansible Vault setup for encrypted secrets
3. SSH key pairs (see specific documentation for key type requirements)

Detailed setup instructions are provided in each environment's documentation.

## Integration

These AWS implementations integrate with the broader multi-provider automation system alongside Hetzner Cloud and local testing environments.