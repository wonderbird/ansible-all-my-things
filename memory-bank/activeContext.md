# Active Context: Ansible All My Things

## Current Work Focus

### Windows Server MVP (URGENT - Primary Objective)
**Goal**: Deliver minimal viable Windows Server with Claude Desktop access for immediate work needs.

**Timeline**: URGENT (2-3 days delivery)

**Business Context**: User needs Claude Desktop access for current work projects - immediate delivery required.

**Foundation**: AWS Linux implementation is working correctly with complete lifecycle management (provision → configure → destroy).

**Cost Acceptance**: Higher costs (~$60/month) acceptable initially, optimize later.

## Next Steps for Windows Server MVP

### Day 1: Windows Server Provisioning (Current)
- [ ] **Create Windows Provisioner**: Copy `provisioners/aws-ec2.yml` → `provisioners/aws-windows.yml`
- [ ] **Windows Server AMI**: Use Windows Server 2022 with Desktop Experience (latest AMI)
- [ ] **Instance Configuration**: t3.large (4 vCPU, 8GB RAM) for reliability over cost
- [ ] **Security Group**: RDP (port 3389) access from user's IP address
- [ ] **Administrator Setup**: Simple password-based authentication

### Day 2: Windows Configuration & Claude Desktop
- [ ] **Install ansible.windows**: Add Windows Ansible collection support
- [ ] **Windows Inventory**: Extend AWS inventory to handle Windows instances
- [ ] **RDP Configuration**: Enable RDP and configure Windows Firewall
- [ ] **Claude Desktop**: Manual installation via PowerShell (automated later)
- [ ] **Basic User Setup**: Administrator account configuration

### Day 2-3: Integration & Testing
- [ ] **Playbook Integration**: Create `provision-aws-windows.yml` and `destroy-aws-windows.yml`
- [ ] **End-to-End Testing**: Complete provision → RDP access → Claude Desktop → destroy cycle
- [ ] **Access Validation**: Verify Claude Desktop works for actual work tasks
- [ ] **Basic Documentation**: Quick usage guide for Windows Server access

## MVP vs Long-term Approach

### MVP Scope (Urgent - Next 2-3 Days)
- **Goal**: Working Windows Server with Claude Desktop access
- **Quality**: "Good enough" - reliable but not optimized
- **Cost**: ~$60/month acceptable initially
- **Features**: Basic RDP access, Claude Desktop working
- **Documentation**: Minimal usage instructions

### Future Optimization Track (After MVP)
- **Cost Optimization**: Target $15/month through smaller instances and usage patterns
- **Automated Installation**: Full Claude Desktop automation
- **Advanced Security**: Comprehensive security configurations
- **Performance Tuning**: RDP and application optimization
- **Comprehensive Documentation**: Complete usage and troubleshooting guides

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

### MVP Cost Estimates (Monthly)
- **t3.large**: ~$60/month (720 hours × $0.0832/hour)
- **Windows License**: Included in AWS Windows AMI pricing
- **Storage**: 50GB × $0.08/GB = $4/month
- **Total**: ~$64/month if running continuously
- **Actual Usage**: On-demand usage for work sessions
- **Cost Acceptance**: Higher costs acceptable for urgent delivery

### Future Optimization Targets
- **t3.medium**: ~$30/month (after optimization)
- **Target Usage**: 10-15 hours/week = ~$15/month actual cost
- **Timeline**: Optimize after MVP is working and immediate needs are met

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
