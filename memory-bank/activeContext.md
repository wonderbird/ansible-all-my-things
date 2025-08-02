# Active Context: Ansible All My Things

## Current Work Focus

### Robust Command Restriction System Implementation 🔴 URGENT
**Goal**: Implement bulletproof command restriction system that prevents AI agents from executing infrastructure commands while working in the ansible-all-my-things project directory.

**Status**: 🔴 IN PROGRESS - Critical security compliance issue requiring immediate resolution

**Business Context**: **SECURITY CRITICAL** - Current command restriction mechanism is fundamentally broken with Claude Code's architecture, creating security risks and compliance violations.

**Timeline**: **URGENT** - 2-3 days maximum delivery requirement

**Core Problem**: Claude Code creates independent shell sessions for each command execution, causing bash function-based restrictions to be lost across tool calls, making current `.clinerules/only-user-can-run-ansible-commands.md` ineffective.

**Business Impact**:
- **Security Risk**: Accidental execution of infrastructure commands could provision expensive resources or destroy existing infrastructure
- **Compliance Violation**: Project rules are technically unenforceable with current implementation
- **Workflow Disruption**: Unreliable restrictions force manual oversight and slow development

**MVP Deliverables**:
1. **Sub-Shell Resistant Command Blocking**: Mechanism that works when Claude creates new bash sub-shells
2. **Comprehensive Command Coverage**: Block all infrastructure commands (`ansible`, `ansible-playbook`, `ansible-vault`, `ansible-inventory`, `ansible-galaxy`, `ansible-config`, `vagrant`, `docker`, `tart`, `aws`, `hcloud`)
3. **AI Agent Verification System**: Enhanced `--status` command that works across sessions
4. **Easy Setup & Maintenance**: Extend existing `./scripts/setup-command-restrictions.sh` with project-scoped restrictions

**Success Criteria**:
- ✅ **Persistent Blocking**: Commands remain blocked across multiple separate Claude tool calls
- ✅ **Status Verification**: `--status` correctly shows "BLOCKED" status across sessions
- ✅ **Error Messages**: Blocked commands display project-rule-compliant error messages
- ✅ **Project Scope**: Restrictions only apply within ansible-all-my-things directory
- ✅ **User Override**: User can still execute commands when needed (restrictions only apply to Claude)

**Implementation Options Under Consideration**:
- **Approach A**: Wrapper Scripts (project-local PATH manipulation)
- **Approach B**: Environment Detection (persistent markers/files)
- **Approach C**: direnv Integration (automatic directory-based loading)
- **Approach D**: Shell Initialization (BASH_ENV/project-local .bashrc)

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
