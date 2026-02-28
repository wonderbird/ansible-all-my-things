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

### Command Restriction Implementation

**Architecture Decision**: AppArmor Integration selected for kernel-level command blocking on Linux target systems. See [ADR-001: Command Restriction Mechanism](../docs/architecture/decisions/001-command-restrictions.md) for complete decision rationale.

**Implementation Architecture Patterns**:

**Target System Deployment Pattern**:
- **AI Agent Runtime Environment**: AI agents run on provisioned systems (`hobbiton`, `rivendell`, `moria`)
- **Target User Accounts**: AI agents operate under `desktop_users` accounts (`galadriel`, `legolas`) created by ansible
- **Cross-Platform Deployment**: Restrictions work on AWS Linux, AWS Windows, and Hetzner Cloud systems
- **Infrastructure-as-Code**: Command restrictions deployed via ansible playbooks during provisioning

**AppArmor Integration Pattern** ✅ SELECTED:
- **Profile Deployment**: Single comprehensive profile at `/etc/apparmor.d/ai-agent-block` blocking all infrastructure commands
- **User-Specific Targeting**: Configure `/etc/security/pam_apparmor.conf` for `galadriel` and `legolas` accounts only
- **Ansible Workflow Integration**: Extend existing `playbooks/setup-users.yml` with AppArmor tasks
- **Remote Verification Pattern**: Use `aa-status` command through ansible tasks for monitoring
- **Kernel-Level Security**: Mandatory Access Control that persists across reboots and system updates

**Claude CLI Native Fallback Pattern** ✅ FALLBACK:
- **Settings Deployment**: Deploy `.claude/settings.json` files to desktop_users' home directories
- **Cross-Platform Support**: Works on both Linux and Windows target systems via Claude's architecture
- **Simple Deployment**: File-based ansible template deployment with immediate effectiveness
- **User-Level Restrictions**: JSON configuration with `"permissions": {"deny": ["Bash(ansible:*)", ...]}` format

**Implementation Integration Points**:
- **Selected**: AppArmor Integration (Ubuntu kernel-level MAC) for `hobbiton` and `rivendell`
- **Fallback**: Claude CLI Native (.claude/settings.json) if AppArmor spike fails
- **Blocked Commands**: `ansible`, `vagrant`, `docker`, `aws`, `hcloud` and variants
- **Target Users**: `galadriel` and `legolas` accounts on target systems
- **Ansible Integration**: Deploy via `playbooks/setup-users.yml` during provisioning
- **Remote Verification**: Status checkable via `aa-status` command (AppArmor) or file existence (Claude CLI)

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

## Security Constraints

### sudo Prohibition for AI Agents
**Critical Constraint**: AI agents MUST NOT execute commands as root via `sudo`.

**Implementation**: Desktop_users accounts (`galadriel`, `legolas`) excluded from sudoers group during provisioning.

**Rationale**: Ensures reproducibility via Infrastructure as Code by limiting AI agents to source-controlled files only.

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