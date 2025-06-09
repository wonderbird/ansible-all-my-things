# MVP Use Case: Cross-Architecture AWS Development Environment

## Problem Statement
I need access to amd64 (x86_64) architecture for development tools and software that are not available on Apple Silicon (arm64), while also providing a secure, isolated environment to safely test untrusted software (specifically LLMs with MCP support) without risking my local machine's security.

## Solution Overview
Create an on-demand AWS EC2 instance running Ubuntu on amd64 architecture that can be provisioned in 10-15 minutes before work sessions and completely destroyed afterward to eliminate ongoing costs. This provides both cross-architecture compatibility and secure isolation for development work.

## MVP Requirements

### Core Functionality
- **Provision**: Create a small AWS EC2 instance running Ubuntu 24.04 LTS on amd64 architecture
- **Configure**: Basic Ubuntu server setup (minimal, no desktop environment initially)
- **Access**: SSH access for command-line development work
- **Cross-Architecture Support**: Enable running x86_64 tools unavailable on Apple Silicon
- **Destroy**: Complete teardown of all AWS resources to ensure zero ongoing costs

### Technical Specifications
- **Architecture**: amd64 (x86_64) for compatibility with tools unavailable on Apple Silicon
- **Instance Type**: t3.micro or t3.small (sufficient for LLM API calls and development tools)
- **Operating System**: Ubuntu 24.04 LTS (foundation for future Windows Server support)
- **Storage**: 20GB GP3 EBS volume (cost-effective, adequate for basic development)
- **Network**: Default VPC with SSH access (port 22) from user's IP
- **Security**: Standard AWS isolation, basic Ubuntu security hardening

### Usage Pattern
- **Frequency**: ~1 hour weekdays, 3-5 hours weekends (10-15 hours/week)
- **Lifecycle**: Provision → Work → Destroy (no persistent infrastructure)
- **Access Method**: SSH command line (graphical interface for future iteration)

### Integration Requirements
- **Ansible Integration**: Follow existing project patterns (similar to Hetzner Cloud implementation)
- **Inventory Management**: Dynamic inventory using AWS EC2 plugin
- **Configuration Management**: Reuse existing playbooks where applicable
- **Credential Management**: AWS credentials via environment variables (similar to HCLOUD_TOKEN)

## Success Criteria
1. Can provision AWS Ubuntu VM in 10-15 minutes using `ansible-playbook provision-aws.yml`
2. Can SSH into the instance and perform basic development tasks
3. Can completely destroy all AWS resources using `ansible-playbook destroy-aws.yml`
4. Zero AWS costs when not actively using the environment
5. Follows same patterns as existing Hetzner Cloud implementation

## Out of Scope (Future Iterations)
- Graphical desktop environment
- Windows Server instances (planned for future implementation)
- Advanced security hardening
- GPU instances for local LLM hosting
- Persistent storage or data backup
- Multi-region deployment
- Auto-scaling or load balancing

## Cost Estimation
- **t3.micro**: ~$0.0104/hour × 15 hours/week = ~$6.50/month
- **Storage**: 20GB GP3 × $0.08/GB/month = ~$1.60/month (only when running)
- **Data Transfer**: Minimal for development use
- **Total**: ~$8-10/month maximum (only when actively used)

## Risk Mitigation
- **Cost Control**: Complete resource destruction prevents runaway costs
- **Security**: Standard AWS isolation adequate for testing untrusted software
- **Simplicity**: Minimal configuration reduces complexity and maintenance overhead
