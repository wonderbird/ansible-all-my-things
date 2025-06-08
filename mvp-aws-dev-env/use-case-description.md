# MVP Use Case: Secure AWS Development Environment

## Problem Statement
I need a secure, isolated environment to safely test untrusted software (specifically LLMs with MCP support) for web development and backend server development without risking my local machine's security.

## Solution Overview
Create an on-demand AWS EC2 instance running Ubuntu that can be provisioned in 10-15 minutes before work sessions and completely destroyed afterward to eliminate ongoing costs.

## MVP Requirements

### Core Functionality
- **Provision**: Create a small AWS EC2 instance running Ubuntu 24.04 LTS
- **Configure**: Basic Ubuntu server setup (minimal, no desktop environment initially)
- **Access**: SSH access for command-line development work
- **Destroy**: Complete teardown of all AWS resources to ensure zero ongoing costs

### Technical Specifications
- **Instance Type**: t3.micro or t3.small (sufficient for LLM API calls to external providers)
- **Operating System**: Ubuntu 24.04 LTS
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
