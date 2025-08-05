# Project Brief: Ansible All My Things

## Project Overview

An Infrastructure-as-Code automation system that provisions cross-platform development environments with AI agent safety controls. The system deploys automated command restrictions to target systems to ensure safe AI agent operation.

## Core Purpose

Automate complete lifecycle of development environments across cloud providers with built-in AI agent safety:

- **Cross-Platform Access**: Enable Windows-only applications from non-Windows host systems
- **Multi-Provider Infrastructure**: AWS EC2 and Hetzner Cloud automation
- **AI Agent Safety**: Command restrictions deployed to target systems via ansible
- **Cost Efficiency**: On-demand provisioning with complete resource cleanup
- **Target System Security**: Prevent infrastructure commands on provisioned systems

## Key Requirements

### Infrastructure Automation
- **AWS Linux**: On-demand development servers (`rivendell`)
- **AWS Windows**: Windows application servers (`moria`) 
- **Hetzner Cloud**: Persistent development environments (`hobbiton`)
- **Complete Lifecycle**: Provision → Configure → Access → Destroy

### AI Agent Safety on Target Systems
- **Command Restrictions**: Block infrastructure commands on target systems
- **Target Users**: Apply to `desktop_users` accounts (`galadriel`, `legolas`)
- **Cross-Platform**: Work on Linux and Windows target systems
- **Ansible Deployment**: Deploy restrictions via infrastructure automation

### Target Applications
- **Claude Desktop**: Windows-only application access
- **Development Tools**: Cross-platform development environments
- **Testing Infrastructure**: Vagrant-based testing environments

## Current Status

### Infrastructure ✅ OPERATIONAL
- **AWS Linux**: Production-ready development servers
- **AWS Windows**: Production-ready Windows application servers
- **Hetzner Cloud**: Production-ready persistent environments
- **Testing Framework**: Comprehensive Vagrant-based testing

### AI Agent Safety 🔴 IMPLEMENTATION READY
- **AppArmor Selected**: Kernel-level command restrictions for Linux target systems
- **Implementation Strategy**: Manual spike validation on rivendell, then ansible automation
- **Target Systems**: Deploy to `hobbiton` and `rivendell` with `moria` deferred until needed

## Success Metrics

### Infrastructure Performance
- Environment provisioning: 3-15 minutes depending on platform
- Cost optimization: Provider choice based on usage patterns
- Unified management: Single automation framework across providers

### AI Agent Safety
- Command blocking: Infrastructure commands blocked on target systems
- Persistence: Restrictions survive system reboots and updates
- Remote verification: Status checkable from control machine via ansible

## Technical Implementation

### Multi-Provider Architecture
- Unified inventory system with dynamic host discovery
- Cross-provider SSH key management
- Idiomatic ansible configuration with vault encryption

### Target System Deployment
- AI agents operate on provisioned systems (`hobbiton`, `rivendell`, `moria`)
- Command restrictions deployed during user provisioning
- Cross-platform ansible automation for Linux and Windows systems
