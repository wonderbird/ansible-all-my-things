# ADR-001: Command Restriction Mechanism for AI Agent Safety

Date: 2025-08-23  
Status: Accepted  
Deciders: Stefan (Product Owner)

## Context and Problem Statement

Infrastructure automation projects require AI agent safety controls to prevent accidental resource provisioning or destruction on target systems where AI agents operate.

AI agents run on provisioned systems (`hobbiton`, `rivendell`, `moria`) under `desktop_users` accounts (`galadriel`, `legolas`) created by ansible. These agents must be prevented from executing infrastructure commands that could modify or destroy the very systems they're running on.

The core technical challenge is that Claude Code creates independent shell sessions for each command execution, requiring sub-shell resistant command blocking mechanisms deployed via ansible Infrastructure-as-Code.

**Business Impact**:
- **Security Risk**: Prevent accidental execution of infrastructure commands on target systems
- **Compliance Requirement**: Enforce project safety rules via ansible deployment  
- **Workflow Protection**: Enable safe AI agent operation during development
- **Timeline**: URGENT - 2-3 days maximum delivery requirement

### MVP Requirements

**Core MVP Deliverables**:
1. **Sub-Shell Resistant Command Blocking**: Mechanism that works across Claude's independent bash sessions
2. **Comprehensive Command Coverage**: Block all infrastructure commands (`ansible`, `vagrant`, `docker`, `aws`, `hcloud`) 
3. **AI Agent Verification System**: Remote verification capability via ansible tasks
4. **Ansible-Integrated Deployment**: Deploy via existing `playbooks/setup-users.yml` workflow

**Acceptance Tests on Target Systems**:
```bash
# These commands must fail for AI agent accounts
bash -c "ansible --version"
bash -c "vagrant status" 
bash -c "docker ps"

# These commands must continue working
bash -c "ls -la"
bash -c "git status"
```

## Decision Drivers

Priority-ordered criteria for evaluating solutions:

1. **Linux Support**: The solution must work for Linux target systems
2. **Effectiveness**: The security measure must be absolutely reliable across Claude's shell sessions
3. **User Level**: Must apply per-user basis, allowing unaffected human user accounts
4. **Maturity**: Prefer professionally maintained solutions over custom implementations
5. **Simplicity**: Easy to maintain solution for Ubuntu/Debian based target systems

### Decision Matrix

**Quality Rating Scale**:
| Rating | Quality      |
| ------ | ------------ |
| 1      | excellent    |
| 2      | good         |
| 3      | mediocre     |
| 4      | sufficient   |
| 5      | flawed       |
| 6      | unacceptable |

**Solution Evaluation**:
| Solution                         | Linux Support | Effectiveness | User Level | Maturity | Simplicity | Average Score | Viable |
| -------------------------------- | ------------- | ------------- | ---------- | -------- | ---------- | ------------- | ------ |
| 1 User Profile Integration       | 2             | 2             | 1          | 5        | 4          | 2.8           | ✅     |
| 2 System-Wide Wrappers           | 2             | 2             | 2          | 5        | 5          | 3.2           | ❌     |
| 3 Service-Based Blocking         | 1             | 3             | 1          | 5        | 5          | 3.0           | ❌     |
| 4 fapolicyd Integration          | 1             | 1             | 1          | 1        | 3          | 1.4           | ✅     |
| 5 AppArmor Integration           | 1             | 1             | 1          | 1        | 2          | 1.2           | ✅     |
| 6 Claude CLI Native Restrictions | 1             | 2             | 1          | 1        | 1          | 1.2           | ✅     |

*Solutions with any score > 4 eliminated (marked as ❌)*

