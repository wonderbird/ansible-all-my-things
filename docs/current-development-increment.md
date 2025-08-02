# Current Development Increment: Robust Command Restriction System

## Product Owner Decision: MVP Increment Definition

**Business Goal**: Implement robust command restriction system that prevents AI agents from executing infrastructure commands while working in the ansible-all-my-things project directory.

**Business Driver**: Current mechanism is insufficient - AI agents ignore rules and execute forbidden commands, hindering workflow and creating security risks.

**Timeline**: URGENT - Delivery within 2-3 days maximum

## MVP Scope & Requirements

### Core Problem to Solve
AI agents (especially Claude Code) create sub-bash shells for every command execution, bypassing current restriction mechanisms. Need bulletproof solution that works in sub-shell scenarios.

### MVP Deliverables

#### 1. Sub-Shell Resistant Command Blocking
- Mechanism that works when Claude creates new bash sub-shells
- Block commands at shell level, not just process level
- Robust against various shell invocation patterns

#### 2. Comprehensive Command Coverage
**Blocked Commands (Phase 1)**:
- `ansible` (all variants)
- `ansible-playbook`
- `ansible-vault` 
- `ansible-inventory`
- `ansible-galaxy`
- `ansible-config`
- `vagrant`
- `docker`
- `aws`
- `hcloud`

**Blocking Strategy**: Block base commands completely (no parameter filtering)

#### 3. AI Agent Verification System
- Simple command for AI agents to verify restrictions are active
- Clear feedback mechanism showing which commands are blocked
- Integration with existing `./scripts/setup-command-restrictions.sh --status`

#### 4. Easy Setup & Maintenance
- Extend existing `./scripts/setup-command-restrictions.sh` script
- Maintain current sourcing pattern: `source <(./scripts/setup-command-restrictions.sh)`
- Configurable command list for future additions

### Success Criteria

**Primary Success Metrics**:
1. AI agents cannot execute any blocked commands in sub-shells
2. AI agents can verify restriction status with single command
3. System survives shell restarts and sub-shell creation
4. Zero false positives (blocking legitimate commands)

**Acceptance Test**:
```bash
# Setup restrictions
source <(./scripts/setup-command-restrictions.sh)

# Verify status works
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
- Focus on shell function overrides rather than complex interception
- Simple blocked/allowed binary decision (no parameter filtering)
- Manual verification rather than automated testing initially
- Basic error messages rather than detailed user guidance

**NOT Compromised**:
- Reliability in sub-shell scenarios (core requirement)
- Easy verification for AI agents (workflow requirement)
- Maintainable command list (future requirement)

## Implementation Strategy

### Phase 1: Core Blocking (Days 1-2)
1. Analyze current system gaps with sub-shells
2. Design shell function override mechanism
3. Implement comprehensive command list blocking
4. Test with Claude's sub-shell patterns

### Phase 2: Integration & Verification (Day 2-3)
1. Integrate with existing setup script
2. Add status verification enhancement
3. Test end-to-end workflow with AI agents
4. Document usage for AI agents

### Risk Mitigation
- **Sub-shell bypass**: Use shell function overrides + environment variables
- **Performance impact**: Lightweight function definitions only
- **Maintenance burden**: Centralized command list configuration
- **False positives**: Careful function naming and scoping

## Success Definition
**MVP Complete When**: AI agents working in project directory cannot execute infrastructure commands even in sub-shells, and can easily verify restriction status.

**Future Enhancements**: Detailed logging, parameter-based filtering, automated testing, additional command categories.

---
**Product Owner**: Stefan  
**Timeline**: 2-3 days maximum  
**Priority**: Urgent workflow blocker resolution