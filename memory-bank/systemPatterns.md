# System Patterns: Ansible All My Things

## Architecture Overview

### Multi-Provider Infrastructure System ✅ OPERATIONAL
Production-ready cross-provider infrastructure automation with unified management patterns:
- **Hetzner Cloud Linux**: Complete development environment
- **AWS Linux**: On-demand development server  
- **AWS Windows**: Windows application server

**Key Patterns**:
- **Dynamic Inventory**: Multi-provider automatic host discovery
- **Platform Grouping**: Consistent linux/windows grouping across providers
- **SSH Key Management**: Single SSH key pair working across all implementations
- **Idiomatic Secret Management**: Vault-encrypted variables with automated access
- **Unified Command Interface**: Similar command patterns across different underlying technologies

## AI Agent Safety Architecture ⚠️ CRITICAL IMPLEMENTATION REQUIRED

### Self-Provisioning Context ⚠️ ARCHITECTURAL GAME-CHANGER
**Infrastructure-as-Code Security**: This ansible-all-my-things project provisions the very target systems where AI agents operate, fundamentally changing the implementation approach.

**Target System Deployment**:
- **AI Agent Runtime Environment**: AI agents run on provisioned systems (`hobbiton`, `rivendell`, `moria`)
- **Target User Accounts**: AI agents operate under `desktop_users` accounts (`galadriel`, `legolas`) created by ansible
- **Cross-Platform Deployment**: Restrictions must work on AWS Linux, AWS Windows, and Hetzner Cloud systems
- **Infrastructure-as-Code**: Command restrictions must be deployed via ansible playbooks, not manually configured

**Design Implications**:
- Restrictions must be **baked into the provisioned systems** during infrastructure deployment
- Cannot rely on project-local solutions since "project" exists on control machine, AI agents run on target machines
- Must work across **multiple target systems** with different operating systems
- Must integrate with existing **user provisioning playbooks** (`playbooks/setup-users.yml`)
- Must **persist through system reboots** and infrastructure updates

### Command Restriction System Requirements
**Core Challenge**: Claude Code creates independent shell sessions for each command execution, bypassing traditional bash function-based restrictions.

**Enhanced Challenge - Distributed Deployment**: Restrictions must be deployed to multiple target systems via ansible automation and work reliably across different platforms.

**Current Broken State**:
- **Command Restriction System**: ⚠️ BROKEN - Current bash function approach fails with Claude Code's shell session isolation
- **Security Compliance**: ⚠️ VIOLATED - `.clinerules/only-user-can-run-ansible-commands.md` technically unenforceable
- **Sub-Shell Resistance**: ⚠️ MISSING - Need mechanism that persists across independent bash sessions
- **Verification System**: ⚠️ UNRELIABLE - Status checking doesn't work across Claude tool calls

**Required Architecture Patterns (Distributed Deployment)**:
```
Infrastructure-as-Code AI Agent Safety System:
├── Ansible-Deployed Restrictions:
│   ├── User Account Integration: Deploy to desktop_users (galadriel, legolas)
│   ├── Cross-Platform Support: Linux and Windows target systems  
│   ├── Persistent Installation: Survive reboots and system updates
│   └── Playbook Integration: Extend existing setup-users.yml
├── Sub-Shell Resistant Blocking:
│   ├── Option A: Global System Wrappers (deployed via ansible)
│   ├── Option B: User Profile Integration (bashrc/profile.ps1 deployment)
│   ├── Option C: System-Wide PATH Manipulation (ansible-managed)
│   └── Option D: Service-Based Blocking (systemd/Windows services)
├── Comprehensive Command Coverage:
│   ├── Infrastructure: ansible*, vagrant, docker, tart
│   ├── Cloud Providers: aws, hcloud
│   └── Target System Scope: Apply to all desktop_users on target systems
└── Cross-System Verification:
    ├── Ansible-Verifiable Status: Check restrictions via ansible tasks
    ├── Platform-Specific Implementation: Linux vs Windows approaches
    └── Remote Status Checking: Verify from control machine
```

**Implementation Success Criteria (Distributed)**:
- **Persistent Blocking**: Commands blocked across separate Claude tool calls on target systems
- **Cross-Platform Deployment**: Works on AWS Linux, AWS Windows, and Hetzner Cloud systems
- **Ansible Integration**: Deployed automatically during infrastructure provisioning
- **User Account Targeting**: Applied to all desktop_users (galadriel, legolas) on target systems
- **Reboot Persistence**: Restrictions survive system reboots and updates
- **Remote Verification**: Status checkable from control machine via ansible

**Technical Constraints (Enhanced)**:
- Must work with Claude Code's independent bash session architecture **on target systems**
- Must be deployable via ansible playbooks across multiple platforms
- Must integrate with existing user provisioning workflows
- Must work on both Linux and Windows target systems
- No modification of Claude Code tool behavior allowed
- Must be maintainable and easily debuggable across distributed infrastructure
- Should not impact normal user workflows on target systems

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
- **Security by Design**: Encrypted credentials and restricted access patterns
- **Cost Optimization**: On-demand provisioning with complete resource cleanup

### AI Agent Safety (Critical Implementation Required)
- **Fail-Safe Defaults**: Commands blocked by default, must explicitly allow
- **Defense in Depth**: Multiple layers of protection against accidental execution
- **Clear Verification**: Easy status checking for AI agents across sessions
- **User Autonomy**: Restrictions apply only to AI agents, not human users
- **Robust Architecture**: Restrictions that work reliably across Claude's session model

## Extension Points

### Current System Capabilities
- **Multi-Provider Support**: Framework ready for additional cloud providers
- **Platform Extension**: Patterns established for Linux and Windows platforms
- **Testing Framework**: Unified testing approach across different environments
- **Application Deployment**: Ready for additional application installations

### Command Restriction Implementation (Pending)
Once implemented, the command restriction system will provide:
- **Bulletproof AI Agent Safety**: Sub-shell resistant command blocking
- **Compliance Enforcement**: Technical enforcement of project safety rules
- **Development Workflow Protection**: Prevention of accidental infrastructure changes
- **Scalable Security Model**: Extensible to additional projects and command categories