**Key Insights**: AppArmor and Claude CLI Native tied at 1.2 average score. AppArmor selected for superior kernel-level effectiveness (priority criterion #2). Detailed scoring rationale provided in Appendix A.

## Considered Options Summary

**Six approaches evaluated** ranging from user profile integration to kernel-level security frameworks:

1. **User Profile Integration** (2.8 avg) - Shell profile deployment, failed on maturity/simplicity
2. **System-Wide Wrappers** (3.2 avg) - Global wrapper scripts, failed on simplicity requirements  
3. **Service-Based Blocking** (3.0 avg) - SystemD services, failed on maturity/simplicity
4. **fapolicyd Integration** (1.4 avg) - Red Hat security framework, viable but Linux-only
5. **AppArmor Integration** (1.2 avg) ⭐ **SELECTED** - Ubuntu native kernel security
6. **Claude CLI Native** (1.2 avg) ⭐ **FALLBACK** - Built-in Claude Code restrictions

*Detailed option analysis provided in Appendix B*

## Decision Outcome

**Chosen option**: **AppArmor Integration** with **Claude CLI Native Restrictions** as fallback.

**Rationale**: AppArmor achieved the same 1.2 average score as Claude CLI Native but provides superior effectiveness through kernel-level enforcement (second-highest priority criterion). This provides maximum security through Mandatory Access Control that is difficult to bypass.

**Implementation Scope**: 
- **Primary**: Linux target systems (`hobbiton`, `rivendell`) via AppArmor
- **Deferred**: Windows target system (`moria`) until needed
- **Fallback Strategy**: Claude CLI Native if AppArmor spike fails

**Blocked Commands**: `ansible`, `ansible-playbook`, `ansible-vault`, `ansible-inventory`, `ansible-galaxy`, `ansible-config`, `vagrant`, `docker`, `tart`, `aws`, `hcloud`

## Implementation Strategy

**Phase 1: Manual AppArmor Spike** (1-2 days)
- Deploy clean `rivendell` AWS Linux instance for testing
- Install AppArmor and create comprehensive `/etc/apparmor.d/ai-agent-block` profile
- Configure `/etc/security/pam_apparmor.conf` for user-specific targeting
- Execute acceptance tests: `bash -c "ansible --version"` must fail, `bash -c "ls -la"` must succeed
- Document spike results for ansible automation decision

**Phase 2: Ansible Automation** (1 day)  
- Create AppArmor deployment tasks in `playbooks/setup-users.yml`
- Add remote verification via `aa-status` command through ansible tasks
- Test idempotent deployment across multiple runs

**Fallback Implementation**: If AppArmor spike fails, implement Claude CLI Native via `.claude/settings.json` deployment

## Constraints

### sudo Prohibition for AI Agents

**Critical Constraint**: AI agents MUST NOT execute commands as root via `sudo`.

**Implementation**: Desktop_users accounts (`galadriel`, `legolas`) excluded from sudoers group during provisioning.

**Rationale**: Ensures reproducibility via Infrastructure as Code by limiting AI agents to source-controlled files only. The need for `sudo` usually indicates missing configuration or security/integrity problems.

**Enforcement**: AI agent rules extended to inform the user instead of running commands as root.

### Cross-Platform Requirements

**Target Systems**: 
- **hobbiton** (Hetzner Cloud Linux) - Primary persistent development environment
- **rivendell** (AWS Linux) - On-demand development server
- **moria** (AWS Windows) - Windows application server [deferred until needed]

**Deployment Method**: All restrictions must be deployable via ansible Infrastructure-as-Code during target system provisioning.

## Consequences

### Positive Consequences
- **Kernel-Level Security**: Mandatory Access Control provides maximum protection against command execution
- **User-Specific Targeting**: Restrictions apply only to AI agent accounts, human users unaffected  
- **Ansible Integration**: Seamlessly integrated with existing user provisioning workflows
- **Remote Verification**: Status checkable from control machine via `aa-status` command
- **Reboot Persistence**: Kernel-level restrictions survive system reboots and updates
- **Sub-shell Resistance**: Works across Claude Code's independent bash sessions

### Negative Consequences  
- **Linux-Only Solution**: Does not address Windows target system (`moria`) immediately
- **Learning Curve**: Requires AppArmor profile syntax knowledge for maintenance
- **System-Wide Impact**: Profiles apply at kernel level, though user-targeted
- **PAM Configuration**: Additional complexity for user-specific profile application

### Risk Mitigation
- **Fallback Strategy**: Claude CLI Native provides cross-platform alternative
- **Gradual Deployment**: Start with Linux systems, extend to Windows as needed
- **Documentation**: Comprehensive profile syntax documentation and examples
- **Testing**: Thorough acceptance testing on target systems before production deployment

## Technical Specifications

### AppArmor Profile Structure
```bash
# /etc/apparmor.d/ai-agent-block - comprehensive profile blocking infrastructure commands
#include <tunables/global>

profile ai-agent-block flags=(attach_disconnected) {
  #include <abstractions/base>
  
  # Block infrastructure commands
  deny /usr/bin/ansible* x,
  deny /usr/local/bin/vagrant x,
  deny /usr/bin/docker x,
  deny /usr/bin/aws x,
  deny /usr/bin/hcloud x,
  
  # Allow normal system operations
  /bin/** ux,
  /usr/bin/** ux,
  /usr/local/bin/** ux,
}
```

### User-Specific Targeting
```bash
# /etc/security/pam_apparmor.conf - apply profile to specific users
galadriel default_profile=ai-agent-block  
legolas default_profile=ai-agent-block
```

### Ansible Integration
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

- name: Verify AppArmor profile status
  command: aa-status
  register: apparmor_status
```

### Acceptance Tests
```bash
# These commands must fail on target systems for AI agent accounts
bash -c "ansible --version"
bash -c "vagrant status" 
bash -c "docker ps"

# These commands must continue working
bash -c "ls -la"
bash -c "git status"
bash -c "python --version"
```

### Success Criteria
- ✅ **Persistent Blocking**: Commands remain blocked across multiple Claude tool calls on target systems
- ✅ **Cross-Platform Deployment**: Works on AWS Linux, AWS Windows, and Hetzner Cloud systems  
- ✅ **Ansible Integration**: Deployed automatically during infrastructure provisioning
- ✅ **Target User Coverage**: Applied to all `desktop_users` (galadriel, legolas) on target systems
- ✅ **Reboot Persistence**: Restrictions survive system reboots and updates
- ✅ **Remote Verification**: Status checkable from control machine via ansible

### Claude CLI Native Fallback Specifications

**Fallback Settings Template**:
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

**Ansible Deployment**:
```yaml
- name: Create Claude settings directory
  file:
    path: "{{ ansible_user_dir }}/.claude"
    state: directory
    mode: '0755'
    
- name: Deploy Claude command restrictions
  template:
    src: claude-settings.json.j2
    dest: "{{ ansible_user_dir }}/.claude/settings.json"
    mode: '0644'
    
- name: Verify Claude settings deployment
  stat:
    path: "{{ ansible_user_dir }}/.claude/settings.json"
  register: claude_settings_stat
```

## Future Enhancements

**Beyond MVP Scope**:
- **Detailed Command Logging**: Log attempted command executions for audit trails
- **Parameter-Based Filtering**: Allow specific ansible commands while blocking others
- **Automated Testing**: Continuous verification of command restriction effectiveness
- **Additional Command Categories**: Extend blocking to other infrastructure tools
- **Windows Implementation**: Full Claude CLI Native deployment for `moria` target system
- **Graduated Restrictions**: Different restriction levels based on AI agent trust levels

## References

- [Ubuntu AppArmor Documentation](https://ubuntu.com/server/docs/security-apparmor)
- [AppArmor Profile Syntax](https://manpages.ubuntu.com/manpages/focal/man5/apparmor.d.5.html)  
- [pam_apparmor Configuration](https://wiki.debian.org/AppArmor/HowToUse)
- [Claude Code Settings Documentation](https://docs.anthropic.com/en/docs/claude-code/settings)
- Original analysis: `docs/concept-branches/feat.command.restrictions.md`

---

## Appendix A: Decision Matrix Scoring Rationale

### Scoring Methodology

**Linux Support**: All solutions work on Linux systems, with varying degrees of native platform integration.

**Effectiveness**: Scored based on reliability and bypass resistance:
- **Kernel-level enforcement** (AppArmor, fapolicyd): Maximum reliability through mandatory access control
- **Application-level blocking** (Claude CLI): Good reliability within Claude's architecture  
- **Custom implementations**: Lower reliability due to development complexity and potential edge cases

**User Level**: Ability to apply restrictions per-user without affecting other accounts:
- System-wide wrappers can implement user-specific logic by checking current user identity
- Profile-based and native solutions naturally support per-user deployment

**Maturity**: Professional maintenance vs. custom development:
- Enterprise security frameworks (AppArmor, fapolicyd, Claude CLI): Professionally maintained
- Custom implementations: Require development and maintenance from scratch

**Simplicity**: Learning curve and deployment complexity from Ubuntu/Debian perspective:
- Claude CLI: Familiar JSON configuration
- AppArmor: Native Ubuntu support but requires profile syntax knowledge  
- fapolicyd: Fedora-focused tooling adds complexity for Ubuntu environments

## Appendix B: Detailed Option Analysis

### 1. User Profile Integration
Deploy restriction scripts to desktop_users' profiles (`.bashrc`/`.profile`) on target systems via ansible templates.

**Technical Implementation**: 
- Deploy restriction scripts to desktop_users' `.bashrc`/`.profile` on Linux target systems
- Windows: Deploy to PowerShell profiles for desktop_users on Windows target systems
- Use ansible templates to customize restrictions per user/platform
- Include in existing `playbooks/setup-users.yml` workflow

**Pros**: User-specific, cross-platform, ansible-integrated, persistent across reboots  
**Cons**: Profile loading dependency, per-user deployment complexity

### 2. System-Wide Wrappers  
Deploy global wrapper scripts to `/usr/local/bin/` on target systems, with PATH modification to prioritize wrappers.

**Technical Implementation**:
- Deploy wrapper scripts to `/usr/local/bin/` (Linux) or `C:\Windows\System32\` (Windows) via ansible
- Wrapper scripts check current user identity and only block commands for specific accounts (`galadriel`, `legolas`)
- Modify system PATH during user provisioning to prioritize wrappers
- Cross-platform ansible tasks for Linux and Windows deployment

**Pros**: System-wide deployment, bulletproof blocking, remotely manageable via ansible  
**Cons**: System-wide impact, requires elevated privileges during deployment

### 3. Service-Based Blocking
Deploy systemd services that monitor and block commands on target systems.

**Technical Implementation**:
- Deploy systemd services (Linux) or Windows services that monitor and block commands
- Service-based approach survives all session types and reboots
- Cross-platform ansible deployment with platform-specific implementations
- Remote monitoring and control capabilities via ansible

**Pros**: Ultimate persistence, service-level blocking, survives all session types  
**Cons**: Complex implementation, service overhead, platform-specific development

### 4. fapolicyd Integration  
Use Red Hat's File Access Policy Daemon for application allowlisting on Linux target systems.

**Technical Implementation**:
- Deploy fapolicyd rules via ansible to block infrastructure commands on Linux target systems
- Configure user/group-based policies to allow commands for human users but block for AI agent accounts
- Leverage RPM trust database for application allowlisting
- Integration with systemd for service-level persistence

**Example Rules**:
```bash
# Block ansible for specific user accounts
deny_audit perm=execute uid=galadriel : path=/usr/bin/ansible
deny_audit perm=execute uid=legolas : path=/usr/bin/ansible

# Allow for admin users
allow perm=execute gid=wheel : path=/usr/bin/ansible
```

**Pros**: Kernel-level enforcement, comprehensive application control, professional maintenance  
**Cons**: Linux-only (doesn't address Windows target `moria`), overkill for simple command blocking

### 5. AppArmor Integration ⭐ **SELECTED**
Deploy AppArmor profiles with user-specific restrictions via ansible for Ubuntu/Debian target systems.

**Technical Implementation**: See main Technical Specifications section.

**Pros**: Native Ubuntu support, kernel-level Mandatory Access Control, user-specific targeting via pam_apparmor, shell session resistant  
**Cons**: Linux-only solution, requires AppArmor profile syntax knowledge

### 6. Claude CLI Native Restrictions ⭐ **FALLBACK**
Deploy `.claude/settings.json` files to desktop_users' home directories via ansible.

**Technical Implementation**: See Claude CLI Native Fallback Specifications section.

**Pros**: Native Claude architecture, inherently sub-shell resistant, cross-platform, elegant deployment  
**Cons**: Claude-specific, effectiveness tied to Claude Code tool architecture