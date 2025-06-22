# Project Brief: Ansible All My Things

## Project Overview
An Ansible-based infrastructure automation system for personal IT environment management, enabling cross-platform development environments with focus on Windows Server support for applications unavailable on Linux/macOS.

## Core Purpose
Automate complete lifecycle of development environments across cloud providers, with emphasis on:
- **Cross-Platform Access**: Enable Windows-only applications from non-Windows host systems
- **AWS Windows Server**: Primary target for Windows-specific applications
- **AWS Linux Foundation**: Proven foundation for Windows Server extension
- **Application Focus**: Claude Desktop Application as primary Windows use case
- **Cost Efficiency**: On-demand provisioning with complete resource cleanup

## Key Requirements

### Windows Server Development (Dual-Track Approach)

#### Track 1: MVP (URGENT - Primary Focus)
- **Target Application**: Claude Desktop Application (Windows-only)
- **Platform**: AWS EC2 Windows Server instances (t3.large)
- **Access Method**: RDP for desktop environment interaction
- **Foundation**: Extend existing AWS Linux implementation
- **Timeline**: URGENT (2-3 days delivery)
- **Business Driver**: Immediate Claude Desktop access for current work projects
- **Cost Acceptance**: ~$60/month initially acceptable

#### Track 2: Long-term Optimization (Future)
- **Goal**: Cost-optimized, fully automated Windows Server solution
- **Timeline**: 1-2 months after MVP delivery
- **Target Cost**: $15/month for typical usage patterns
- **Quality**: Production-ready with comprehensive automation
- **Features**: Advanced security, performance tuning, full automation

### Multi-Provider Foundation (Established)
- **AWS EC2**: Working Linux implementation, target for Windows Server
- **Hetzner Cloud**: Production-ready Linux environments
- **Local Testing**: Vagrant-based testing for Linux configurations

### Complete Lifecycle Management
1. **Provision**: Create Windows Server infrastructure on AWS
2. **Configure**: Install Claude Desktop and supporting software
3. **Access**: RDP-based desktop environment access
4. **Destroy**: Complete teardown to eliminate costs

## Current Status
- **AWS Linux**: Production-ready with complete lifecycle management
- **Hetzner Cloud**: Production-ready reference implementation
- **Windows Server**: Planning phase for Claude Desktop Application support

## Success Metrics
- Windows Server environments provisioned in 15-20 minutes
- Claude Desktop Application accessible via RDP
- Cost-effective operation under $15/month for typical usage
- Consistent automation patterns across Linux and Windows

## Technical Constraints
- Windows Server licensing costs (factor into budget)
- RDP access requirements for desktop applications
- Windows-specific Ansible modules and approaches
- Larger instance types needed for Windows Server GUI
