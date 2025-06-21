# Active Context: Ansible All My Things

## Current Work Focus

### Windows Server Development (Primary Objective)
**Goal**: Extend AWS EC2 automation to support Windows Server instances for Claude Desktop Application access.

**Timeline**: Medium-term (1-3 months)

**Foundation**: AWS Linux implementation is working correctly with complete lifecycle management (provision → configure → destroy).

## Next Steps for Windows Server Implementation

### Phase 1: Research & Planning (Current)
- [ ] **Windows Server AMI Selection**: Research Windows Server 2022 AMIs with desktop experience
- [ ] **Instance Type Requirements**: Determine minimum specs for Windows Server + Claude Desktop
- [ ] **Cost Analysis**: Calculate Windows Server licensing + instance costs vs. target budget ($15/month)
- [ ] **RDP Configuration**: Plan secure RDP access setup and firewall rules

### Phase 2: Windows Provisioning
- [ ] **Create Windows Provisioner**: `provisioners/aws-windows.yml` based on existing `aws-ec2.yml`
- [ ] **Windows Inventory**: Extend AWS inventory to handle Windows instances
- [ ] **Security Groups**: Configure RDP (3389) access with IP restrictions
- [ ] **User Management**: Windows Administrator account setup and configuration

### Phase 3: Windows Configuration
- [ ] **Windows Ansible Modules**: Research `ansible.windows` collection requirements
- [ ] **Desktop Environment**: Enable Windows Server desktop experience
- [ ] **Claude Desktop Installation**: Automate Claude Desktop Application download and install
- [ ] **RDP Optimization**: Configure RDP for optimal desktop application performance

### Phase 4: Integration & Testing
- [ ] **End-to-End Testing**: Complete provision → configure → access → destroy cycle
- [ ] **Performance Validation**: Verify Claude Desktop responsiveness via RDP
- [ ] **Cost Validation**: Confirm actual costs align with budget targets
- [ ] **Documentation**: Create Windows Server usage guide

## Technical Considerations for Windows Server

### Key Differences from Linux Implementation
- **Authentication**: Windows uses WinRM instead of SSH
- **User Management**: Administrator vs. standard user accounts
- **Package Management**: Chocolatey or direct downloads vs. APT
- **Desktop Environment**: Windows Server desktop experience vs. Linux GUI
- **Access Method**: RDP (port 3389) vs. SSH (port 22)

### Windows-Specific Requirements
- **Ansible Collection**: `ansible.windows` for Windows module support
- **WinRM Configuration**: Windows Remote Management setup for Ansible
- **PowerShell**: Windows PowerShell for configuration tasks
- **Firewall**: Windows Firewall configuration for RDP access

### Cost Considerations
- **Windows Licensing**: Additional cost beyond Linux instances
- **Instance Size**: Windows Server requires larger instances (t3.medium minimum)
- **Storage**: Windows Server needs more disk space than Linux
- **Target Budget**: ~$15/month for typical usage patterns

## Current Architecture Strengths (Reusable for Windows)

### Proven Patterns from AWS Linux
- **Dynamic Inventory**: AWS EC2 plugin for automatic host discovery
- **Idempotent Provisioning**: Fixed instance identifiers prevent duplicates
- **Security Groups**: Automated firewall rule management
- **Complete Lifecycle**: Provision → configure → destroy automation
- **Cost Control**: Automatic resource cleanup

### Multi-Provider Foundation
- **Provider Abstraction**: Clean separation between provisioning and configuration
- **Ansible Vault**: Encrypted credential management
- **Modular Design**: Individual playbooks for specific functionality

## Windows Server Planning Details

### Target Configuration
- **OS**: Windows Server 2022 with Desktop Experience
- **Instance Type**: t3.medium (2 vCPU, 4GB RAM minimum for GUI)
- **Storage**: 50GB GP3 EBS (Windows Server space requirements)
- **Network**: RDP access from user's IP address only
- **Applications**: Claude Desktop Application + supporting software

### Estimated Costs (Monthly)
- **t3.medium**: ~$30/month (720 hours × $0.0416/hour)
- **Windows License**: Included in AWS Windows AMI pricing
- **Storage**: 50GB × $0.08/GB = $4/month
- **Total**: ~$34/month if running continuously
- **Target Usage**: 10-15 hours/week = ~$15/month actual cost

### Security Model
- **RDP Access**: Restricted to user's IP address
- **Windows Firewall**: Configured for minimal exposure
- **User Accounts**: Separate Administrator and standard user accounts
- **Credential Management**: Windows passwords via Ansible Vault

## Important Learnings from AWS Linux (Applicable to Windows)

### Successful Patterns to Reuse
- **Fixed Instance Naming**: Use consistent identifiers for idempotency
- **Dynamic Inventory**: Automatic host discovery reduces configuration
- **Security Group Management**: Automated firewall rule creation
- **Complete Cleanup**: Host key removal and resource termination

### AWS-Specific Considerations
- **Region Selection**: eu-north-1 for cost optimization
- **AMI Selection**: Use latest Windows Server 2022 AMIs
- **Instance Lifecycle**: Proper startup/shutdown handling for Windows
- **Tagging Strategy**: Consistent resource tagging for management

## Context for Future Work

### Extension Opportunities
- **Additional Windows Applications**: Extend beyond Claude Desktop
- **Windows Development Tools**: Visual Studio, .NET development environment
- **Multi-Application Support**: Multiple Windows-only applications per instance
- **Performance Optimization**: GPU instances for graphics-intensive applications

### Integration with Existing System
- **Consistent Commands**: Same playbook patterns as Linux implementation
- **Shared Infrastructure**: Reuse AWS credentials and networking setup
- **Documentation Alignment**: Windows guides following Linux documentation patterns

## Memory Bank Maintenance Notes
- **Focus**: Windows Server development for Claude Desktop Application
- **Foundation**: AWS Linux implementation working correctly
- **Timeline**: Medium-term (1-3 months) implementation
- **Next Review**: After Windows Server research and planning phase completion
