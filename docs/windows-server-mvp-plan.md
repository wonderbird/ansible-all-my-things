# Windows Server MVP Development Plan

## Executive Summary

**Objective**: Deliver minimal viable Windows Server with Claude Desktop access in 2-3 days for urgent work needs.

**Business Value**: Immediate access to Claude Desktop Application for current work projects.

**Approach**: Extend existing AWS Linux automation to Windows Server with focus on "working" over "optimized".

**Cost Acceptance**: ~$60/month initially acceptable, optimize later.

## Product Increment Definition

### What We're Building
- Windows Server 2025 with Desktop Experience on AWS EC2
- SSH and RDP access for command-line and desktop environment interaction
- Claude Desktop Application installed and functional
- Complete provision → access → destroy lifecycle
- Integration with existing Ansible automation patterns

### What We're NOT Building (MVP Scope)
- Cost optimization (accept higher costs initially)
- Fully automated Claude Desktop installation (manual PowerShell acceptable)
- Advanced security configurations beyond basic SSH and RDP access
- Performance tuning and optimization
- Comprehensive documentation (basic usage guide only)

## Development Timeline

### Day 1: Windows Server Provisioning (4-6 hours)
**Goal**: Get Windows Server instance running with RDP access

#### Morning (2-3 hours)
1. **Create Windows Provisioner** (`provisioners/aws-windows.yml`)
   - Copy existing `provisioners/aws-ec2.yml`
   - Modify for Windows Server 2025 AMI with Desktop Experience
   - Configure t3.large instance type (4 vCPU, 8GB RAM)
   - Set up Windows-specific security group

2. **Configure Security Group**
   - SSH access (port 22) from user's IP only
   - RDP access (port 3389) from user's IP only
   - WinRM access (ports 5985/5986) for Ansible compatibility
   - Outbound internet access for downloads

#### Afternoon (2-3 hours)
3. **Administrator Account Setup**
   - Configure Administrator password via user data script
   - Enable RDP for Administrator account
   - Test RDP connection from local machine

**Day 1 Success Criteria**:
- [ ] Windows Server instance provisions successfully
- [ ] SSH and RDP connections work from user's machine
- [ ] Desktop environment accessible and functional

### Day 2: Windows Configuration & Claude Desktop (6-8 hours)
**Goal**: Configure Windows for automation and install Claude Desktop

#### Morning (3-4 hours)
1. **Install ansible.windows Collection**
   - Run: `ansible-galaxy collection install ansible.windows`
   - Verify Windows modules available

2. **Extend AWS Inventory for Windows**
   - Update `inventories/aws/aws_ec2.yml`
   - Configure SSH and WinRM connection settings
   - Test Ansible connectivity to Windows instance via SSH

3. **Basic Windows Configuration Playbook**
   - Create `playbooks/setup-windows-basics.yml`
   - Configure Windows Firewall for SSH and RDP
   - Enable necessary Windows features
   - Basic system configuration for desktop use

#### Afternoon (3-4 hours)
4. **Claude Desktop Installation**
   - Research Claude Desktop download URL and installation method
   - Create PowerShell script for installation
   - Test installation and application launch
   - Verify Claude Desktop functionality

**Day 2 Success Criteria**:
- [ ] Ansible can connect to Windows instance via SSH
- [ ] Windows configured for reliable SSH and RDP access
- [ ] Claude Desktop installed and launches successfully
- [ ] Application functional for basic work tasks

### Day 3: Integration & Testing (4-6 hours)
**Goal**: Complete integration and validate end-to-end workflow

#### Morning (2-3 hours)
1. **Create Main Playbooks**
   - `provision-aws-windows.yml` (complete provisioning workflow)
   - `destroy-aws-windows.yml` (complete cleanup workflow)
   - Follow existing Linux playbook patterns
   - Include Windows-specific provisioning and configuration

2. **Integration Testing**
   - Test complete provision workflow
   - Verify all components work together
   - Test destroy workflow and resource cleanup

#### Afternoon (2-3 hours)
3. **End-to-End Validation**
   - Complete provision → RDP → Claude Desktop → work tasks → destroy cycle
   - Validate Claude Desktop suitable for actual work
   - Test multiple provision/destroy cycles for reliability

