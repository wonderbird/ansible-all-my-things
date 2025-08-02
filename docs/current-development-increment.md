# Current Development Increment: Robust Command Restriction System

## Product Owner Decision: MVP Increment Definition

**Business Goal**: Implement robust command restriction system that prevents AI agents from executing infrastructure commands on target systems.

**Business Driver**: Current mechanism is fundamentally broken with Claude Code - AI agents ignore rules and execute forbidden commands, creating security risks and workflow problems. **CRITICAL DISCOVERY**: AI agents run on target systems provisioned by this ansible project, requiring distributed Infrastructure-as-Code security deployment.

**Timeline**: URGENT - Delivery within 2-3 days maximum

## Problem Analysis

### Self-Provisioning Context ⚠️ ARCHITECTURAL GAME-CHANGER
**Infrastructure-as-Code Security**: This ansible-all-my-things project provisions the very target systems where AI agents operate, fundamentally changing the implementation approach.

**Target System Deployment**:
- **AI Agent Runtime Environment**: AI agents run on provisioned systems (`hobbiton`, `rivendell`, `moria`)
- **Target User Accounts**: AI agents operate under `desktop_users` accounts (`galadriel`, `legolas`) created by ansible
- **Cross-Platform Deployment**: Restrictions must work on AWS Linux, AWS Windows, and Hetzner Cloud systems
- **Infrastructure-as-Code**: Command restrictions must be deployed via ansible playbooks, not manually configured

### Current Broken State
The existing command restriction system (`scripts/setup-command-restrictions.sh`) is fundamentally incompatible with Claude Code's architecture AND the self-provisioning context:

1. **Shell Session Isolation**: Claude Code creates independent shell sessions for each command execution
2. **Function Loss**: Bash functions created in session A don't exist in session B  
3. **Security Gap**: Restrictions are lost across tool calls, making them ineffective
4. **Wrong Deployment Target**: Current approach targets control machine, but AI agents run on target systems

### Technical Root Cause
```bash
# Shell session 1: Restrictions applied
source <(./scripts/setup-command-restrictions.sh)
ansible --version  # Would be blocked

# Shell session 2: Restrictions gone  
ansible --version  # Executes normally (not blocked)
```

**Current Status Verification**: Status command confirms functions don't persist across Claude's tool calls.

### Business Impact (Enhanced with Self-Provisioning Context)
- **Security Risk**: Accidental execution of infrastructure commands could provision expensive resources or destroy existing infrastructure **on target systems**
- **Compliance Violation**: `.clinerules/only-user-can-run-ansible-commands.md` mandates restrictions but they're ineffective **where AI agents actually operate**
- **Workflow Disruption**: Unreliable restrictions force manual oversight and slow development **across distributed infrastructure**
- **Architectural Mismatch**: Current local restrictions don't address target system security where AI agents actually run

## MVP Scope & Requirements

### Core Problem to Solve (Enhanced)
AI agents (especially Claude Code) create sub-bash shells for every command execution, bypassing current restriction mechanisms. **CRITICAL**: AI agents run on target systems (`hobbiton`, `rivendell`, `moria`) under `desktop_users` accounts (`galadriel`, `legolas`) provisioned by this ansible project. Need bulletproof solution that:
1. Works in sub-shell scenarios **on target systems**
2. Is deployed via ansible Infrastructure-as-Code
3. Works cross-platform (Linux and Windows target systems)
4. Integrates with existing user provisioning workflows

### MVP Deliverables

#### 1. Sub-Shell Resistant Command Blocking (Distributed)
- Mechanism that works when Claude creates new bash sub-shells **on target systems**
- Block commands at shell level, not just process level **on provisioned infrastructure**
- Robust against various shell invocation patterns **across Linux and Windows platforms**
- Deployed via ansible to `desktop_users` on target systems

#### 2. Comprehensive Command Coverage
**Blocked Commands (Current + Enhanced)**:
- `ansible` (all variants)
- `ansible-playbook`
- `ansible-vault` 
- `ansible-inventory`
- `ansible-galaxy`
- `ansible-config`
- `vagrant`
- `docker`
- `tart`
- `aws`
- `hcloud`

**Blocking Strategy**: Block base commands completely (no parameter filtering)

