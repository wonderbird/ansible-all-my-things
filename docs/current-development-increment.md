# Current Development Increment: Robust Command Restriction System

## Product Owner Decision: MVP Increment Definition

**Business Goal**: Implement robust command restriction system that prevents AI agents from executing infrastructure commands while working in the ansible-all-my-things project directory.

**Business Driver**: Current mechanism is fundamentally broken with Claude Code - AI agents ignore rules and execute forbidden commands, creating security risks and workflow problems.

**Timeline**: URGENT - Delivery within 2-3 days maximum

## Problem Analysis

### Current Broken State
The existing command restriction system (`scripts/setup-command-restrictions.sh`) is fundamentally incompatible with Claude Code's architecture:

1. **Shell Session Isolation**: Claude Code creates independent shell sessions for each command execution
2. **Function Loss**: Bash functions created in session A don't exist in session B  
3. **Security Gap**: Restrictions are lost across tool calls, making them ineffective

### Technical Root Cause
```bash
# Shell session 1: Restrictions applied
source <(./scripts/setup-command-restrictions.sh)
ansible --version  # Would be blocked

# Shell session 2: Restrictions gone  
ansible --version  # Executes normally (not blocked)
```

**Current Status Verification**: Status command confirms functions don't persist across Claude's tool calls.

### Business Impact
- **Security Risk**: Accidental execution of infrastructure commands could provision expensive resources or destroy existing infrastructure
- **Compliance Violation**: `.clinerules/only-user-can-run-ansible-commands.md` mandates restrictions but they're ineffective
- **Workflow Disruption**: Unreliable restrictions force manual oversight and slow development

## MVP Scope & Requirements

### Core Problem to Solve
AI agents (especially Claude Code) create sub-bash shells for every command execution, bypassing current restriction mechanisms. Need bulletproof solution that works in sub-shell scenarios.

### MVP Deliverables

#### 1. Sub-Shell Resistant Command Blocking
- Mechanism that works when Claude creates new bash sub-shells
- Block commands at shell level, not just process level
- Robust against various shell invocation patterns

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

#### 3. AI Agent Verification System
- Simple command for AI agents to verify restrictions are active
- Clear feedback mechanism showing which commands are blocked
- Enhanced `./scripts/setup-command-restrictions.sh --status` that works across sessions

#### 4. Easy Setup & Maintenance
- Extend existing `./scripts/setup-command-restrictions.sh` script
- Project-scoped restrictions (only apply in ansible-all-my-things directory)
- Configurable command list for future additions

### Success Criteria

**Primary Success Metrics**:
1. ✅ **Persistent Blocking**: Commands remain blocked across multiple separate Claude tool calls
2. ✅ **Status Verification**: `--status` correctly shows "BLOCKED" status across sessions
3. ✅ **Error Messages**: Blocked commands display project-rule-compliant error messages
4. ✅ **Project Scope**: Restrictions only apply within ansible-all-my-things directory
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
- Project-scoped behavior (security requirement)
- Maintainable command list (future requirement)

## Implementation Strategy

### Solution Approaches for Developer Team Consideration

#### Approach A: Wrapper Scripts
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

### Functional Requirements
1. **Project-Scoped**: Restrictions apply only when working in ansible-all-my-things directory ✅
2. **Command Coverage**: All specified commands blocked ✅
3. **Persistence**: Restrictions survive across multiple Claude bash tool calls ✅
4. **Clear Messaging**: Blocked commands display clear error messages referencing project rules ✅

### Non-Functional Requirements
1. **Simplicity**: Solution easy to understand and maintain ✅
2. **Robustness**: Difficult to bypass accidentally or through normal usage ✅
3. **Non-Intrusive**: No interference with normal user command execution ✅
4. **Reversible**: Easy to disable when needed ✅

## Success Definition
**MVP Complete When**: AI agents working in project directory cannot execute infrastructure commands even in sub-shells, can easily verify restriction status, and restrictions persist across all Claude tool calls.

**Future Enhancements**: Detailed logging, parameter-based filtering, automated testing, additional command categories.

---
**Product Owner**: Stefan  
**Timeline**: 2-3 days maximum  
**Priority**: Critical security and compliance issue resolution