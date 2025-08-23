# Active Context: Ansible All My Things

## Current Work Focus

### AppArmor Implementation Spike 🟡 READY TO START
**Goal**: Validate AppArmor kernel-level command restrictions on target systems via manual configuration spike.

**Status**: 🟡 IMPLEMENTATION READY - AppArmor learning completed, comprehensive profile approach defined

**Business Context**: Infrastructure automation projects require AI agent safety controls to prevent accidental resource provisioning or destruction on target systems.

**Target System Deployment**: AI agents operate on target systems (`hobbiton`, `rivendell`, `moria`) under `desktop_users` accounts (`galadriel`, `legolas`), requiring ansible-deployed command restrictions.

**Timeline**: **URGENT** - 2-3 days maximum delivery requirement

**Core Challenge**: Deploy restrictions via ansible that work reliably across Claude Code's independent shell sessions on target systems.

**Business Impact**:
- **Security Risk**: Prevent accidental execution of infrastructure commands on target systems
- **Compliance Requirement**: Enforce project rules via ansible deployment
- **Workflow Protection**: Enable safe AI agent operation during development

**MVP Deliverables**:
1. **Sub-Shell Resistant Command Blocking**: Mechanism that works across Claude's bash sessions on target systems
2. **Comprehensive Command Coverage**: Block infrastructure commands (`ansible`, `vagrant`, `docker`, `aws`, `hcloud`) on target systems
3. **Ansible-Integrated Deployment**: Deploy restrictions via ansible playbooks to `desktop_users` on target systems
4. **Cross-Platform Support**: Work on AWS Linux, AWS Windows, and Hetzner Cloud target systems
5. **Remote Verification System**: Verify restriction status on target systems from control machine via ansible

**Success Criteria**:
- ✅ **Persistent Blocking**: Commands remain blocked across multiple Claude tool calls on target systems
- ✅ **Cross-Platform Deployment**: Works on AWS Linux, AWS Windows, and Hetzner Cloud systems
- ✅ **Ansible Integration**: Deployed automatically during infrastructure provisioning
- ✅ **Target User Coverage**: Applied to all `desktop_users` (galadriel, legolas) on target systems
- ✅ **Reboot Persistence**: Restrictions survive system reboots and updates
- ✅ **Remote Verification**: Status checkable from control machine via ansible

**Selected Implementation**: **AppArmor Integration**
- **Decision Rationale**: Kernel-level enforcement provides maximum effectiveness (1.2 average score, tied with Claude CLI Native)
- **Tiebreaker**: Superior effectiveness on second-highest priority criterion
- **Implementation Scope**: Linux systems (`hobbiton`, `rivendell`) with Windows (`moria`) deferred
- **Fallback Strategy**: Claude CLI Native Restrictions via `.claude/settings.json` deployment if AppArmor spike fails

**Implementation Specifications**:
- **AppArmor Profile**: Single comprehensive profile at `/etc/apparmor.d/ai-agent-block` blocking all infrastructure commands
- **Profile Approach**: Block multiple executables (`deny /usr/bin/ansible* x,`, `deny /usr/local/bin/vagrant x,` etc.) in one profile
- **User Targeting**: Configure `/etc/security/pam_apparmor.conf` for `galadriel` and `legolas` accounts
- **Ansible Integration**: Extend `playbooks/setup-users.yml` with AppArmor tasks
- **Remote Verification**: Use `aa-status` command through ansible tasks
- **Acceptance Tests**: `bash -c "ansible --version"` must fail, `bash -c "ls -la"` must succeed
- **Security Constraint**: AI agents MUST NOT execute `sudo` - enforced by excluding desktop_users from sudoers group

## Current System State

### Infrastructure Status
Production-ready cross-provider infrastructure automation:
- **Hetzner Cloud Linux**: `hobbiton` - Complete development environment
- **AWS Linux**: `rivendell` - On-demand development server  
- **AWS Windows**: `moria` - Windows application server with Claude Desktop access

### Technical Foundation
- Unified inventory system with proper group_vars structure
- Idiomatic Ansible configuration with automated vault password handling
- Cross-provider SSH key management and credential patterns
- Target systems ready for command restriction deployment
- **Documentation streamlined**: Removed discovery narrative, consolidated approaches

## Recent Changes

### AppArmor Learning Completed ✅
- **Stand-Alone Profiling mastered**: Hands-on experience with `aa-genprof` and `aa-logprof` tools
- **Profile structure understanding**: Learned abstractions, deny rules, and enforcement modes
- **Security decision-making**: Practiced allow/deny choices for file access and capabilities
- **Comprehensive profile approach**: Identified single profile blocking multiple commands as optimal strategy
- **Sub-shell testing validated**: Confirmed AppArmor works across Claude Code's independent bash sessions

### Documentation Streamlining Completed
- **Memory bank restructured**: Removed "broken state" and "discovery" language throughout all files
- **Implementation approaches consolidated**: From 8 scattered options to 6 clear approaches
- **Forward-looking documentation**: Written as if target system deployment was always the known approach

### Infrastructure Improvements
- Enhanced inventory system with provider-specific targeting
- Complete transition to idiomatic ansible configuration
- Unified command patterns across multiple cloud providers

### Next Immediate Actions
**Sprint Ready Implementation Steps**:

**Story 1: Fresh rivendell Provisioning** (0.5 day)
- Deploy clean AWS Linux instance using existing `provision-aws-linux.yml`
- Verify SSH access and basic system setup

**Story 2: Manual AppArmor Spike** (1-2 days)  
- Install AppArmor on rivendell target system
- Create comprehensive `/etc/apparmor.d/ai-agent-block` profile blocking all infrastructure commands
- Configure `/etc/security/pam_apparmor.conf` for user-specific targeting
- Execute acceptance tests: `bash -c "ansible --version"` fails, `bash -c "ls -la"` succeeds
- Document spike results and decision for ansible automation vs fallback

**Story 3: Ansible Automation** (1 day)
- Create AppArmor deployment tasks in `playbooks/setup-users.yml` 
- Add remote verification via `aa-status` command
- Test idempotent deployment across multiple runs
