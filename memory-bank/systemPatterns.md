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

### Command Restriction System Requirements
**Core Challenge**: Claude Code creates independent shell sessions for each command execution, bypassing traditional bash function-based restrictions.

**Current Broken State**:
- **Command Restriction System**: ⚠️ BROKEN - Current bash function approach fails with Claude Code's shell session isolation
- **Security Compliance**: ⚠️ VIOLATED - `.clinerules/only-user-can-run-ansible-commands.md` technically unenforceable
- **Sub-Shell Resistance**: ⚠️ MISSING - Need mechanism that persists across independent bash sessions
- **Verification System**: ⚠️ UNRELIABLE - Status checking doesn't work across Claude tool calls

**Required Architecture Patterns**:
```
AI Agent Safety System:
├── Sub-Shell Resistant Blocking:
│   ├── Option A: Wrapper Scripts with PATH manipulation
│   ├── Option B: Environment Detection with persistent markers
│   ├── Option C: direnv Integration with automatic loading
│   └── Option D: Shell Initialization with BASH_ENV/project .bashrc
├── Comprehensive Command Coverage:
│   ├── Infrastructure: ansible*, vagrant, docker, tart
│   ├── Cloud Providers: aws, hcloud
│   └── Project-Scoped: Only within ansible-all-my-things directory
└── Verification & Status:
    ├── Cross-Session Status Checking
    ├── Clear Error Messages
    └── User Override Capability
```

**Implementation Success Criteria**:
- **Persistent Blocking**: Commands blocked across separate Claude tool calls
- **Status Verification**: Reliable `--status` command across sessions
- **Project Scope**: Restrictions only apply in project directory
- **User Override**: Normal user command execution unaffected

**Technical Constraints**:
- Must work with Claude Code's independent bash session architecture
- No modification of Claude Code tool behavior allowed
- Must be maintainable and easily debuggable
- Should not impact normal development workflow

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
- **Project Scoping**: Restrictions confined to specific project directory

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