# Current Development Increment: Command Restriction System Fix

## Feature Request

Implement a robust command restriction system that prevents Claude Code from executing ansible, vagrant, and other infrastructure commands while working in the ansible-all-my-things project directory.

## Problem Description

### Current Situation
The project includes a command restriction system (`scripts/setup-command-restrictions.sh`) designed to prevent AI agents from executing potentially dangerous infrastructure commands. However, the current implementation is fundamentally broken when used with Claude Code.

### Technical Root Cause
The restriction system uses bash functions to override commands (e.g., creating a bash function named `ansible` that blocks the real ansible command). However, Claude Code's Bash tool creates **independent shell sessions** for each command execution. This means:

1. `source <(./scripts/setup-command-restrictions.sh)` creates blocking functions in shell session A
2. Functions exist only within that specific shell session
3. Next `Bash` tool call creates shell session B (fresh environment)
4. Blocking functions are lost - commands are no longer restricted

### Current Behavior
```bash
# Shell session 1: Restrictions are applied
source <(./scripts/setup-command-restrictions.sh)
ansible --version  # Would be blocked

# Shell session 2: Restrictions are gone  
ansible --version  # Executes normally (not blocked)
```

### Expected Behavior
Claude should be consistently prevented from executing restricted commands across all bash sessions when working in this project directory, regardless of shell session boundaries.

## Business Impact

**Security Risk**: Without working restrictions, Claude can accidentally execute infrastructure commands that could:
- Provision expensive cloud resources
- Modify or destroy existing infrastructure
- Access sensitive credentials and environments

**Project Compliance**: The `.clinerules/only-user-can-run-ansible-commands.md` rule states this restriction is mandatory and cannot be overridden by future instructions.

## Solution Approaches Identified

### Approach A: Wrapper Scripts
**Concept**: Create project-local wrapper scripts that intercept commands
- Create `scripts/bin/` directory with wrapper scripts for each restricted command
- Modify PATH to prioritize local wrappers
- Wrappers check if executing in project directory and either block or delegate to real commands

**Pros**: Very robust, hard to bypass, works across all shell sessions
**Cons**: PATH manipulation, requires finding real command paths

### Approach B: Environment Detection  
**Concept**: Use persistent markers (files/environment) to trigger restrictions
- Set marker file (`.ansible-restriction-active`) or environment variable
- Each bash session checks for marker and auto-applies restrictions
- Leverages existing function-based restriction system

**Pros**: Non-intrusive, toggleable, works with existing code
**Cons**: Requires Claude to check markers, relies on "good behavior"

### Approach C: Shell Initialization
**Concept**: Modify how bash sessions start within project directory
- Use `BASH_ENV`, project-local `.bashrc`, or command prefixes
- Automatically source restrictions on every shell initialization
- Leverages bash's native initialization mechanisms

**Pros**: Automatic, clean, uses standard bash features
**Cons**: May require modifying Claude's bash tool behavior

### Approach D: direnv Integration
**Concept**: Use direnv to automatically apply restrictions when entering project directory
- Create `.envrc` file that sources the existing restriction script
- direnv automatically loads restrictions when entering directory
- direnv automatically unloads restrictions when leaving directory
- Claude inherits restricted environment when launched from project directory

**Implementation**:
```bash
# Create .envrc file:
echo 'source <(./scripts/setup-command-restrictions.sh)' > .envrc

# User setup (one-time):
direnv allow .
```

**Behavior**:
- User navigates to project directory → restrictions automatically active
- User launches Claude → Claude inherits restricted environment
- User leaves project directory → restrictions automatically removed
- Works with existing script, minimal code changes required

**Pros**: 
- Automatic activation/deactivation
- Leverages existing script unchanged
- Standard developer workflow (direnv widely adopted)
- Visual feedback from direnv messages
- Truly project-scoped behavior
- Reversible and user-friendly

**Cons**: 
- External dependency (requires direnv installation)
- User must run `direnv allow .` to enable
- Could be bypassed if user disables direnv globally

## Requirements

### Functional Requirements
1. **Project-Scoped**: Restrictions apply only when working in ansible-all-my-things directory
2. **Command Coverage**: Block ansible, ansible-playbook, ansible-inventory, vagrant, docker, tart, aws, hcloud
3. **Persistence**: Restrictions must survive across multiple Claude bash tool calls
4. **Clear Messaging**: Blocked commands should display clear error messages referencing project rules

### Non-Functional Requirements
1. **Simplicity**: Solution should be easy to understand and maintain
2. **Robustness**: Difficult to bypass accidentally or through normal usage
3. **Non-Intrusive**: Should not interfere with normal user command execution
4. **Reversible**: Should be easy to disable when needed

## Success Criteria

1. ✅ **Persistent Blocking**: Commands remain blocked across multiple separate bash tool calls
2. ✅ **Status Verification**: `./scripts/setup-command-restrictions.sh --status` correctly shows "BLOCKED" status
3. ✅ **Error Messages**: Blocked commands display project-rule-compliant error messages
4. ✅ **Project Scope**: Restrictions only apply within ansible-all-my-things directory
5. ✅ **User Override**: User can still execute commands when needed (restrictions only apply to Claude)

## Implementation Priority

**High Priority**: This is a critical security and compliance issue that affects the safety of infrastructure operations. The current broken state means Claude is operating without intended safety restrictions.

## Next Steps

1. **Solution Selection**: Choose most appropriate approach based on technical constraints and requirements
2. **Prototype Implementation**: Create working proof-of-concept for chosen approach  
3. **Testing**: Verify restrictions work across multiple bash sessions
4. **Documentation**: Update project documentation with new restriction mechanism
5. **Validation**: Confirm compliance with `.clinerules` requirements