#### 3. AI Agent Verification System (Remote)
- Simple command for AI agents to verify restrictions are active **on target systems**
- Clear feedback mechanism showing which commands are blocked **on remote systems**
- Remote verification capability via ansible tasks from control machine
- Cross-platform status checking (Linux and Windows target systems)

#### 4. Ansible-Integrated Deployment & Maintenance
- Deploy restrictions via ansible playbooks during infrastructure provisioning
- Integrate with existing `playbooks/setup-users.yml` workflow
- Cross-platform deployment (Linux and Windows target systems)
- Remote management and updates via ansible automation
- Configurable command list for future additions

### Success Criteria

**Primary Success Metrics**:
1. ✅ **Persistent Blocking**: Commands remain blocked across multiple separate Claude tool calls
2. ✅ **Status Verification**: `--status` correctly shows "BLOCKED" status across sessions
3. ✅ **Error Messages**: Blocked commands display project-rule-compliant error messages
4. ✅ **Robust Implementation**: Restrictions work reliably across Claude's session architecture
5. ✅ **User Override**: User can still execute commands when needed (restrictions only apply to Claude)

**Acceptance Test**:
```bash
# Verify restrictions persist across Claude tool calls
./scripts/setup-command-restrictions.sh --status

# Test blocking in sub-shell (should fail)
bash -c "ansible --version"
bash -c "vagrant status"
bash -c "docker ps"

# Verify legitimate commands still work
bash -c "ls -la"
bash -c "git status"
```

### Quality Trade-offs Accepted

**For Speed**:
- Manual verification rather than automated testing initially
- Basic error messages rather than detailed user guidance
- Simple implementation approach over complex architectures

**NOT Compromised**:
- Reliability in sub-shell scenarios (core requirement)
- Easy verification for AI agents (workflow requirement)
- Robust cross-session behavior (security requirement)
- Maintainable command list (future requirement)

## Implementation Strategy

### Solution Approaches for Developer Team Consideration

#### Approach A: Project-Local Wrapper Scripts
**Concept**: Create project-local wrapper scripts that intercept commands
- Create `scripts/bin/` directory with wrapper scripts for each restricted command
- Modify PATH to prioritize local wrappers
- Wrappers check if executing in project directory and either block or delegate

**Pros**: Very robust, hard to bypass, works across all shell sessions
**Cons**: PATH manipulation, requires finding real command paths

#### Approach B: Environment Detection
**Concept**: Use persistent markers (files/environment) to trigger restrictions
- Set marker file (`.ansible-restriction-active`) or environment variable
- Each bash session checks for marker and auto-applies restrictions
- Leverages existing function-based restriction system

**Pros**: Non-intrusive, toggleable, works with existing code
**Cons**: Requires Claude to check markers, relies on "good behavior"

#### Approach C: direnv Integration  
**Concept**: Use direnv to automatically apply restrictions when entering project directory
- Create `.envrc` file that sources the existing restriction script
- direnv automatically loads restrictions when entering directory
- Claude inherits restricted environment when launched from project directory

**Pros**: Automatic, leverages existing script, standard developer workflow
**Cons**: External dependency, user must run `direnv allow .`

#### Approach D: Shell Initialization
**Concept**: Modify how bash sessions start within project directory
- Use `BASH_ENV`, project-local `.bashrc`, or command prefixes
- Automatically source restrictions on every shell initialization
- Leverages bash's native initialization mechanisms

**Pros**: Automatic, clean, uses standard bash features
**Cons**: May require modifying Claude's bash tool behavior

#### Approach E: Global System-Wide Wrapper Scripts
**Concept**: Create global wrapper scripts that always block AI agent execution
- Create global wrapper scripts in `~/bin/` or `/usr/local/bin/` that always block AI agent execution
- Modify system PATH to prioritize global wrappers over real commands
- AI agents are blocked system-wide, users can bypass with full paths or sudo when needed

**Pros**: Extremely simple, bulletproof across all sessions and directories, no project-specific logic
**Cons**: System-wide impact, requires user path setup or sudo for real command access

### Self-Provisioning Implementation Approaches ⚠️ DISTRIBUTED DEPLOYMENT