4. **Basic Documentation**
   - Create `docs/windows-server-mvp-usage.md`
   - Quick start guide and RDP connection instructions
   - Basic troubleshooting and cost management notes

**Day 3 Success Criteria**:
- [ ] Single command provisions complete Windows environment
- [ ] Claude Desktop accessible and functional for real work
- [ ] Single command destroys all resources completely
- [ ] Basic usage documentation available

## Technical Specifications

### AWS Configuration
- **Region**: eu-north-1 (carbon footprint and latency optimization)
- **AMI**: Windows Server 2025 with Desktop Experience (latest)
- **Instance Type**: t3.large (4 vCPU, 8GB RAM)
- **Storage**: 50GB GP3 EBS
- **Security Group**: Custom with SSH (22), RDP (3389) and WinRM (5985/5986)

### Authentication & Access
- **Method**: Administrator password (stored in Ansible Vault)
- **RDP Client**: Standard Windows RDP client or equivalent
- **Ansible Connection**: SSH preferred, WinRM available for compatibility

### Cost Estimates
- **Instance Cost**: ~$60/month if running continuously
- **Storage Cost**: ~$4/month
- **Total Maximum**: ~$64/month
- **Actual Usage**: On-demand for work sessions (much lower)

## Success Metrics

### Functional Requirements
- Windows Server provisions in ≤20 minutes
- SSH and RDP connections establish reliably
- Claude Desktop launches and functions normally
- Can perform actual work tasks via RDP
- Complete environment destroys in ≤5 minutes

### Business Requirements
- Immediate access to Claude Desktop for work projects
- Cost acceptable for urgent delivery
- Foundation established for future optimization
- User can work productively via RDP

## Risk Mitigation

### Technical Risks & Mitigation
- **Windows AMI Compatibility**: Use latest Windows Server 2025 with Desktop Experience
- **SSH/RDP Performance**: Use t3.large for adequate performance, test thoroughly
- **Ansible Windows Learning Curve**: Start with simple approaches, iterate
- **Claude Desktop Compatibility**: Test in Windows Server environment early

### Timeline Risks & Mitigation
- **Windows Complexity**: Focus on "good enough" rather than perfect
- **Unknown Issues**: Allocate buffer time for troubleshooting
- **Testing Requirements**: Plan sufficient time for end-to-end validation

## Future Optimization Roadmap

### Phase 1: Cost Optimization (After MVP)
- Reduce to t3.medium instance type
- Implement automated start/stop scheduling
- Optimize storage and network configuration
- Target $15/month usage cost

### Phase 2: Automation Enhancement
- Fully automated Claude Desktop installation
- Advanced Windows configuration
- Multiple application support
- Performance and security tuning

### Phase 3: Production Readiness
- Comprehensive documentation
- Advanced security configurations
- Monitoring and logging
- Integration with broader automation ecosystem

## Implementation Commands

### Initial Setup
```bash
# Install Windows Ansible collection
ansible-galaxy collection install ansible.windows

# Create Windows provisioner (copy and modify existing)
cp provisioners/aws-ec2.yml provisioners/aws-windows.yml
```

### Daily Workflow (After MVP)
```bash
# Provision Windows Server with Claude Desktop
ansible-playbook provision-aws-windows.yml

# Connect via RDP (instructions in documentation)
# Use Claude Desktop for work

# Destroy environment when done
ansible-playbook destroy-aws-windows.yml
```

## Definition of Done

The Windows Server MVP is complete when:

1. **Single Command Provisioning**: `ansible-playbook provision-aws-windows.yml` creates working environment
2. **RDP Access**: Reliable connection to Windows desktop environment
3. **Claude Desktop Functional**: Application works for actual work tasks
4. **Single Command Cleanup**: `ansible-playbook destroy-aws-windows.yml` removes all resources
5. **Basic Documentation**: Usage instructions available
6. **End-to-End Tested**: Complete workflow validated multiple times

This plan provides immediate business value while establishing the foundation for future optimization and cost reduction.
