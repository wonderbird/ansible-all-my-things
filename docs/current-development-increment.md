# Current Development Increment: Command Restriction System

## Product Owner Decision: MVP Increment Definition

**Business Goal**: Deploy command restriction system to target systems that prevents AI agents from executing infrastructure commands.

**Business Driver**: Infrastructure automation projects require AI agent safety controls to prevent accidental resource provisioning or destruction on target systems.

**Timeline**: URGENT - Delivery within 2-3 days maximum

## Problem Analysis

### Target System Deployment Context
**Infrastructure-as-Code Security**: Command restrictions must be deployed to target systems where AI agents operate.

**Target System Architecture**:
- **AI Agent Runtime Environment**: AI agents run on provisioned systems (`hobbiton`, `rivendell`, `moria`)
- **Target User Accounts**: AI agents operate under `desktop_users` accounts (`galadriel`, `legolas`) created by ansible
- **Cross-Platform Deployment**: Restrictions must work on AWS Linux, AWS Windows, and Hetzner Cloud systems
- **Infrastructure-as-Code**: Command restrictions deployed via ansible playbooks during provisioning

### Technical Challenge
**Core Problem**: Claude Code creates independent shell sessions for each command execution, requiring sub-shell resistant command blocking on target systems.

**Business Impact**:
- **Security Risk**: Prevent accidental execution of infrastructure commands on target systems
- **Compliance Requirement**: Enforce project safety rules via ansible deployment
- **Workflow Protection**: Enable safe AI agent operation during development

## MVP Scope & Requirements

### Core Problem to Solve
Deploy restrictions via ansible that work reliably across Claude Code's independent shell sessions on target systems. Need solution that:
1. Works across sub-shell scenarios on target systems
2. Is deployed via ansible Infrastructure-as-Code
3. Works cross-platform (Linux and Windows target systems)
4. Integrates with existing user provisioning workflows

### MVP Deliverables

#### 1. Sub-Shell Resistant Command Blocking
- Mechanism that works when Claude creates new bash sub-shells on target systems
- Block commands at shell level across Linux and Windows platforms
- Deployed via ansible to `desktop_users` on target systems

#### 2. Comprehensive Command Coverage
**Blocked Commands**:
- `ansible` (all variants: ansible-playbook, ansible-vault, ansible-inventory, ansible-galaxy, ansible-config)
- `vagrant`
- `docker`
- `tart`
- `aws`
- `hcloud`

**Blocking Strategy**: Block base commands completely (no parameter filtering)

#### 3. AI Agent Verification System
- Remote verification capability via ansible tasks from control machine
- Cross-platform status checking (Linux and Windows target systems)
- Clear feedback mechanism showing which commands are blocked

#### 4. Ansible-Integrated Deployment
- Deploy restrictions via ansible playbooks during infrastructure provisioning
- Integrate with existing `playbooks/setup-users.yml` workflow
- Cross-platform deployment (Linux and Windows target systems)
- Remote management and updates via ansible automation

### Success Criteria

**Primary Success Metrics**:
1. ✅ **Persistent Blocking**: Commands remain blocked across multiple Claude tool calls on target systems
2. ✅ **Cross-Platform Support**: Works on AWS Linux, AWS Windows, and Hetzner Cloud target systems
3. ✅ **Ansible Integration**: Deployed automatically during infrastructure provisioning
4. ✅ **Remote Verification**: Status checkable from control machine via ansible
5. ✅ **User Override**: Restrictions apply only to AI agents, not human users

**Acceptance Test on Target Systems**:
```bash
# Test blocking in sub-shell (should fail on target systems)
bash -c "ansible --version"
bash -c "vagrant status"
bash -c "docker ps"

# Verify legitimate commands still work
bash -c "ls -la"
bash -c "git status"
```

## Implementation Strategy

### Four Implementation Approaches

#### 1. User Profile Integration
**Concept**: Deploy restriction scripts to desktop_users' profiles on target systems
- Deploy restriction scripts to desktop_users' `.bashrc`/`.profile` on Linux target systems
- Windows: Deploy to PowerShell profiles for desktop_users on Windows target systems
- Use ansible templates to customize restrictions per user/platform
- Include in existing `playbooks/setup-users.yml` workflow

**Pros**: User-specific, cross-platform, ansible-integrated, persistent across reboots
**Cons**: Profile loading dependency, per-user deployment complexity

