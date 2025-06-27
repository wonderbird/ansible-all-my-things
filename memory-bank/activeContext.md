# Active Context: Ansible All My Things

## Current Work Focus

### Windows Server MVP (END-TO-END TESTING IN PROGRESS)
**Goal**: Deliver minimal viable Windows Server with Claude Desktop access for immediate work needs.

**Status**: END-TO-END TESTING IN PROGRESS - User currently testing deployment

**Business Context**: User needs Claude Desktop access for current work projects - MVP implementation completed, testing phase active.

**Foundation**: Successfully extended AWS Linux implementation to Windows Server with complete lifecycle management.

**Implementation**: Complete Windows Server 2025 automation with RDP access and Claude Desktop workflow ready for validation.

## Detailed Development Tasks for Windows Server MVP

### Day 1: Windows Server Provisioning

#### Task 1.1: Create Windows Provisioner
- **File**: `provisioners/aws-windows.yml`
- **Approach**: Copy existing `provisioners/aws-ec2.yml` and modify for Windows
- **Key Changes**:
  - Windows Server 2025 AMI with Desktop Experience
  - t3.large instance type (4 vCPU, 8GB RAM)
  - Windows-specific security group with RDP (port 3389)
  - Administrator password setup
- **Acceptance Criteria**: 
  - Provisioner creates Windows Server instance
  - Instance boots successfully with desktop experience
  - RDP port accessible from user's IP
- **Estimated Effort**: 2-3 hours

#### Task 1.2: Windows Security Group Configuration
- **File**: Update security group configuration in provisioner
- **Requirements**:
  - RDP (port 3389) access from user's IP address only
  - Windows Remote Management (WinRM) for Ansible (ports 5985/5986)
  - Outbound internet access for downloads
- **Acceptance Criteria**:
  - RDP connection possible from user's machine
  - Security group restricts access appropriately
- **Estimated Effort**: 1 hour

#### Task 1.3: Administrator Account Setup
- **Approach**: Simple password-based authentication for MVP
- **Requirements**:
  - Set Administrator password via user data script
  - Enable RDP for Administrator account
  - Configure Windows for remote access
- **Acceptance Criteria**:
  - Can connect via RDP using Administrator credentials
  - Desktop environment accessible
- **Estimated Effort**: 1-2 hours

### Day 2: Windows Configuration & Claude Desktop

#### Task 2.1: Install ansible.windows Collection
- **Command**: `ansible-galaxy collection install ansible.windows`
- **Purpose**: Enable Windows-specific Ansible modules
- **Acceptance Criteria**:
  - Collection installed successfully
  - Windows modules available for use
- **Estimated Effort**: 30 minutes

#### Task 2.2: Extend AWS Inventory for Windows
- **File**: Update `inventories/aws/aws_ec2.yml`
- **Requirements**:
  - Include Windows instances in inventory
  - Configure WinRM connection settings
  - Set appropriate connection variables
- **Acceptance Criteria**:
  - Windows instances appear in Ansible inventory
  - Ansible can connect to Windows instances via WinRM
- **Estimated Effort**: 1-2 hours

#### Task 2.3: Basic Windows Configuration Playbook
- **File**: Create `playbooks/setup-windows-basics.yml`
- **Requirements**:
  - Configure Windows Firewall for RDP
  - Enable necessary Windows features
  - Basic system configuration
- **Acceptance Criteria**:
  - RDP access reliable and stable
  - Windows configured for desktop application use
- **Estimated Effort**: 2-3 hours

#### Task 2.4: Claude Desktop Installation (Manual)
- **Approach**: PowerShell script for manual installation
- **Requirements**:
  - Download Claude Desktop installer
  - Install application silently
  - Configure for immediate use
- **Acceptance Criteria**:
  - Claude Desktop launches successfully
  - Application functional for work tasks
- **Estimated Effort**: 1-2 hours

### Day 2-3: Integration & Testing

#### Task 3.1: Create Main Playbooks
- **Files**: 
  - `provision-aws-windows.yml`
  - `destroy-aws-windows.yml`
- **Requirements**:
  - Follow same patterns as Linux playbooks
  - Include Windows-specific provisioning and configuration
  - Complete lifecycle management
- **Acceptance Criteria**:
  - Single command provisions complete Windows environment
  - Single command destroys all resources
- **Estimated Effort**: 2-3 hours

#### Task 3.2: End-to-End Testing
- **Process**:
  1. Run provision playbook
  2. Connect via RDP
  3. Launch Claude Desktop
  4. Perform actual work tasks
  5. Run destroy playbook
- **Acceptance Criteria**:
  - Complete cycle works reliably
  - Claude Desktop suitable for real work
  - All resources cleaned up properly
- **Estimated Effort**: 2-3 hours

#### Task 3.3: Basic Documentation
- **File**: `docs/windows-server-mvp-usage.md`
- **Content**:
  - Quick start guide
  - RDP connection instructions
  - Basic troubleshooting
  - Cost warnings and management
- **Acceptance Criteria**:
  - User can follow documentation to use Windows Server
  - Common issues addressed
- **Estimated Effort**: 1-2 hours

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
- **OS**: Windows Server 2025 with Desktop Experience
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
- **Region Selection**: eu-north-1 for carbon footprint and latency optimization
- **AMI Selection**: Use latest Windows Server 2025 AMIs
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
