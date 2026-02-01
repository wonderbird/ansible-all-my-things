# Product Context: Ansible All My Things

## Why This Project Exists

### The Problem
**Cross-Platform Development Complexity**: Modern development workflows require access to different operating systems and cloud providers, each with unique tools, applications, and deployment targets.

**Infrastructure Management Overhead**: Managing multiple cloud providers and platforms manually creates complexity, inconsistency, and cost inefficiencies.

**Platform-Specific Application Access**: Some applications are only available on specific platforms (e.g., Claude Desktop on Windows/macOS), creating gaps for users on other systems.

**AI Agent Safety Requirements**: Infrastructure automation projects require strict AI agent safety controls to prevent accidental resource provisioning or destruction on target systems.

### The Solution
A unified, cross-provider automation system that provides automated access to development environments with built-in AI agent safety controls:

**Multi-Provider Infrastructure**: Automated environments across AWS and Hetzner Cloud
**Cross-Platform Support**: Both Linux and Windows environments with consistent patterns
**Cost Optimization**: Provider choice optimized for specific usage patterns and requirements
**Application Access**: Run platform-specific applications from any host system
**AI Agent Safety**: Command restrictions deployed to target systems via ansible
**Unified Management**: Single automation framework managing diverse infrastructure

## How It Works

### Multi-Provider User Experience

**Hetzner Cloud Linux (Persistent Development)**:
```bash
ansible-playbook provision.yml
ssh galadriel@$HOBBITON_IP
ansible-playbook destroy.yml
```

**AWS Linux (On-Demand Development)**:
```bash
ansible-playbook provision-aws-linux.yml
ssh galadriel@$RIVENDELL_IP
ansible-playbook destroy-aws.yml
```

**AWS Windows (Application Access)**:
```bash
ansible-playbook provision-aws-windows.yml
ssh galadriel@$MORIA_IP  # Command-line access
# RDP connection available for desktop applications
ansible-playbook destroy-aws.yml
```

### Primary Workflows

**Persistent Development Environment (Hetzner Cloud)**:
1. **Provision**: Complete GNOME desktop environment (~10-15 minutes)
2. **Configure**: Automatic application installation and user setup with command restrictions
3. **Access**: SSH with full desktop environment and AI agent safety controls
4. **Destroy**: Complete cleanup with data backup

**Cross-Platform Application Access (AWS Windows)**:
1. **Provision**: Windows Server 2025 instance with desktop environment (~5 minutes)
2. **Configure**: Automatic Chocolatey installation, RDP optimization, and command restrictions
3. **Access**: SSH and RDP connections to Windows Server environment with AI agent safety
4. **Use**: Ready for Claude Desktop and other Windows applications
5. **Destroy**: Complete environment cleanup

### AI Agent Safety on Target Systems

**Command Restriction Deployment**: 
- Restrictions deployed to target systems (`hobbiton`, `rivendell`, `moria`) via ansible
- Applied to `desktop_users` accounts (`galadriel`, `legolas`) during provisioning
- Cross-platform implementation for Linux and Windows target systems

**Blocked Commands**: `ansible`, `vagrant`, `docker`, `aws`, `hcloud` and related tools
**User Access**: Restrictions apply only to AI agents, users retain full command access

## Problems This Solves

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

**Cost Optimization Across Providers**:
- Hetzner Cloud: ~$4/month with predictable pricing
- AWS Linux: ~$8-10/month with on-demand optimization
- AWS Windows: ~$60/month base with on-demand reducing actual costs

**Automation Coverage**:
- Zero manual configuration required across all implementations
- Complete lifecycle automation (provision → configure → destroy)
- Cross-provider SSH key management working
- AI agent safety controls deployed automatically

### AI Agent Safety
**Command Blocking**: Infrastructure commands blocked on target systems
**Persistence**: Restrictions survive system reboots and updates
**Cross-Platform**: Works on Linux and Windows target systems
**Remote Verification**: Status checkable from control machine via ansible

## Integration Philosophy

Cross-provider infrastructure automation with built-in AI agent safety demonstrates that consistent automation patterns can work across diverse technologies while maintaining security. The system deploys command restrictions to target systems during infrastructure provisioning, ensuring safe AI agent operation throughout the development workflow.