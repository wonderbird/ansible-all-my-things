# ADR-001: Command Restriction Mechanism for AI Agent Safety

Date: 2025-08-23  
Status: Accepted  
Deciders: Stefan (Product Owner)

## Context and Problem Statement

**The Challenge**: AI coding agents operating on remote development systems need safety controls to prevent accidental infrastructure destruction.

**Specific Problem**: This project provisions cloud development environments (`hobbiton`, `rivendell`, `moria`) where AI agents run under user accounts created by ansible automation. Without restrictions, these agents could accidentally execute commands like `ansible-playbook destroy.yml` or `docker system prune -a`, potentially destroying the very systems they're working on.

**Technical Constraint**: Claude Code (the AI agent) creates independent shell sessions for each command, making traditional shell-based blocking ineffective. Any solution must work across these isolated shell sessions and be deployable via Infrastructure-as-Code.

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

**Chosen option**: **AppArmor Integration** (Linux kernel-level security framework)

**Why AppArmor?** 
- **Tied for best score** (1.2/6.0) with Claude CLI Native approach
- **Kernel-level enforcement** provides maximum reliability - nearly impossible to bypass
- **Battle-tested** security framework built into Ubuntu/Debian systems  
- **User-specific targeting** via PAM configuration affects only AI agent accounts

**Fallback Strategy**: Claude CLI Native restrictions (simpler `.claude/settings.json` deployment) if AppArmor implementation proves too complex.

**Scope**: 
- **Phase 1**: Linux systems (`hobbiton`, `rivendell`) 
- **Future**: Windows system (`moria`) via Claude CLI Native
- **Commands Blocked**: `ansible`, `vagrant`, `docker`, `aws`, `hcloud` and variants

**Bottom Line**: AppArmor provides enterprise-grade security with minimal complexity for Ubuntu-based target systems.

## Implementation Strategy

**Two-phase implementation** with fallback strategy:

1. **Manual AppArmor Spike** (1-2 days) - Validate kernel-level blocking on target system
2. **Ansible Automation** (1 day) - Deploy via ansible Infrastructure-as-Code
3. **Fallback Available** - Claude CLI Native if AppArmor validation fails

*Implementation details in memory bank: [activeContext.md](../memory-bank/activeContext.md), [techContext.md](../memory-bank/techContext.md)*

## Constraints

### sudo Prohibition for AI Agents

**Rule**: AI agents cannot use `sudo` (administrative privileges) on target systems.

**Why?** Infrastructure-as-Code principles require that all changes be reproducible through source-controlled automation. If an AI agent needs `sudo`, it usually indicates:
- Missing ansible automation for that task
- Security misconfiguration  
- Attempt to make changes that should be in version control

**Implementation**: AI agent accounts (`galadriel`, `legolas`) are created without sudo privileges during system provisioning.

**Benefit**: Prevents AI agents from making unreproducible system changes while maintaining the ability to perform development tasks.

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

## Technical Overview

**How It Works**: AppArmor (Ubuntu's kernel-level security) prevents specific users from running specific programs, making it nearly impossible to bypass.

**Implementation**: Security profiles deployed to target systems block infrastructure commands for AI agent accounts only, while preserving normal development tool access.

**Result**: AI agents get "permission denied" for dangerous commands (`ansible`, `docker`) but can still use development tools (`git`, `python`) normally.

*Complete technical specifications in memory bank: [techContext.md](../memory-bank/techContext.md), [systemPatterns.md](../memory-bank/systemPatterns.md)*

*Current implementation status and success criteria in memory bank: [progress.md](../memory-bank/progress.md), [activeContext.md](../memory-bank/activeContext.md)*

## Future Enhancements

*Future enhancements and detailed technical specifications in memory bank: [techContext.md](../memory-bank/techContext.md)*

## References

- [Ubuntu AppArmor Documentation](https://ubuntu.com/server/docs/security-apparmor)
- [AppArmor Profile Syntax](https://manpages.ubuntu.com/manpages/focal/man5/apparmor.d.5.html)  
- [Claude Code Settings Documentation](https://docs.anthropic.com/en/docs/claude-code/settings)
- Original analysis: `docs/concept-branches/feat.command.restrictions.md`
- **Implementation Details**: See memory bank files [activeContext.md](../memory-bank/activeContext.md), [techContext.md](../memory-bank/techContext.md), [systemPatterns.md](../memory-bank/systemPatterns.md), [progress.md](../memory-bank/progress.md)

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
