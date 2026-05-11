# Technical Context: Ansible All My Things

## Core Technologies

### Ansible Ecosystem
- **Ansible Core**: Infrastructure automation and configuration management
- **Ansible Vault**: Encryption for sensitive data and credentials
- **Dynamic Inventory**: Multi-provider plugins for automatic host discovery
- **Collections**: Extended functionality for AWS, Hetzner Cloud, and Windows

### Multi-Provider Cloud Infrastructure
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
│   ├── provision.yml                 # Hetzner Cloud Linux
│   ├── provision-aws-linux.yml       # AWS Linux provisioning
│   └── provision-aws-windows.yml     # AWS Windows provisioning
├── Configuration:
│   ├── configure.yml                 # Hetzner Cloud configuration
│   ├── configure-linux.yml           # Linux configuration (used by tests)
│   └── configure-aws-windows.yml     # AWS Windows configuration
├── Cleanup:
│   ├── destroy.yml                   # Hetzner Cloud cleanup
│   └── destroy-aws.yml              # AWS unified cleanup
├── Provisioners:
│   ├── provisioners/hcloud-linux.yml     # Hetzner provisioner
│   ├── provisioners/aws-linux.yml        # AWS Linux provisioner
│   └── provisioners/aws-windows.yml      # AWS Windows provisioner
├── Unified Inventory & Configuration:
│   ├── inventories/aws_ec2.yml           # AWS dynamic inventory
│   ├── inventories/hcloud.yml            # Hetzner dynamic inventory
│   ├── inventories/vagrant_docker.yml    # Vagrant Docker inventory
│   ├── inventories/vagrant_tart.yml      # Vagrant Tart inventory
│   └── inventories/group_vars/           # Provider-aware variables with secrets
├── Testing:
│   ├── test/docker/                      # Vagrant Docker test environment
│   └── test/tart/                        # Vagrant Tart test environment
├── Dependencies:
│   ├── requirements.txt              # Python dependencies
│   └── requirements.yml             # Ansible collections
└── docs/                            # Project documentation
```

## Unified Inventory System

The project uses a dual-keyed-groups inventory strategy: each host belongs to both a generic cross-provider group (`@linux`, `@windows`) and a provider-specific group (`@hcloud_linux`, `@aws_ec2_linux`, `@aws_ec2_windows`). This enables writing playbooks that target platforms uniformly while retaining the ability to apply provider-specific overrides.

### Inventory Directory Tree
```
inventories/
├── aws_ec2.yml              # AWS dynamic inventory (dual keyed_groups)
├── hcloud.yml               # Hetzner dynamic inventory (dual keyed_groups)
├── vagrant_docker.yml       # Vagrant Docker static inventory
├── vagrant_tart.yml         # Vagrant Tart static inventory
├── requirements.txt         # Python inventory-plugin dependencies
├── requirements.yml         # Ansible collection dependencies
└── group_vars/
    ├── all/
    │   └── vars.yml         # Vault-encrypted shared secrets
    ├── aws_ec2/             # AWS-specific variables
    ├── aws_ec2_linux/       # AWS Linux overrides
    ├── aws_ec2_windows/     # AWS Windows overrides
    ├── hcloud/              # Hetzner-specific variables
    ├── hcloud_linux/        # Hetzner Linux overrides
    ├── vagrant_docker/      # Vagrant Docker variables (admin_user handling)
    └── vagrant_tart/        # Vagrant Tart variables (admin_user handling)
```

### Group Structure
```
@all:
  @linux:               # All Linux hosts (cross-provider)
    @hcloud_linux:      # Hetzner Linux hosts
    @aws_ec2_linux:     # AWS Linux hosts
    @vagrant_docker:    # Vagrant Docker Linux hosts
  @windows:             # All Windows hosts (cross-provider)
    @aws_ec2_windows:   # AWS Windows hosts
  @aws_ec2:             # All AWS hosts
    @aws_ec2_linux
    @aws_ec2_windows
  @hcloud:              # All Hetzner hosts
    @hcloud_linux
```

### Variable Precedence (4-tier)
Variables are resolved from broadest to most specific:
1. `all` — defaults for every host
2. `platform` (e.g., `hcloud`, `aws_ec2`) — provider-level overrides
3. `provider_platform` (e.g., `hcloud_linux`, `aws_ec2_windows`) — provider + platform combination

The `platform:` host variable (e.g., `platform: "linux"`) is set via the inventory `keyed_groups` configuration. It replaced the legacy `ansible_group:` tag and provides backward-compatible cross-provider grouping.

## Testing Infrastructure

Each test provider has its own subdirectory under `test/`:

```
test/
├── docker/
│   ├── Vagrantfile           # Docker-backend Vagrant definition
│   ├── ansible.cfg           # Points to ../../inventories (shared inventory)
│   └── README.md
└── tart/
    ├── Vagrantfile           # Tart-backend Vagrant definition
    ├── ansible.cfg           # Points to ../../inventories (shared inventory)
    └── README.md
