# Technical Context: Ansible All My Things

## Core Technologies

### Ansible Ecosystem
- **Ansible Core**: Infrastructure automation and configuration management
- **Ansible Vault**: Encryption for sensitive data and credentials
- **Dynamic Inventory**: Multi-provider plugins for automatic host discovery
- **Collections**: Extended functionality for AWS, Hetzner Cloud, and Windows

### Multi-Provider Cloud Infrastructure
**Hetzner Cloud**: Primary provider for persistent development environments
**AWS EC2**: Multi-platform provider for diverse workloads

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
│   └── provision.yml                 # Unified provisioning (provider + platform params)
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
    │   ├── vars.yml         # Shared variables (references vault.yml)
    │   ├── vault.yml        # Vault-encrypted secrets (user-created, not in repo)
    │   └── vault-template.yml # Documents required secret keys
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

See [ADR-001 Command Restriction Decision](architecture/decisions/001-command-restrictions.md) for context, evaluated options, decision rationale, acceptance tests, and deployment details.

For VM inventory and provider comparison see [README.md](../README.md).

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

Secrets are stored in `inventories/group_vars/all/vault.yml` (user-created, not in repo) as Ansible Vault-encrypted values. `vars.yml` is a plain wrapper that references variables from `vault.yml`. `vault-template.yml` documents the required secret keys without their values. The vault password is supplied automatically via `ansible.cfg`:

```ini
[defaults]
vault_password_file = scripts/echo-vault-password-environment-variable.sh
```

Playbooks do not use `vars_files:` directives — all secrets are loaded from group_vars automatically by Ansible's inventory resolution. See [docs/user-manual/important-concepts.md](user-manual/important-concepts.md) for setup instructions.

## Infrastructure Requirements

### Current System Capabilities
- **Multi-Provider Support**: AWS and Hetzner Cloud with dynamic inventory
- **Cross-Platform**: Linux and Windows environments with unified patterns
- **Secret Management**: Ansible Vault with automated password handling
- **Testing Integration**: Vagrant-based testing environments (Docker and Tart backends)

## Dependencies & Integration

- **Multi-Provider Collections**: `amazon.aws`, `hetzner.hcloud`, `ansible.windows`, `community.windows`, `community.general`
- **Python Dependencies**: `boto3`, `botocore` for AWS dynamic inventory
- **Inventory Integration**: Dynamic inventory plugins working across providers
- **Secret Management**: Unified Ansible Vault patterns for all implementations
