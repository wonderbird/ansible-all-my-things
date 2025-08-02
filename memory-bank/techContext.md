# Technical Context: Ansible All My Things

## Core Technologies

### Ansible Ecosystem
- **Ansible Core**: Infrastructure automation and configuration management
- **Ansible Vault**: Encryption for sensitive data and credentials
- **Dynamic Inventory**: Multi-provider plugins for automatic host discovery
- **Collections**: Extended functionality for AWS, Hetzner Cloud, and Windows

### Multi-Provider Cloud Infrastructure ✅ PRODUCTION-READY
**Hetzner Cloud**: Primary provider for persistent development environments (~$4/month)
**AWS EC2**: Multi-platform provider for diverse workloads (~$8-60/month depending on usage)

### Target Applications & Use Cases
**Cross-Provider Development**: Automated development environments across providers ✅ ACHIEVED
**Windows Application Access**: Claude Desktop Application (Windows-only) ✅ ACHIEVED
**Cost-Optimized Infrastructure**: Provider choice based on usage patterns ✅ IMPLEMENTED

## Development Setup

### Required Tools
**Automated Installation:**
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Ansible collections
ansible-galaxy collection install -r requirements.yml
```

### Multi-Provider Environment Configuration ✅ ENHANCED WITH IDIOMATIC ANSIBLE
```bash
# Production Environment Credentials
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export AWS_DEFAULT_REGION="eu-north-1"
export HCLOUD_TOKEN="your-hcloud-token"

# Ansible configuration (automated vault password handling)
# ansible.cfg includes vault_password_file = ansible-vault-password.txt
export ANSIBLE_HOST_KEY_CHECKING=False
```

### Project Structure (Current Implementation)
```
ansible-all-my-things/
├── Multi-Provider Provisioning:
│   ├── provision.yml             # Hetzner Cloud Linux ✅ WORKING
│   ├── provision-aws-linux.yml   # AWS Linux provisioning ✅ WORKING
│   └── provision-aws-windows.yml # AWS Windows provisioning ✅ WORKING
├── Configuration:
│   ├── configure.yml             # Hetzner Cloud configuration ✅ WORKING
│   ├── configure-linux.yml       # Linux configuration (used by tests) ✅ WORKING
│   └── configure-aws-windows.yml # AWS Windows configuration ✅ WORKING
├── Cleanup:
│   ├── destroy.yml               # Hetzner Cloud cleanup ✅ WORKING
│   └── destroy-aws.yml           # AWS unified cleanup ✅ WORKING
├── Unified Inventory & Idiomatic Configuration:
│   ├── inventories/aws_ec2.yml   # AWS inventory ✅ WORKING
│   ├── inventories/hcloud.yml    # Hetzner inventory ✅ WORKING
│   └── inventories/group_vars/   # Provider-aware variables with secrets ✅ ENHANCED
├── Dependencies:
│   ├── requirements.txt          # Python dependencies ✅ COMPLETED
│   └── requirements.yml          # Ansible collections ✅ COMPLETED
└── memory-bank/                  # Cross-provider documentation ✅ CURRENT
```

## Technical Constraints & Requirements

### AI Agent Safety Constraints ⚠️ CRITICAL LIMITATION DISCOVERED

#### Claude Code Shell Session Isolation ⚠️ FUNDAMENTAL ISSUE
**Problem**: Claude Code creates independent shell sessions for each command execution, causing traditional bash function-based command restrictions to fail.

**Technical Root Cause**:
```bash
# Shell session 1: Restrictions applied
source <(./scripts/setup-command-restrictions.sh)
ansible --version  # Would be blocked