```

The `ansible.cfg` inside each test directory sets `inventory_path = ../../inventories`, so test VMs load variables from the same unified `group_vars/` tree as production hosts. Provider-specific defaults (e.g., `admin_user_on_fresh_system: vagrant` for Vagrant Docker) live in `inventories/group_vars/vagrant_docker/`.

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

**Technical Specifications**: See [ADR-001 Command Restriction Decision](architecture/decisions/001-command-restrictions.md) for decision rationale.

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

## Per-VM Specifications

| VM | Provider | Region | OS | Auth chain | Cost |
|---|---|---|---|---|---|
| hobbiton | Hetzner Cloud cx22 | Helsinki | Ubuntu 24.04 LTS | root → galadriel | ~$4/mo |
| rivendell | AWS t3.micro/small | eu-north-1 | Ubuntu 24.04 LTS | ubuntu → galadriel | ~$8-10/mo |
| moria | AWS t3.large | eu-north-1 | Windows Server 2025 | Administrator | ~$60/mo |
| dagorlad | Vagrant Docker | local | Ubuntu Linux (container) | vagrant | free |
| lorien | Vagrant Tart | local | macOS-compatible | vagrant | free |

## Windows Server Implementation

### Connection Configuration
AWS Windows hosts use SSH with a PowerShell shell rather than WinRM:

```yaml
ansible_connection: ssh
ansible_user: Administrator
ansible_shell_type: powershell
ansible_shell_executable: powershell
```

### Chocolatey Package Manager
```yaml
- name: Install Chocolatey
  win_shell: |
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  args:
    creates: C:\ProgramData\chocolatey\bin\choco.exe
```

### Achieved Windows Configuration
- OpenSSH Server enabled with PowerShell as the default SSH shell
- SSH key authentication configured via `icacls` permissions
- Windows Firewall configured via PowerShell (ports 22 and 3389)
- Desktop Experience feature installed
- RDP optimized: 32-bit color depth, clipboard sharing enabled

### Security Group (Shared Between Linux and Windows)
```yaml
- name: Configure ansible-sg security group
  amazon.aws.ec2_group:
    name: ansible-sg
    rules:
      - proto: tcp
        ports: [22]
        cidr_ip: "{{ current_public_ip }}/32"
      - proto: tcp
        ports: [3389]
        cidr_ip: "{{ current_public_ip }}/32"
```

The `current_public_ip` variable is detected dynamically via `ipinfo.io`. The `ansible-sg` security group is shared between Linux and Windows EC2 instances.

### AMI Reference
Windows Server 2025 AMI: `ami-01998fe5b868df6e3` (eu-north-1)

### Collections
```yaml
# requirements.yml
collections:
  - ansible.windows
  - community.windows
  - amazon.aws
  - hetzner.hcloud
  - community.general
```

## Idiomatic Configuration

Secrets are stored in `inventories/group_vars/all/vars.yml` as Ansible Vault-encrypted values. The vault password is supplied automatically via `ansible.cfg`:

```ini
[defaults]
vault_password_file = scripts/echo-vault-password-environment-variable.sh
```

Playbooks do not use `vars_files:` directives — all secrets are loaded from group_vars automatically by Ansible's inventory resolution. A `vault-template.yml` file documents the required secret keys without their values.

## Provider Differences Reference

| Attribute | AWS Linux | AWS Windows | Hetzner Linux |
|---|---|---|---|
| Connection | SSH | SSH | SSH |
| Default User | ubuntu → galadriel | Administrator | root → galadriel |
| Package Manager | apt | Chocolatey | apt |
| Instance Type | t3.micro/small | t3.large | cx22 |
| Desktop Access | No | RDP (3389) | GNOME via backup/restore |
| Cost | ~$8-10/mo | ~$60/mo | ~$4/mo |
| Authentication | SSH key | SSH key + Windows password (vault) | SSH key |
| Provisioning Time | ~5-8 min | ~15-20 min | ~3-5 min |
| Inventory Groups | @aws_ec2, @aws_ec2_linux, @linux | @aws_ec2, @aws_ec2_windows, @windows | @hcloud, @hcloud_linux, @linux |

## Infrastructure Requirements

### Current System Capabilities
- **Multi-Provider Support**: AWS and Hetzner Cloud with dynamic inventory
- **Cross-Platform**: Linux and Windows environments with unified patterns
- **Secret Management**: Ansible Vault with automated password handling
- **Testing Integration**: Vagrant-based testing environments (Docker and Tart backends)

### Cost Analysis
- **Hetzner Cloud**: ~$4/month with predictable EU pricing
- **AWS Linux**: ~$8-10/month with on-demand usage
- **AWS Windows**: ~$60/month base with on-demand reducing actual costs

## Dependencies & Integration

- **Multi-Provider Collections**: `amazon.aws`, `hetzner.hcloud`, `ansible.windows`, `community.windows`, `community.general`
- **Python Dependencies**: `boto3`, `botocore` for AWS dynamic inventory
- **Inventory Integration**: Dynamic inventory plugins working across providers
- **Secret Management**: Unified Ansible Vault patterns for all implementations
