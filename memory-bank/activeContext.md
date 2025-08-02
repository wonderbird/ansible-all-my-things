# Active Context: Ansible All My Things

## Current Work Focus

### Robust Command Restriction System Implementation 🔴 URGENT
**Goal**: Implement bulletproof command restriction system that prevents AI agents from executing infrastructure commands on target systems.

**Status**: 🔴 IN PROGRESS - Critical security compliance issue requiring immediate resolution

**Business Context**: **SECURITY CRITICAL & ARCHITECTURAL SHIFT** - Current command restriction mechanism is fundamentally broken with Claude Code's architecture, creating security risks and compliance violations. **MAJOR DISCOVERY**: AI agents run on target systems provisioned by this very ansible project, requiring distributed deployment approach.

**Self-Provisioning Context**: AI agents operate on target systems (`hobbiton`, `rivendell`, `moria`) under `desktop_users` accounts (`galadriel`, `legolas`) created by this ansible project, fundamentally changing implementation requirements from local to distributed Infrastructure-as-Code security deployment.

**Timeline**: **URGENT** - 2-3 days maximum delivery requirement

**Core Problem**: Claude Code creates independent shell sessions for each command execution, causing bash function-based restrictions to be lost across tool calls, making current `.clinerules/only-user-can-run-ansible-commands.md` ineffective.

**Business Impact**:
- **Security Risk**: Accidental execution of infrastructure commands could provision expensive resources or destroy existing infrastructure
- **Compliance Violation**: Project rules are technically unenforceable with current implementation
- **Workflow Disruption**: Unreliable restrictions force manual oversight and slow development

**MVP Deliverables (Distributed Deployment)**:
1. **Sub-Shell Resistant Command Blocking**: Mechanism that works when Claude creates new bash sub-shells **on target systems**
2. **Comprehensive Command Coverage**: Block all infrastructure commands (`ansible`, `ansible-playbook`, `ansible-vault`, `ansible-inventory`, `ansible-galaxy`, `ansible-config`, `vagrant`, `docker`, `tart`, `aws`, `hcloud`) **on target systems**
3. **Ansible-Integrated Deployment**: Deploy restrictions via ansible playbooks to `desktop_users` on target systems (`hobbiton`, `rivendell`, `moria`)
4. **Cross-Platform Support**: Work on AWS Linux, AWS Windows, and Hetzner Cloud target systems
5. **Remote Verification System**: Verify restriction status on target systems from control machine via ansible

**Success Criteria (Distributed)**:
- ✅ **Persistent Blocking**: Commands remain blocked across multiple separate Claude tool calls **on target systems**
- ✅ **Cross-Platform Deployment**: Works on AWS Linux, AWS Windows, and Hetzner Cloud systems
- ✅ **Ansible Integration**: Deployed automatically during infrastructure provisioning
- ✅ **Target User Coverage**: Applied to all `desktop_users` (galadriel, legolas) on target systems
- ✅ **Reboot Persistence**: Restrictions survive system reboots and updates
- ✅ **Remote Verification**: Status checkable from control machine via ansible

**Implementation Options Under Consideration**:
**Legacy Local Approaches** (Pre-Self-Provisioning Discovery):
- **Approach A-E**: Project-local and global approaches for control machine deployment

**New Distributed Deployment Approaches** (Post-Discovery):
- **Approach F**: Ansible-Deployed User Profile Integration (bashrc/PowerShell profiles on target systems)
- **Approach G**: Ansible-Deployed System-Wide Wrappers (global wrappers deployed to target systems)
- **Approach H**: Ansible-Deployed Service-Based Blocking (systemd/Windows services on target systems)

## Current System State

### Infrastructure Status
Production-ready cross-provider infrastructure automation with:
- **Hetzner Cloud Linux**: `hobbiton` - Complete development environment
- **AWS Linux**: `rivendell` - On-demand development server  
- **AWS Windows**: `moria` - Windows application server with Claude Desktop access

### Technical Foundation
- Unified inventory system with proper group_vars structure
- Idiomatic Ansible configuration with automated vault password handling
- Cross-provider SSH key management and credential patterns
