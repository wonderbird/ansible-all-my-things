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
**Cross-Provider Development**: Automated development environments across providers
**Windows Application Access**: Claude Desktop Application (Windows-only)
**Cost-Optimized Infrastructure**: Provider choice based on usage patterns
**AI Agent Safety**: Command restrictions deployed to target systems

## Development Setup

### Required Tools
**Automated Installation:**
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Ansible collections
ansible-galaxy collection install -r requirements.yml
```

### Multi-Provider Environment Configuration
```bash
# Production Environment Credentials
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export AWS_DEFAULT_REGION="eu-north-1"
export HCLOUD_TOKEN="your-hcloud-token"

# Ansible configuration (automated vault password handling)
export ANSIBLE_VAULT_PASSWORD_FILE="./scripts/echo-vault-password-environment-variable.sh"
export ANSIBLE_HOST_KEY_CHECKING=False
```

### Project Structure
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
├── Unified Inventory & Configuration:
│   ├── inventories/aws_ec2.yml   # AWS inventory ✅ WORKING
│   ├── inventories/hcloud.yml    # Hetzner inventory ✅ WORKING
│   └── inventories/group_vars/   # Provider-aware variables with secrets ✅ WORKING
├── Dependencies:
│   ├── requirements.txt          # Python dependencies ✅ COMPLETED
│   └── requirements.yml          # Ansible collections ✅ COMPLETED
└── memory-bank/                  # Cross-provider documentation ✅ CURRENT
```

## AI Agent Safety Implementation

### Target System Deployment Requirements
**Target Systems**: AI agents operate on provisioned systems (`hobbiton`, `rivendell`, `moria`) under `desktop_users` accounts (`galadriel`, `legolas`).

**Deployment Constraints**:
- **Cross-Platform**: Must work on AWS Linux, AWS Windows, and Hetzner Cloud systems
- **Ansible Integration**: Deploy via ansible playbooks during infrastructure provisioning
- **Shell Session Resistance**: Work across Claude Code's independent bash sessions
- **User Isolation**: Apply only to AI agents, not human users

### Implementation Approaches

#### User Profile Integration
**Concept**: Deploy restriction scripts to desktop_users' profiles on target systems
- **Linux Implementation**: `.bashrc`/`.profile` modification via ansible templates
- **Windows Implementation**: PowerShell profile deployment for desktop_users
- **Ansible Integration**: Extend existing `playbooks/setup-users.yml` workflow
- **Persistence**: Restrictions loaded on every shell session

#### System-Wide Wrappers
**Concept**: Deploy global wrapper scripts to target systems via ansible
- **Linux Implementation**: `/usr/local/bin/` deployment with PATH modification
- **Windows Implementation**: `C:\Windows\System32\` deployment via ansible
- **Deployment**: Cross-platform ansible tasks for installation and verification
- **Management**: Remote updates and status checking via ansible

#### Service-Based Blocking
**Concept**: Deploy services that monitor and block commands on target systems
- **Linux Implementation**: systemd services deployed via ansible
- **Windows Implementation**: Windows services deployed via ansible
- **Monitoring**: Service-based approach survives all session types and reboots
- **Control**: Remote monitoring and management capabilities via ansible

#### AppArmor Integration (Ubuntu/Debian Linux Systems) ✅ SELECTED

**Technical Specifications**: See [ADR-001 Command Restriction Decision](../docs/architecture-decisions/001-command-restrictions.md) for decision rationale.

**AppArmor Profile Structure**:
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

**User-Specific Targeting**:
```bash
# /etc/security/pam_apparmor.conf - apply profile to specific users
galadriel default_profile=ai-agent-block  
legolas default_profile=ai-agent-block
```

**Ansible Integration Tasks**:
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

#### Claude CLI Native Restrictions ✅ FALLBACK OPTION

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

**Blocked Commands**: `ansible`, `ansible-playbook`, `ansible-vault`, `ansible-inventory`, `ansible-galaxy`, `ansible-config`, `vagrant`, `docker`, `tart`, `aws`, `hcloud`

**Comprehensive Acceptance Tests**:
```bash
# These commands must fail on target systems for AI agent accounts
bash -c "ansible --version"
bash -c "ansible-playbook --help"
bash -c "vagrant status" 
bash -c "docker ps"
bash -c "aws --version"
bash -c "hcloud version"

# These commands must continue working normally
bash -c "ls -la"
bash -c "git status"
bash -c "python --version"
bash -c "curl --version"
bash -c "ssh -V"
```

### Technical Constraints

**Claude Code Architecture**: Creates independent shell sessions for each command execution, requiring sub-shell resistant solutions.

**Security Constraints**:
- **sudo Prohibition**: AI agents MUST NOT execute commands as root - enforced by excluding desktop_users from sudoers group
- **Acceptance Tests**: Sub-shell command blocking must work (`bash -c "ansible --version"` fails, `bash -c "ls -la"` succeeds)

**Deployment Requirements**:
- Must be deployable via ansible playbooks across multiple platforms
- Must integrate with existing user provisioning workflows (`playbooks/setup-users.yml`)
- Must work on both Linux and Windows target systems
- Must be maintainable and debuggable across distributed infrastructure
- Should not impact normal user workflows on target systems

## Infrastructure Requirements ✅ IMPLEMENTED

### Current System Capabilities
- **Multi-Provider Support**: AWS and Hetzner Cloud with dynamic inventory
- **Cross-Platform**: Linux and Windows environments with unified patterns
- **Secret Management**: Ansible Vault with automated password handling
- **Testing Integration**: Vagrant-based testing environments

### Cost Analysis
- **Hetzner Cloud**: ~$4/month with predictable EU pricing
- **AWS Linux**: ~$8-10/month with on-demand usage
- **AWS Windows**: ~$60/month base with on-demand reducing actual costs

## Tool Usage Patterns

### Current Infrastructure Patterns
```yaml
# Multi-provider inventory management ✅ WORKING
# Cross-provider SSH key authentication ✅ WORKING
# Unified command structure across providers ✅ WORKING
# Automated vault password handling ✅ WORKING
```

### AI Agent Safety Architecture
**Current Priority**: AppArmor kernel-level command restrictions implementation
**Timeline**: 3 scrum stories (0.5 + 1-2 + 1 days) for complete implementation
**Selected Approach**: AppArmor Integration with comprehensive profile strategy
**Implementation Strategy**: ✅ Stand-Alone Profiling method mastered, comprehensive single-profile approach validated
**Learning Completed**: ✅ Hands-on experience with `aa-genprof`, `aa-logprof`, profile creation, and sub-shell testing

## Dependencies & Integration

### Current Working Dependencies ✅ IMPLEMENTED
- **Multi-Provider Collections**: `amazon.aws`, `hetzner.hcloud`, `ansible.windows`
- **Python Dependencies**: `boto3`, `botocore` for AWS support
- **Inventory Integration**: Dynamic inventory plugins working across providers
- **Secret Management**: Unified Ansible Vault patterns for all implementations

### Command Restriction Implementation
**AI Agent Safety System**: Deploy robust command restriction mechanism to target systems via ansible automation

The technical foundation provides a solid base for infrastructure automation with the command restriction system ready for implementation on target systems.