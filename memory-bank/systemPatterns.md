# System Patterns: Ansible All My Things

## Architecture Overview

### Multi-Provider Infrastructure System ✅ OPERATIONAL
Production-ready cross-provider infrastructure automation with unified management patterns:
- **Hetzner Cloud Linux**: Complete development environment (`hobbiton`)
- **AWS Linux**: On-demand development server (`rivendell`)
- **AWS Windows**: Windows application server (`moria`)

**Key Patterns**:
- **Dynamic Inventory**: Multi-provider automatic host discovery
- **Platform Grouping**: Consistent linux/windows grouping across providers
- **SSH Key Management**: Single SSH key pair working across all implementations
- **Idiomatic Secret Management**: Vault-encrypted variables with automated access
- **Unified Command Interface**: Similar command patterns across different underlying technologies

## AI Agent Safety Architecture

### Target System Deployment
**Infrastructure-as-Code Security**: Command restrictions deployed to target systems where AI agents operate.

**Target System Architecture**:
- **AI Agent Runtime Environment**: AI agents run on provisioned systems (`hobbiton`, `rivendell`, `moria`)
- **Target User Accounts**: AI agents operate under `desktop_users` accounts (`galadriel`, `legolas`) created by ansible
- **Cross-Platform Deployment**: Restrictions work on AWS Linux, AWS Windows, and Hetzner Cloud systems
- **Infrastructure-as-Code**: Command restrictions deployed via ansible playbooks during provisioning

**Design Principles**:
- Restrictions **deployed to target systems** during infrastructure provisioning
- Integrated with existing **user provisioning playbooks** (`playbooks/setup-users.yml`)
- Work across **multiple target systems** with different operating systems
- **Persist through system reboots** and infrastructure updates

### Command Restriction Implementation Approaches

**Core Challenge**: Deploy restrictions via ansible that work reliably across Claude Code's independent shell sessions on target systems.

**Four Implementation Approaches**:

#### 1. User Profile Integration
- Deploy restriction scripts to desktop_users' profiles on target systems
- Linux: `.bashrc`/`.profile` modification via ansible templates
- Windows: PowerShell profile deployment for desktop_users
- Ansible integration: Extend existing `playbooks/setup-users.yml`
- **Pros**: User-specific, cross-platform, ansible-integrated, persistent across reboots
- **Cons**: Profile loading dependency, per-user deployment complexity

#### 2. System-Wide Wrappers
- Deploy global wrapper scripts to target systems via ansible
- Linux: `/usr/local/bin/` deployment with PATH modification
- Windows: `C:\Windows\System32\` deployment via ansible
- Cross-platform ansible tasks for deployment and verification
- **Pros**: System-wide on target systems, ansible-deployable, bulletproof, remotely manageable
- **Cons**: System-wide impact on target systems, requires elevated privileges

#### 3. Service-Based Blocking
- Deploy systemd services (Linux) or Windows services via ansible
- Service-based approach survives all session types and reboots
- Cross-platform ansible deployment with platform-specific implementations
- Remote monitoring and control capabilities via ansible
- **Pros**: Ultimate persistence, service-level blocking, remotely manageable, survives all changes
- **Cons**: Complex implementation, service overhead, platform-specific development

#### 4. fapolicyd Integration (Linux-Only Alternative)
- Deploy Red Hat's File Access Policy Daemon for application allowlisting on Linux target systems
- Configure user/group-based policies via ansible to block infrastructure commands for AI agent accounts
- Leverage RPM trust database and systemd integration for comprehensive application control
- **Assessment**: Not recommended due to Linux-only limitation (doesn't address Windows target `moria`) and complexity mismatch for simple command blocking requirements

**Blocked Commands**: `ansible`, `ansible-playbook`, `ansible-vault`, `ansible-inventory`, `ansible-galaxy`, `ansible-config`, `vagrant`, `docker`, `tart`, `aws`, `hcloud`

**Implementation Success Criteria**:
- **Persistent Blocking**: Commands blocked across separate Claude tool calls on target systems
- **Cross-Platform Deployment**: Works on AWS Linux, AWS Windows, and Hetzner Cloud systems
- **Ansible Integration**: Deployed automatically during infrastructure provisioning
- **User Account Targeting**: Applied to all desktop_users on target systems
- **Reboot Persistence**: Restrictions survive system reboots and updates
- **Remote Verification**: Status checkable from control machine via ansible

## Inventory System Architecture ✅ IMPLEMENTED

**Current Structure**:
```
inventories/
├── aws_ec2.yml                # AWS dynamic inventory
├── hcloud.yml                 # Hetzner Cloud dynamic inventory
├── vagrant_docker.yml         # Vagrant Docker testing inventory
├── vagrant_tart.yml           # Vagrant Tart testing inventory
└── group_vars/                # Provider-aware variables with secrets
    ├── all/vars.yml           # Encrypted secrets
    └── [provider]/vars.yml    # Provider-specific configurations
```

**Key Design Patterns**:
- **Dual Group Structure**: Cross-provider (@linux, @windows) and provider-specific groups
- **Variable Precedence**: all → platform → provider → provider_platform hierarchy
- **Secret Management**: Encrypted vault variables with automated password handling
- **Testing Integration**: Unified variable management across production and test environments

## Design Principles

### Infrastructure Automation
- **Idempotent Operations**: Repeatable infrastructure provisioning without side effects
- **Provider Abstraction**: Common patterns across different cloud providers
- **Security by Design**: Encrypted credentials and AI agent safety controls
- **Cost Optimization**: On-demand provisioning with complete resource cleanup

### AI Agent Safety
- **Target System Deployment**: Restrictions deployed to target systems via ansible
- **Defense in Depth**: Multiple implementation approaches for robust protection
- **Clear Verification**: Remote status checking via ansible tasks
- **User Autonomy**: Restrictions apply only to AI agents, not human users
- **Cross-Platform**: Unified approach across Linux and Windows target systems

## Extension Points

### Current System Capabilities
- **Multi-Provider Support**: Framework ready for additional cloud providers
- **Platform Extension**: Patterns established for Linux and Windows platforms
- **Testing Framework**: Unified testing approach across different environments
- **Application Deployment**: Ready for additional application installations

### Command Restriction System
The command restriction system provides:
- **Bulletproof AI Agent Safety**: Sub-shell resistant command blocking on target systems
- **Compliance Enforcement**: Technical enforcement of project safety rules
- **Development Workflow Protection**: Prevention of accidental infrastructure changes
- **Scalable Security Model**: Extensible to additional projects and command categories