**Critical Context**: AI agents run on target systems (`hobbiton`, `rivendell`, `moria`) provisioned by this ansible project under `desktop_users` accounts (`galadriel`, `legolas`). Restrictions must be deployed via ansible to multiple target systems.

#### Approach F: Ansible-Deployed User Profile Integration
**Concept**: Deploy restriction scripts to desktop_users' profiles on target systems
- Deploy restriction scripts to desktop_users' `.bashrc`/`.profile` on Linux target systems
- Windows: Deploy to PowerShell profiles for desktop_users on Windows target systems
- Use ansible templates to customize restrictions per user/platform
- Include in existing `playbooks/setup-users.yml` workflow
- Cross-platform deployment with platform-specific implementations

**Pros**: User-specific, cross-platform, ansible-integrated, persistent across reboots
**Cons**: Profile loading dependency, per-user deployment complexity

#### Approach G: Ansible-Deployed System-Wide Wrappers
**Concept**: Deploy global wrapper scripts to target systems via ansible
- Deploy wrapper scripts to `/usr/local/bin/` (Linux) or `C:\Windows\System32\` (Windows) via ansible
- Modify system PATH during user provisioning to prioritize wrappers
- Cross-platform ansible tasks for Linux and Windows deployment
- Include verification tasks in ansible playbooks
- Remote management and updates via ansible automation

**Pros**: System-wide on target systems, ansible-deployable, cross-platform, bulletproof, remotely manageable
**Cons**: System-wide impact on target systems, requires elevated privileges during deployment

#### Approach H: Ansible-Deployed Service-Based Blocking
**Concept**: Deploy services that monitor and block commands on target systems
- Deploy systemd services (Linux) or Windows services that monitor and block commands
- Service-based approach survives all session types and reboots
- Cross-platform ansible deployment with platform-specific implementations
- Remote monitoring and control capabilities via ansible
- Ultimate persistence across system updates and configuration changes

**Pros**: Ultimate persistence, service-level blocking, remotely manageable, survives all system changes
**Cons**: Complex implementation, service overhead, platform-specific development

### Implementation Strategy

**⚠️ Solution Selection Required**: The development team must choose which approach to implement based on:
- Technical feasibility with Claude Code's architecture
- Maintenance complexity and long-term sustainability
- Security robustness and bypass resistance
- User experience and setup simplicity

**Implementation Timeline**: 2-3 days maximum for chosen solution

### Risk Mitigation (Approach-Dependent)
- **Sub-shell bypass**: Solution-specific mitigation strategy required
- **Performance impact**: Lightweight implementation regardless of approach
- **Maintenance burden**: Centralized command list configuration
- **False positives**: Careful implementation and testing

## Requirements Compliance

### Functional Requirements (Enhanced for Distributed Deployment)
1. **Robust Implementation**: Restrictions work reliably across Claude's session architecture **on target systems** ✅
2. **Command Coverage**: All specified commands blocked **on target systems** ✅
3. **Persistence**: Restrictions survive across multiple Claude bash tool calls **on target systems** ✅
4. **Clear Messaging**: Blocked commands display clear error messages referencing project rules **on target systems** ✅
5. **Cross-Platform Support**: Works on AWS Linux, AWS Windows, and Hetzner Cloud target systems ✅
6. **Ansible Integration**: Deployed automatically during infrastructure provisioning ✅
7. **Remote Management**: Manageable and verifiable from control machine via ansible ✅

### Non-Functional Requirements
1. **Simplicity**: Solution easy to understand and maintain ✅
2. **Robustness**: Difficult to bypass accidentally or through normal usage ✅
3. **Non-Intrusive**: No interference with normal user command execution ✅
4. **Reversible**: Easy to disable when needed ✅

## Success Definition
**MVP Complete When**: AI agents operating on target systems (`hobbiton`, `rivendell`, `moria`) under `desktop_users` accounts cannot execute infrastructure commands even in sub-shells, restrictions are deployed via ansible during infrastructure provisioning, work cross-platform, and can be verified remotely from control machine.

**Future Enhancements**: Detailed logging, parameter-based filtering, automated testing, additional command categories.

---
**Product Owner**: Stefan  
**Timeline**: 2-3 days maximum  
**Priority**: Critical security and compliance issue resolution