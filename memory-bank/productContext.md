# Product Context: Ansible All My Things

## Why This Project Exists

### The Problem
Managing personal development environments across multiple cloud providers and local systems is complex, time-consuming, and error-prone. Manual setup leads to:
- Inconsistent configurations across environments
- Hours spent recreating development setups
- Security risks from manual credential management
- Vendor lock-in to specific cloud providers
- Ongoing costs from forgotten cloud resources

### Cross-Architecture Challenge
**Apple Silicon Limitation**: Development on Apple Silicon (arm64) systems lacks access to amd64 (x86_64) architecture tools and software. Many development tools, legacy applications, and testing environments are only available for x86_64, creating a significant gap in development capabilities.

**Security Isolation Need**: Testing untrusted software (such as LLMs with MCP support) requires secure, isolated environments that don't risk the local machine's security. Cloud-based environments provide complete isolation with the ability to destroy compromised systems entirely.

**Specific Use Case**: Need access to amd64 architecture for development tools unavailable on Apple Silicon, while providing secure isolation for testing untrusted software (specifically LLMs with MCP support) without risking local machine security. Usage pattern: ~10-15 hours/week with complete provision → work → destroy lifecycle.

### The Solution Vision
A unified, automated system that treats infrastructure as code, enabling:
- **Reproducible Environments**: Identical setups across any supported provider
- **Cost Control**: Complete resource lifecycle management with automatic cleanup
- **Security**: Encrypted credential management and consistent security practices
- **Provider Flexibility**: Switch between Hetzner, AWS, or local testing without changing workflows
- **Time Savings**: 10-15 minute automated provisioning vs hours of manual work

## How It Should Work

### User Experience Goals

#### Simple Commands, Complex Results
```bash
# Provision and configure a complete development environment
ansible-playbook provision.yml -i inventories/hcloud/

# Back up current settings before changes
ansible-playbook backup.yml -i inventories/hcloud/

# Completely destroy environment to stop costs
ansible-playbook destroy.yml -i inventories/hcloud/
```

#### Consistent Experience Across Providers
Whether using Hetzner Cloud for production work or AWS for secure testing, the user experience remains identical. Only the inventory file changes.

#### Zero-Touch Security
- All secrets encrypted with Ansible Vault
- No manual credential entry during provisioning
- Automatic SSH key management
- Consistent user account setup across all environments

### Target Workflows

#### Cross-Architecture Development
1. **Provision**: `ansible-playbook provision-aws.yml` → amd64 environment ready in 10-15 minutes
2. **Develop**: Access to x86_64 tools unavailable on Apple Silicon
3. **Test**: Secure isolation for untrusted software testing
4. **Destroy**: `ansible-playbook destroy-aws.yml` → Zero ongoing costs

#### Daily Development Work
1. **Morning**: `ansible-playbook provision.yml` → Ready to work in 10-15 minutes
2. **Work**: Full development environment with all tools and settings
3. **Evening**: `ansible-playbook destroy.yml` → Zero ongoing costs

#### Environment Migration
1. **Backup**: Save current settings and configurations
2. **Provision**: Create new environment (same or different provider)
3. **Restore**: Apply backed-up configurations automatically
4. **Verify**: Identical working environment ready immediately

#### Secure Testing
1. **Isolate**: Provision dedicated environment for untrusted software
2. **Test**: Run potentially dangerous code in complete isolation
3. **Destroy**: Complete environment elimination after testing

## Problems This Solves

### For Individual Users
- **Cross-Architecture Access**: Run amd64 tools from Apple Silicon host systems
- **Secure Testing**: Isolated environments for untrusted software without local risk
- **Time Recovery**: Eliminate hours of manual environment setup
- **Cost Control**: Never pay for forgotten cloud resources
- **Consistency**: Identical environments reduce configuration debugging
- **Security**: Proper credential management without manual processes
- **Flexibility**: Easy provider switching based on needs or pricing

### For Development Teams
- **Onboarding**: New team members get identical environments instantly
- **Reproducibility**: "Works on my machine" problems eliminated
- **Documentation**: Infrastructure configuration is self-documenting code
- **Compliance**: Consistent security practices across all environments

## Success Indicators

### Quantitative Measures
- Environment provisioning time: ≤15 minutes
- Configuration drift: Zero (everything automated)
- Manual intervention required: Zero after initial setup
- Cost from forgotten resources: Zero (automatic cleanup)

### Qualitative Measures
- User confidence in trying new providers
- Reduced anxiety about cloud costs
- Faster experimentation with new tools
- Consistent development experience regardless of underlying infrastructure

## User Personas

### Primary: Solo Developer/Consultant
- Needs flexible, cost-effective development environments
- Works with multiple clients requiring different setups
- Values time savings and cost control
- Requires security for client work

### Secondary: Small Development Team
- Needs consistent environments across team members
- Wants to eliminate "works on my machine" issues
- Requires reproducible deployment processes
- Values infrastructure as code practices

## Integration Philosophy
This system should feel like a natural extension of existing development workflows, not a separate tool requiring context switching. It leverages familiar Ansible patterns while hiding complexity behind simple, memorable commands.