#### 2. System-Wide Wrappers
**Concept**: Deploy global wrapper scripts to target systems via ansible
- Deploy wrapper scripts to `/usr/local/bin/` (Linux) or `C:\Windows\System32\` (Windows) via ansible
- Modify system PATH during user provisioning to prioritize wrappers
- Cross-platform ansible tasks for Linux and Windows deployment
- Include verification tasks in ansible playbooks

**Pros**: System-wide on target systems, ansible-deployable, cross-platform, bulletproof
**Cons**: System-wide impact on target systems, requires elevated privileges during deployment

#### 3. Service-Based Blocking
**Concept**: Deploy services that monitor and block commands on target systems
- Deploy systemd services (Linux) or Windows services that monitor and block commands
- Service-based approach survives all session types and reboots
- Cross-platform ansible deployment with platform-specific implementations
- Remote monitoring and control capabilities via ansible

**Pros**: Ultimate persistence, service-level blocking, remotely manageable
**Cons**: Complex implementation, service overhead, platform-specific development

#### 4. fapolicyd Integration (Linux-Only Alternative)
**Concept**: Use Red Hat's File Access Policy Daemon for application allowlisting on Linux target systems
- Deploy fapolicyd rules via ansible to block infrastructure commands on Linux target systems
- Configure user/group-based policies to allow commands for human users but block for AI agent accounts
- Leverage RPM trust database for application allowlisting
- Integration with systemd for service-level persistence

**Rule Examples**:
```bash
# Block ansible for specific user accounts
deny_audit perm=execute uid=galadriel : path=/usr/bin/ansible
deny_audit perm=execute uid=legolas : path=/usr/bin/ansible

# Allow for admin users
allow perm=execute gid=wheel : path=/usr/bin/ansible
```

**Pros**: 
- System-level enforcement, very difficult to bypass
- Integration with Red Hat ecosystem and RHEL system roles
- Comprehensive application allowlisting capabilities
- Performance optimizations and kernel-level integration

**Cons**: 
- **Linux-only solution** (doesn't address Windows target `moria`)
- System-wide impact and complexity
- Performance overhead from monitoring all file access
- Overkill for simple command blocking requirements
- Risk of blocking legitimate system operations

**Key Resources**:
- [Red Hat fapolicyd Documentation](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/security_hardening/assembly_blocking-and-allowing-applications-using-fapolicyd_security-hardening)
- [fapolicyd GitHub Repository](https://github.com/linux-application-whitelisting/fapolicyd)
- [Automating fapolicyd with RHEL System Roles](https://www.redhat.com/en/blog/automating-fapolicyd-rhel-system-roles)
- [fapolicyd Ansible Configuration](https://access.redhat.com/solutions/6997136) (Red Hat Subscription Required)

### Implementation Decision
**Solution Selection Required**: Choose implementation approach based on:
- Technical feasibility with Claude Code's architecture
- Maintenance complexity and long-term sustainability
- Security robustness and bypass resistance
- Cross-platform compatibility requirements

**Implementation Timeline**: 2-3 days maximum for chosen solution

## Requirements Compliance

### Functional Requirements
1. **Robust Implementation**: Restrictions work reliably across Claude's session architecture on target systems ✅
2. **Command Coverage**: All specified commands blocked on target systems ✅
3. **Persistence**: Restrictions survive across multiple Claude tool calls on target systems ✅
4. **Cross-Platform Support**: Works on AWS Linux, AWS Windows, and Hetzner Cloud target systems ✅
5. **Ansible Integration**: Deployed automatically during infrastructure provisioning ✅
6. **Remote Management**: Manageable and verifiable from control machine via ansible ✅

### Non-Functional Requirements
1. **Simplicity**: Solution easy to understand and maintain ✅
2. **Robustness**: Difficult to bypass accidentally or through normal usage ✅
3. **Non-Intrusive**: No interference with normal user command execution ✅
4. **Reversible**: Easy to disable when needed ✅

## Success Definition
**MVP Complete When**: AI agents operating on target systems (`hobbiton`, `rivendell`, `moria`) under `desktop_users` accounts cannot execute infrastructure commands, restrictions are deployed via ansible during infrastructure provisioning, work cross-platform, and can be verified remotely from control machine.

**Future Enhancements**: Detailed logging, parameter-based filtering, automated testing, additional command categories.

---
**Product Owner**: Stefan  
**Timeline**: 2-3 days maximum  
**Priority**: Critical implementation priority for AI agent safety