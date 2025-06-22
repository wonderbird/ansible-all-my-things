# Active Product Increment: Windows Server MVP

## Increment Overview

**Title**: Minimal Viable Windows Server with Claude Desktop Access

**Business Value**: Immediate Claude Desktop access for current work projects

**Timeline**: 2-3 days (URGENT delivery)

**Success Criteria**: Single command → Windows Server → RDP → Claude Desktop → Destroy

## Product Increment Specification

### What We're Building
A minimal viable Windows Server automation that extends the existing AWS Linux foundation to provide immediate Claude Desktop access via RDP.

### What We're NOT Building (Out of Scope)
- Cost optimization (accept ~$60/month initially)
- Automated Claude Desktop installation (manual PowerShell for MVP)
- Advanced security configurations
- Performance tuning
- Comprehensive documentation

## Development Tasks

### Day 1: Windows Server Provisioning

#### Task 1.1: Create Windows Provisioner
- **File**: `provisioners/aws-windows.yml`
- **Approach**: Copy existing `provisioners/aws-ec2.yml` and modify for Windows
- **Key Changes**:
  - Windows Server 2022 AMI with Desktop Experience
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

## Technical Specifications

### Instance Configuration
- **AMI**: Windows Server 2022 with Desktop Experience (latest)
- **Instance Type**: t3.large (4 vCPU, 8GB RAM)
- **Storage**: 50GB GP3 EBS
- **Region**: eu-north-1 (cost optimization)

### Network Configuration
- **Security Group**: Custom Windows security group
- **RDP Access**: Port 3389 from user's IP only
- **WinRM Access**: Ports 5985/5986 for Ansible
- **Outbound**: Full internet access for downloads

### Cost Estimates
- **Instance**: ~$60/month if running continuously
- **Storage**: ~$4/month
- **Total**: ~$64/month maximum
- **Actual Usage**: On-demand for work sessions

### Authentication
- **Method**: Administrator password (stored in Ansible Vault)
- **RDP**: Standard Windows RDP client
- **Ansible**: WinRM with password authentication

## Success Metrics

### Functional Requirements
- [ ] Windows Server provisions in ≤20 minutes
- [ ] RDP connection establishes reliably
- [ ] Claude Desktop launches and functions normally
- [ ] Can perform actual work tasks via RDP
- [ ] Complete environment destroys in ≤5 minutes

### Quality Requirements
- [ ] Process is repeatable and reliable
- [ ] No manual intervention required after initial setup
- [ ] Error handling for common failure scenarios
- [ ] Basic troubleshooting documentation available

### Business Requirements
- [ ] Immediate access to Claude Desktop for work projects
- [ ] Cost acceptable for urgent delivery (~$60/month)
- [ ] Foundation established for future optimization
- [ ] User can work productively via RDP

## Risk Mitigation

### Technical Risks
- **Windows AMI Selection**: Use latest Windows Server 2022 with Desktop Experience
- **RDP Performance**: Use t3.large for adequate performance
- **Network Connectivity**: Test RDP access thoroughly
- **Claude Desktop Compatibility**: Verify application works in Windows Server environment

### Cost Risks
- **Higher Than Expected Costs**: Monitor usage and optimize after MVP
- **Continuous Running**: Emphasize on-demand usage patterns
- **Storage Costs**: Use standard GP3 storage for cost balance

### Timeline Risks
- **Windows Complexity**: Focus on "good enough" rather than perfect
- **Ansible Windows Learning Curve**: Use simple approaches initially
- **Testing Time**: Allocate sufficient time for end-to-end validation

## Future Optimization Backlog

### Cost Optimization (Priority 1)
- Reduce to t3.medium instance type
- Implement automated start/stop scheduling
- Optimize storage configuration
- Target $15/month usage cost

### Automation Improvements (Priority 2)
- Fully automated Claude Desktop installation
- Advanced Windows configuration
- Multiple application support
- Performance tuning

### Security Enhancements (Priority 3)
- Certificate-based authentication
- VPN-based access
- Advanced firewall configuration
- Audit logging

### Documentation & Usability (Priority 4)
- Comprehensive user guide
- Troubleshooting documentation
- Video tutorials
- Integration with existing documentation

## Daily Progress Tracking

### Day 1 Progress
- [ ] Windows provisioner created
- [ ] Security group configured
- [ ] Administrator account working
- [ ] RDP access established

### Day 2 Progress
- [ ] ansible.windows collection installed
- [ ] Windows inventory configured
- [ ] Basic Windows configuration complete
- [ ] Claude Desktop installed and working

### Day 3 Progress
- [ ] Main playbooks created
- [ ] End-to-end testing complete
- [ ] Basic documentation written
- [ ] MVP ready for production use

## Definition of Done

The Windows Server MVP is complete when:

1. **Functional**: User can run single command to get working Windows Server with Claude Desktop
2. **Reliable**: Process works consistently without manual intervention
3. **Usable**: Claude Desktop suitable for actual work projects
4. **Documented**: Basic usage instructions available
5. **Destroyable**: Complete cleanup works correctly
6. **Validated**: End-to-end testing confirms all requirements met

This MVP provides immediate business value while establishing the foundation for future optimization and enhancement.