# Shell session 2: Restrictions gone  
ansible --version  # Executes normally (not blocked)
```

**Impact**: Current `.clinerules/only-user-can-run-ansible-commands.md` rule is technically unenforceable, creating security and compliance violations.

**Required Solution Characteristics**:
- **Sub-Shell Resistant**: Must work across independent bash sessions
- **Project-Scoped**: Only apply restrictions within ansible-all-my-things directory
- **Verification Capable**: AI agents must be able to verify restriction status across sessions
- **User-Friendly**: Must not interfere with normal user command execution
- **Maintainable**: Simple to understand, debug, and extend

#### Implementation Constraint Analysis
**Cannot Rely On**:
- Bash functions (lost across sessions)
- Environment variables (not inherited by independent sessions)
- Session-specific configuration (Claude creates fresh sessions)

**Must Work With**:
- PATH manipulation (persists across sessions if properly configured)
- File system markers (persistent across sessions)
- Directory-specific configuration (direnv, project-local files)
- Shell initialization hooks (BASH_ENV, .bashrc)

#### Command Restriction Implementation Options ⚠️ SOLUTION SELECTION REQUIRED

**Approach A: Project-Local Wrapper Scripts**
- Create `scripts/bin/` directory with wrapper scripts for each restricted command
- Modify PATH to prioritize local wrappers that check project directory and either block or delegate
- Pros: Very robust, hard to bypass, works across all shell sessions
- Cons: PATH manipulation complexity, requires finding real command paths

**Approach B: Environment Detection**
- Set marker file (`.ansible-restriction-active`) or environment variable
- Each bash session checks for marker and auto-applies restrictions
- Pros: Non-intrusive, toggleable, works with existing code
- Cons: Requires Claude to check markers, relies on "good behavior"

**Approach C: direnv Integration**
- Create `.envrc` file that sources existing restriction script
- direnv automatically loads restrictions when entering directory
- Pros: Automatic, leverages existing script, standard developer workflow
- Cons: External dependency, user must run `direnv allow .`

**Approach D: Shell Initialization**
- Use `BASH_ENV`, project-local `.bashrc`, or command prefixes
- Automatically source restrictions on every shell initialization
- Pros: Automatic, clean, uses standard bash features
- Cons: May require modifying Claude's bash tool behavior

**Approach E: Global System-Wide Wrapper Scripts**
- Create global wrapper scripts in `~/bin/` or `/usr/local/bin/` that always block AI agent execution
- Modify system PATH to prioritize global wrappers over real commands
- AI agents are blocked system-wide, users can bypass with full paths or sudo when needed
- Pros: Extremely simple, bulletproof across all sessions and directories, no project-specific logic
- Cons: System-wide impact, requires user path setup or sudo for real command access

**Blocked Commands (Current + Enhanced)**:
- `ansible` (all variants: ansible-playbook, ansible-vault, ansible-inventory, ansible-galaxy, ansible-config)
- `vagrant` (all subcommands)
- `docker` (all subcommands)
- `tart` (all subcommands)
- `aws` (AWS CLI)
- `hcloud` (Hetzner Cloud CLI)

### Infrastructure Requirements ✅ IMPLEMENTED

#### Current System Capabilities
- **Multi-Provider Support**: AWS and Hetzner Cloud with dynamic inventory
- **Cross-Platform**: Linux and Windows environments with unified patterns
- **Secret Management**: Ansible Vault with automated password handling
- **Testing Integration**: Vagrant-based testing environments

#### Cost Analysis (Current Implementation)
- **Hetzner Cloud**: ~$4/month with predictable EU pricing ✅ COST LEADER
- **AWS Linux**: ~$8-10/month with on-demand usage ✅ IMPLEMENTED
- **AWS Windows**: ~$60/month base with on-demand reducing actual costs ✅ IMPLEMENTED

## Tool Usage Patterns

### Current Infrastructure Patterns (Implemented)
```yaml
# Multi-provider inventory management ✅ WORKING
# Cross-provider SSH key authentication ✅ WORKING
# Unified command structure across providers ✅ WORKING
# Automated vault password handling ✅ WORKING
```

### Security Architecture (Broken - Requires Fix)
**Current State**: Command restrictions fail with Claude Code's independent session architecture
**Required**: Sub-shell resistant command blocking system
**Timeline**: 2-3 days maximum for implementation
**Priority**: Critical security compliance issue

## Dependencies & Integration

### Current Working Dependencies ✅ IMPLEMENTED
- **Multi-Provider Collections**: `amazon.aws`, `hetzner.hcloud`, `ansible.windows`
- **Python Dependencies**: `boto3`, `botocore` for AWS support
- **Inventory Integration**: Dynamic inventory plugins working across providers
- **Secret Management**: Unified Ansible Vault patterns for all implementations

### Critical Missing Dependency ⚠️ URGENT
**AI Agent Safety System**: Robust command restriction mechanism compatible with Claude Code's architecture

The technical foundation is solid for infrastructure automation, but the critical security gap in AI agent safety controls must be resolved immediately to enable safe development workflows.