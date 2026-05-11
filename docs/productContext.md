# Product Context: Ansible All My Things

## Project Overview

An Infrastructure-as-Code automation system that provisions cross-platform development environments with AI agent safety controls. The system deploys automated command restrictions to target systems to ensure safe AI agent operation.

## Core Purpose

Automate complete lifecycle of development environments across cloud providers with built-in AI agent safety:

- **Cross-Platform Access**: Enable Windows-only applications from non-Windows host systems
- **Multi-Provider Infrastructure**: AWS EC2 and Hetzner Cloud automation
- **AI Agent Safety**: Command restrictions deployed to target systems via ansible
- **Cost Efficiency**: On-demand provisioning with complete resource cleanup

## Why This Project Exists

### The Problem
**Cross-Platform Development Complexity**: Modern development workflows require access to different operating systems and cloud providers, each with unique tools, applications, and deployment targets.

**Infrastructure Management Overhead**: Managing multiple cloud providers and platforms manually creates complexity, inconsistency, and cost inefficiencies.

**Platform-Specific Application Access**: Some applications are only available on specific platforms (e.g., Claude Desktop on Windows/macOS), creating gaps for users on other systems.

**AI Agent Safety Requirements**: Infrastructure automation projects require strict AI agent safety controls to prevent accidental resource provisioning or destruction on target systems.

### Key Requirements

#### Infrastructure Automation
- **Hetzner Cloud**: Persistent development environments (`hobbiton`)
- **AWS Linux**: On-demand development servers (`rivendell`)
- **AWS Windows**: Windows application servers (`moria`)
- **Vagrant Docker**: Linux testing environments (`dagorlad`)
- **Vagrant Tart**: macOS-compatible testing environments (`lorien`)
- **Complete Lifecycle**: Provision → Configure → Access → Destroy

#### Target Applications
- **Claude Desktop**: Windows-only application access
- **Development Tools**: Cross-platform development environments
- **Testing Infrastructure**: Vagrant-based testing environments

### Success Metrics

#### Infrastructure Performance
- Environment provisioning: 3-15 minutes depending on platform
- Cost optimization: Provider choice based on usage patterns
- Unified management: Single automation framework across providers

### The Solution
A unified, cross-provider automation system that provides automated access to development environments with built-in AI agent safety controls:

**Multi-Provider Infrastructure**: Automated environments across AWS and Hetzner Cloud
**Cross-Platform Support**: Both Linux and Windows environments with consistent patterns
**Cost Optimization**: Provider choice optimized for specific usage patterns and requirements
**Application Access**: Run platform-specific applications from any host system
**AI Agent Safety**: Command restrictions deployed to target systems via ansible
**Unified Management**: Single automation framework managing diverse infrastructure

### Technical Implementation

#### Multi-Provider Architecture
- Unified inventory system with dynamic host discovery
- Cross-provider SSH key management
- Idiomatic ansible configuration with vault encryption

#### Target System Deployment
- AI agents operate on provisioned systems (`hobbiton`, `rivendell`, `moria`)
- Command restrictions deployed during user provisioning
- Cross-platform ansible automation for Linux and Windows systems

## How It Works

Environments are provisioned, configured, accessed, and destroyed using Ansible playbooks. A unified `provision.yml` entrypoint accepts `provider` and `platform` parameters to target any supported environment with a single command.

For step-by-step instructions see [docs/user-manual/create-vm.md](user-manual/create-vm.md).

## Problems This Solves

### For Individual Users
**Cross-Provider Choice**: Freedom to select the cloud provider and platform that best fits each task — persistent Hetzner Cloud for daily development, on-demand AWS for intermittent workloads.
**Platform Access**: Run platform-specific applications (e.g., Claude Desktop) from any host OS without manual setup.
**Environment Isolation**: Each provisioned environment is reproducible and self-contained, preventing dependency conflicts with the local machine.
**Cost Control**: On-demand provisioning means resources are destroyed when not in use, eliminating idle charges.
**Flexibility**: Switch between Linux and Windows environments using the same automation framework without vendor lock-in.

### For Development Teams
**Consistent Environments**: Identical, reproducible development environments across team members
**Multi-Provider Strategy**: Avoid vendor lock-in with proven patterns across providers
**Platform Testing**: Access to both Linux and Windows environments for cross-platform development
**Cost Optimization**: Provider choice based on specific requirements and usage patterns
**Safe AI Agent Operation**: Prevent accidental infrastructure changes during development workflows

### Technical Benefits
**Provider Abstraction**: Proven automation patterns across AWS and Hetzner Cloud
**Scalability**: Framework ready for extension to additional providers and platforms
**Security**: Isolated environments with SSH key authentication and AI agent safety controls
**Operational Consistency**: Unified management approach despite different underlying technologies

## Success Indicators

### Quantitative Measures
**Cross-Provider Provisioning Performance**:
- Hetzner Cloud Linux: ~10-15 minutes for complete desktop environment
- AWS Linux: ~3-5 minutes for minimal server environment  
- AWS Windows: ~5 minutes for complete Windows Server environment

**Cost Optimization Across Providers**: For current pricing see the comments in the provider-specific group_vars files, e.g. [`inventories/group_vars/hcloud_linux/vars.yml`](../inventories/group_vars/hcloud_linux/vars.yml).

**Automation Coverage**:
- Zero manual configuration required across all implementations
- Complete lifecycle automation (provision → configure → destroy)
- Cross-provider SSH key management working
- AI agent safety controls deployed automatically

### Qualitative Measures
**Predictable command patterns**: The same `ansible-playbook provision.yml --extra-vars "provider=<x> platform=<y>"` interface works across providers.
**Consistent SSH key authentication**: A single key pair grants access to all provisioned environments regardless of provider.
**Unified automation framework**: New providers and platforms can be added by following existing playbook and inventory conventions, without redesigning the automation layer.
**Complete cloud environment cleanup**: Every cloud-provisioned environment (Hetzner Cloud, AWS) can be fully destroyed, leaving no orphaned resources or costs. Local Vagrant environments (dagorlad, lorien) are excluded — they incur no cloud cost.

### AI Agent Safety
**Command Blocking**: Infrastructure commands blocked on target systems
**Persistence**: Restrictions survive system reboots and updates
**Cross-Platform**: Works on Linux and Windows target systems
**Remote Verification**: Status checkable from control machine via ansible

## User Personas

### Cross-Platform Developer (Primary)
A developer working primarily on Linux or macOS who needs occasional access to Windows environments to run platform-specific applications (e.g., Claude Desktop, Windows-only tooling). They value automation over manual VM management and expect a single command to produce a ready-to-use environment.

### Cost-Conscious Developer (Primary)
A developer who self-funds cloud infrastructure and needs on-demand environments that cost nothing when not in use. They choose providers based on task duration: Hetzner for persistent daily work, AWS for intermittent workloads, Vagrant for local testing that incurs no cloud cost.

### Team Lead / DevOps Engineer (Secondary)
A technical lead responsible for ensuring that all team members work in identical, reproducible environments. They value the unified inventory system, idiomatic Ansible configuration, and the ability to extend the framework to new providers without rewriting existing automation.

## Integration Philosophy

Cross-provider infrastructure automation with built-in AI agent safety demonstrates that consistent automation patterns can work across diverse technologies while respecting each provider's strengths — without vendor lock-in. The system deploys command restrictions to target systems during infrastructure provisioning, ensuring safe AI agent operation throughout the development workflow.
