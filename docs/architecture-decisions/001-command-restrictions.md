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

## Decision Drivers

Priority-ordered criteria for evaluating solutions:

1. **Linux Support**: The solution must work for Linux target systems
2. **Effectiveness**: The security measure must be absolutely reliable across Claude's shell sessions
3. **User Level**: Must apply per-user basis, allowing unaffected human user accounts
4. **Maturity**: Prefer professionally maintained solutions over custom implementations
5. **Simplicity**: Easy to maintain solution for Ubuntu/Debian based target systems

## Considered Options

### 1. User Profile Integration
Deploy restriction scripts to desktop_users' profiles (`.bashrc`/`.profile`) on target systems via ansible templates.

**Pros**: User-specific, cross-platform, ansible-integrated, persistent across reboots  
**Cons**: Profile loading dependency, per-user deployment complexity  
**Score**: 2.8 average

### 2. System-Wide Wrappers  
Deploy global wrapper scripts to `/usr/local/bin/` on target systems, with PATH modification to prioritize wrappers.

**Pros**: System-wide deployment, bulletproof blocking, remotely manageable via ansible  
**Cons**: System-wide impact, requires elevated privileges during deployment  
**Score**: Failed (Simplicity = 5)

### 3. Service-Based Blocking
Deploy systemd services that monitor and block commands on target systems.

**Pros**: Ultimate persistence, service-level blocking, survives all session types  
**Cons**: Complex implementation, service overhead, platform-specific development  
**Score**: Failed (Maturity = 5, Simplicity = 5)

### 4. fapolicyd Integration  
Use Red Hat's File Access Policy Daemon for application allowlisting on Linux target systems.

**Pros**: Kernel-level enforcement, comprehensive application control, professional maintenance  
**Cons**: Linux-only (doesn't address Windows target `moria`), overkill for simple command blocking  
**Score**: 1.4 average  
**Assessment**: Not recommended due to cross-platform requirements

### 5. AppArmor Integration ⭐ **SELECTED**
Deploy AppArmor profiles with user-specific restrictions via ansible for Ubuntu/Debian target systems.

**Pros**: Native Ubuntu support, kernel-level Mandatory Access Control, user-specific targeting via pam_apparmor, shell session resistant  
**Cons**: Linux-only solution, requires AppArmor profile syntax knowledge  
**Score**: 1.2 average

### 6. Claude CLI Native Restrictions ⭐ **FALLBACK**
Deploy `.claude/settings.json` files to desktop_users' home directories via ansible.

**Pros**: Native Claude architecture, inherently sub-shell resistant, cross-platform, elegant deployment  
**Cons**: Claude-specific, effectiveness tied to Claude Code tool architecture  
**Score**: 1.2 average (tied)

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

## References

- [Ubuntu AppArmor Documentation](https://ubuntu.com/server/docs/security-apparmor)
- [AppArmor Profile Syntax](https://manpages.ubuntu.com/manpages/focal/man5/apparmor.d.5.html)  
- [pam_apparmor Configuration](https://wiki.debian.org/AppArmor/HowToUse)
- [Claude Code Settings Documentation](https://docs.anthropic.com/en/docs/claude-code/settings)
- Original analysis: `docs/concept-branches/feat.command.restrictions.md`