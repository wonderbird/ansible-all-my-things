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

### Decision Drivers

The following aspectes are most important for the decision. These aspects are sorted by priority.

- **Linux Support:** The solution must work for Linux
- **Effectiveness:** The security measure must be absolutely reliable
- **User Level:** The solution must be employable on a per-user basis. It must be possible to have user accounts that are unaffected from the security measures.
- **Maturity:** Prefer a mature solution which is maintained by a professional developer team
- **Simplicity:** Prefer a simple and easy to maintain solution for Debian/Ubuntu based systems

### Unimportant Aspects

The following aspects are not important and can be neglected:

- **One-fits-all solution:** As long as the solution works for any Linux OS, it is sufficient

### Decision Matrix

| Rating | Quality      |
| ------ | ------------ |
| 1      | excellent    |
| 2      | good         |
| 3      | mediocre     |
| 4      | sufficient   |
| 5      | flawed       |
| 6      | unacceptable |

| Solution                         | Linux Support | Effectiveness | User Level | Maturity | Simplicity | Average Score | All <= 4 |
| -------------------------------- | ------------- | ------------- | ---------- | -------- | ---------- | ------------- | -------- |
| 1 User Profile Integration       | 2             | 2             | 1          | 5        | 4          | 2,8           | ✅       |
| 2 System-Wide Wrappers           | 2             | 2             | 6          | 5        | 4          |               | ❌       |
| 3 Service-Based Blocking         | 1             | 2             | 1          | 5        | 5          |               | ❌       |
| 4 fapolicyd Integration          | 1             | 1             | 1          | 1        | 3          | 1,4           | ✅       |
| 5 AppArmor Integration           | 1             | 1             | 1          | 1        | 2          | 1,2           | ✅       |
| 6 Claude CLI Native Restrictions | 1             | 1             | 1          | 1        | 1          | 1,0           | ✅       |

### Six Implementation Approaches

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

#### 5. AppArmor Integration (Ubuntu/Debian Linux Systems)
**Concept**: Deploy AppArmor profiles with user-specific restrictions via ansible for Ubuntu/Debian target systems

**Implementation**: Deploy AppArmor profiles to target systems blocking infrastructure commands for specific desktop users

**Profile Structure**:
```bash
# Example profile for blocking commands per user
#include <tunables/global>

profile ai_agent_block flags=(attach_disconnected) {
  #include <abstractions/base>
  
  # Block infrastructure commands for specific users
  owner /usr/bin/ansible ux,
  owner /usr/bin/vagrant ux,
  owner /usr/bin/docker ux,
  owner /usr/bin/aws ux,
  owner /usr/bin/hcloud ux,
  
  # Allow normal system commands
  /bin/* ux,
  /usr/bin/* ux,
  /usr/local/bin/* ux,
}
```

**User-Specific Targeting via pam_apparmor**:
```bash
# Configure PAM to apply profiles based on user accounts
# /etc/security/pam_apparmor.conf
galadriel default_profile=ai_agent_block
legolas default_profile=ai_agent_block
```

**Ansible Integration**:
```yaml
- name: Deploy AppArmor profile for AI agent command restrictions
  template:
    src: ai-agent-block.profile.j2
    dest: /etc/apparmor.d/ai-agent-block
  notify: reload apparmor

- name: Configure pam_apparmor for desktop users
  template:
    src: pam_apparmor.conf.j2  
    dest: /etc/security/pam_apparmor.conf
  notify: restart ssh

- name: Enable AppArmor profile
  command: aa-enforce /etc/apparmor.d/ai-agent-block
```

**Pros**: 
- **Native Ubuntu/Debian Support**: Ships by default, fully supported security framework
- **User-Specific Targeting**: Can apply restrictions to specific desktop_users via pam_apparmor
- **Kernel-Level Enforcement**: Mandatory Access Control that's difficult to bypass
- **Ansible Integration**: Simple profile deployment and management via ansible
- **Persistent Security**: Restrictions survive reboots and system updates
- **Remote Verification**: Status checking via `aa-status` command through ansible
- **Shell Session Resistant**: Works across all shell types and sub-shells

**Cons**:
- **Linux-Only Solution** (doesn't address Windows target `moria`)
- **PAM Configuration Required**: Additional complexity for user-specific targeting
- **Profile Development**: Requires AppArmor profile syntax knowledge
- **System-Wide Impact**: Profiles apply at kernel level

**Key Resources**:
- [Ubuntu AppArmor Documentation](https://ubuntu.com/server/docs/security-apparmor)
- [AppArmor Profile Syntax](https://manpages.ubuntu.com/manpages/focal/man5/apparmor.d.5.html)
- [pam_apparmor Configuration](https://wiki.debian.org/AppArmor/HowToUse)
- [AppArmor Management Tools](https://documentation.ubuntu.com/server/how-to/security/apparmor/)

#### 6. Claude CLI Native Restrictions
**Concept**: Use Claude Code's built-in permission system to block commands at the tool execution level

**Implementation**: Deploy `.claude/settings.json` files to desktop_users' home directories on target systems via ansible

**Settings Template**:
```json
{
  "permissions": {
    "deny": [
      "Bash(ansible:*)",
      "Bash(vagrant:*)", 
      "Bash(docker:*)",
      "Bash(tart:*)",
      "Bash(aws:*)",
      "Bash(hcloud:*)"
    ]
  }
}
```

**Ansible Integration**:
```yaml
- name: Create Claude settings directory
  file:
    path: "{{ ansible_user_dir }}/.claude"
    state: directory
    
- name: Deploy Claude command restrictions
  template:
    src: claude-settings.json.j2
    dest: "{{ ansible_user_dir }}/.claude/settings.json"
```

**Deployment Locations**:
- **User-level**: `~/.claude/settings.json` (standard approach)
- **Project-level**: `.claude/settings.json` (for project-specific restrictions)
- **Enterprise-managed**: `/etc/claude-code/managed-settings.json` (Linux system-wide)

**Pros**: 
- **Native Architecture**: Works directly with Claude's tool execution system
- **Sub-shell Resistant**: Inherently handles Claude's independent sessions
- **Cross-Platform**: Built-in Linux + Windows support through Claude
- **Zero Brittleness**: No shell profile dependencies or wrapper complications
- **Elegant Deployment**: Simple file management via ansible templates
- **Remote Verification**: Standard file existence/content checking via ansible
- **Bulletproof Persistence**: Restrictions apply automatically across all Claude sessions

**Cons**:
- **Claude-Specific**: Only works when Claude CLI is the execution environment
- **Tool Dependency**: Effectiveness tied to Claude Code tool architecture

**Key Resources**:
- [Claude Code Settings Documentation](https://docs.anthropic.com/en/docs/claude-code/settings)
- [Claude Code CLI Reference](https://docs.anthropic.com/en/docs/claude-code/cli-reference)
- [Claude Code Security Features](https://docs.anthropic.com/en/docs/claude-code/security)

### Implementation Decision
**Solution Selection Required**: Choose implementation approach based on:
- Technical feasibility with Claude Code's architecture
- Maintenance complexity and long-term sustainability
- Security robustness and bypass resistance
- Cross-platform compatibility requirements

**Implementation Timeline**: 2-3 days maximum for chosen solution

**Available Approaches**: Six implementation approaches documented for development team and software architect analysis and decision

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