# System Patterns: Ansible All My Things

## Architecture Overview

### Cross-Provider Infrastructure System ✅ IMPLEMENTED & TESTED
**Current Reality**: Three production-ready implementations plus comprehensive testing framework

**Proven Architecture:**
```
Multi-Provider Infrastructure:
├── Production Environments:
│   ├── Hetzner Cloud Linux (hobbiton)     # Complete desktop development environment
│   ├── AWS Linux (rivendell)              # On-demand development server  
│   └── AWS Windows (moria)                # Windows application server
└── Testing Environments:
    ├── Vagrant Docker (dagorlad)          # Linux testing with Docker provider
    └── Vagrant Tart (lorien)              # macOS-compatible testing environment
```

**Cross-Provider Patterns ✅ WORKING:**
- **Dynamic Inventory**: `amazon.aws.aws_ec2`, `hetzner.hcloud.hcloud` plugins plus static Vagrant inventories
- **Platform Grouping**: Consistent linux/windows grouping across all providers including test environments
- **SSH Key Management**: Single SSH key pair working across AWS, Hetzner Cloud, and test environments
- **Idiomatic Secret Management**: Vault-encrypted variables in `inventories/group_vars/all/vars.yml` ✅ NEW
- **Automated Vault Access**: `ansible.cfg` with `vault_password_file` for seamless secret handling ✅ NEW
- **Testing Integration**: Unified secret management across production and test environments ✅ ENHANCED

**AI Agent Safety Patterns ⚠️ CRITICAL IMPLEMENTATION REQUIRED:**
- **Command Restriction System**: ⚠️ BROKEN - Current bash function approach fails with Claude Code's shell session isolation
- **Security Compliance**: ⚠️ VIOLATED - `.clinerules/only-user-can-run-ansible-commands.md` technically unenforceable
- **Sub-Shell Resistance**: ⚠️ MISSING - Need mechanism that persists across independent bash sessions
- **Verification System**: ⚠️ UNRELIABLE - Status checking doesn't work across Claude tool calls

### Enhanced Inventory System ✅ COMPLETED & IMPROVED
**Implemented Structure:**
```
inventories/
├── aws_ec2.yml                # AWS dynamic inventory with dual keyed_groups
├── hcloud.yml                 # Hetzner Cloud dynamic inventory with dual keyed_groups
├── vagrant_docker.yml         # Vagrant Docker static inventory for testing
├── vagrant_tart.yml           # Vagrant Tart static inventory for testing
├── group_vars/
│   ├── all/
│   │   ├── vars.yml           # Encrypted secrets (was playbooks/vars-secrets.yml) ✅ MOVED
│   │   └── vault-template.yml # Secret documentation template ✅ NEW
│   ├── linux/vars.yml         # Cross-provider Linux variables (hobbiton + rivendell + dagorlad + lorien)
│   ├── windows/vars.yml       # Cross-provider Windows variables (moria)
│   ├── aws_ec2/vars.yml       # AWS provider-specific overrides
│   ├── aws_ec2_linux/vars.yml # AWS Linux-specific variables
│   ├── aws_ec2_windows/vars.yml # AWS Windows-specific variables
│   ├── hcloud/vars.yml        # Hetzner provider-specific overrides
│   ├── hcloud_linux/vars.yml  # Hetzner Linux-specific variables
│   ├── vagrant_docker/vars.yml # Vagrant Docker provider-specific variables
│   └── vagrant_tart/vars.yml   # Vagrant Tart provider-specific variables
├── requirements.txt           # Python dependencies for multi-provider support
└── requirements.yml           # Ansible collections for all providers
```

**Enhanced Inventory Pattern ✅ IMPLEMENTED & TESTED:**
- **Dual Group Structure**: Both cross-provider (@linux, @windows) and provider-specific (@aws_ec2_linux, @hcloud_linux, @vagrant_docker, @vagrant_tart) groups ✅ IMPLEMENTED
- **Enhanced Targeting**: Fine-grained automation control with provider-specific groups including test environments ✅ WORKING
- **Improved Tag Semantics**: `platform: "linux"` instead of `ansible_group: "linux"` for clarity ✅ IMPLEMENTED
- **Enhanced Variable Precedence**: all → platform → provider → provider_platform hierarchy including test providers ✅ IMPLEMENTED
- **Backward Compatibility**: Existing playbooks continue working while enabling enhanced features ✅ VERIFIED
- **Dependency Management**: Streamlined setup with requirements files ✅ COMPLETED
- **Testing Integration**: Test environments follow same inventory patterns as production ✅ VERIFIED

### Implemented Cross-Provider Playbook Structure
```
Cross-Provider Patterns:
├── Production Environments:
│   ├── Hetzner Cloud Linux:  provision.yml → provisioners/hcloud.yml → configure.yml
│   ├── AWS Linux:            provision-aws-linux.yml → provisioners/aws-linux.yml
│   ├── AWS Windows:          provision-aws-windows.yml → provisioners/aws-windows.yml → configure-aws-windows.yml
│   └── Unified Cleanup:      destroy.yml (Hetzner) / destroy-aws.yml (AWS)
└── Testing Environments:
    ├── Vagrant Docker:       vagrant up → configure-linux.yml (via Vagrantfile)
    └── Vagrant Tart:         vagrant up → configure-linux.yml (via Vagrantfile)
```

**Separation of Concerns (Achieved):**
- **Provision Layer**: Provider-specific infrastructure creation with platform-specific configurations
- **Configuration Layer**: Platform-specific system setup and application installation  
- **Unified Patterns**: Consistent structure across providers with provider-specific optimizations
- **Testing Layer**: Vagrant-based testing environments using same configuration patterns as production

### Multi-Provider Pattern (Implemented & Tested)
All implementations follow consistent structure with provider and platform-specific implementations:
```
Production Environments:
Hetzner Cloud Linux:  provision.yml → configure.yml → destroy.yml
AWS Linux:            provision-aws-linux.yml → destroy-aws.yml
AWS Windows:          provision-aws-windows.yml → configure-aws-windows.yml → destroy-aws.yml

Testing Environments:
Vagrant Docker:       vagrant up → configure-linux.yml → vagrant destroy
Vagrant Tart:         vagrant up → configure-linux.yml → vagrant destroy
```

### Testing Infrastructure Pattern (Implemented)
**Problem Resolved**: Fixed undefined group_vars in test environments by integrating with main inventory structure

**Testing Architecture:**
```
Testing Infrastructure:
├── test/docker/               # Vagrant Docker provider testing
│   ├── Vagrantfile              # Docker provider configuration with inventory integration
│   ├── ansible.cfg              # Points to ../../inventories for unified variable loading
│   └── README.md                # Testing procedures and documentation
├── test/tart/                 # Vagrant Tart provider testing
│   ├── Vagrantfile              # Tart provider configuration with inventory integration
│   ├── ansible.cfg              # Points to ../../inventories for unified variable loading
│   └── README.md                # Testing procedures and documentation
└── test/README.md             # Overall testing framework documentation
```

**Key Testing Patterns:**
- **Unified Variable Loading**: Test environments use main project inventory structure (../../inventories)
- **Provider-Specific Variables**: vagrant_docker and vagrant_tart group_vars for admin user handling
- **Consistent Patterns**: Test environments follow same configuration patterns as production
- **Security Integration**: SSH key management and security guidelines for testing environments

**Provider Abstraction Achieved:**
- **Common Interface**: Similar command patterns across providers including test environments
- **Provider-Specific Optimizations**: Each provider optimized for its strengths (production) and testing needs
- **Consistent Patterns**: Same architectural principles applied across production and test environments
- **Unified User Experience**: Predictable workflows regardless of provider or environment type
- **Testing Integration**: Test environments follow production patterns for reliable validation

## Key Technical Decisions

### Cross-Provider Architecture Strategy (Achieved)
**Provider Abstraction**: Successfully implemented consistent patterns across AWS and Hetzner Cloud
- **Shared Patterns**: Dynamic inventory, SSH key management, platform-based grouping
- **Provider-Specific Optimizations**: AWS for on-demand, Hetzner Cloud for persistent environments
- **Consistent Interface**: Similar command patterns across all implementations

### Multi-Platform Extension Strategy (Achieved)
**Platform Adaptation**: Successfully extended Linux patterns to Windows Server
- **Shared AWS Infrastructure**: Reused security groups, networking, tagging patterns
- **Platform-Specific Configuration**: Windows-specific modules and PowerShell approaches
- **Consistent Interface**: Same command patterns for provision/configure/destroy achieved

### Provider-Specific Architecture Decisions (Implemented)

#### Hetzner Cloud Optimization Strategy
**Persistent Environment Model**: Optimized for long-term development use
- **Complete Desktop**: Full GNOME environment with comprehensive application suite
- **Backup/Restore**: Automated data persistence across reprovisioning cycles
- **Cost Optimization**: Predictable EU-based pricing at ~$4/month
- **User Experience**: Designed for daily development workflow

#### AWS Multi-Platform Strategy  
**On-Demand Model**: Optimized for intermittent usage patterns
- **Linux Foundation**: Minimal server setup with dynamic inventory patterns
- **Windows Extension**: Platform-specific adaptations within shared infrastructure
- **Cost Management**: Complete lifecycle automation to eliminate ongoing costs
- **Flexibility**: Both Linux and Windows platforms on same provider

#### Windows-Specific Implementation (AWS)
**Authentication Method**: SSH key-based authentication successfully implemented
```yaml
# Windows connection configuration (SSH implemented)
ansible_connection: ssh
ansible_user: Administrator
ansible_port: 22
ansible_shell_type: powershell
ansible_shell_executable: powershell
```

**Package Management**: Chocolatey successfully implemented
```yaml
# Windows package installation pattern (implemented)
- name: Install Chocolatey package manager
  win_shell: |
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  args:
    creates: C:\ProgramData\chocolatey\bin\choco.exe
```

### Implementation Specifications Across Providers

#### Hetzner Cloud Linux Technical Specifications
- **Instance**: cx22 (2 vCPU, 4GB RAM, 40GB SSD) in Helsinki
- **OS**: Ubuntu 24.04 LTS with full GNOME desktop environment
- **Authentication**: root → gandalf user with SSH key authentication
- **Cost**: ~$4/month with predictable EU-based pricing
- **Features**: Complete desktop applications, automated backup/restore system

#### AWS Linux Technical Specifications  
- **Instance**: t3.micro/small in eu-north-1
- **OS**: Ubuntu 24.04 LTS with minimal server setup
- **Authentication**: ubuntu → gandalf user with SSH key authentication
- **Cost**: ~$8-10/month with on-demand usage patterns
- **Features**: Basic development tools, dynamic inventory foundation

#### AWS Windows Technical Specifications
- **Instance**: t3.large (4 vCPU, 8GB RAM, 50GB GP3) in eu-north-1
- **OS**: Windows Server 2025 with Desktop Experience
- **Authentication**: Administrator with SSH key authentication via icacls
- **Cost**: ~$60/month with on-demand usage reducing actual costs
- **Features**: SSH + RDP access, Chocolatey package management, application framework

## Component Relationships

### Implemented Windows Server Provisioning Flow
```mermaid
graph TD
    A[provision-aws-windows.yml] --> B[provisioners/aws-windows.yml]
    B --> C[Windows Server 2025 AMI]
    B --> D[t3.large instance]
    B --> E[ansible-sg Security Group]
    B --> F[SSH Key Setup via PowerShell]
    B --> G[meta: refresh_inventory]
    A --> H[configure-aws-windows.yml]
    H --> I[Chocolatey Installation]
    H --> J[RDP Performance Optimization]
```

### Implemented AWS Infrastructure Reuse
**Shared Components** (successfully reused from Linux):
- AWS credentials and authentication (working across platforms)
- Dynamic inventory plugin (`amazon.aws.aws_ec2`) (supports both platforms)
- Instance tagging and naming conventions (consistent across platforms)
- Security group patterns (extended for Windows ports)

**Windows-Specific Components** (successfully implemented):
- Windows Server 2025 AMI selection (ami-01998fe5b868df6e3)
- SSH (22) and RDP (3389) in shared security group
- OpenSSH Server configuration via PowerShell user data
- Larger instance types (t3.large for optimal performance)
- Windows-specific configuration with Chocolatey and RDP optimization

## Critical Implementation Paths

### Implemented Windows Server Provisioning Pattern
```yaml
# provisioners/aws-windows.yml (implemented and working)
- name: Launch Windows Server EC2 instance
  amazon.aws.ec2_instance:
    name: "{{ aws_instance_name }}"
    image_id: "{{ aws_ami_id }}"
    instance_type: "{{ aws_instance_type }}"
    key_name: "{{ aws_ssh_key_name }}"
    security_groups:
      - "{{ aws_security_group_name }}"
    user_data: |
      <powershell>
      # Set Administrator password
      $Password = ConvertTo-SecureString "{{ windows_admin_password }}" -AsPlainText -Force
      $UserAccount = Get-LocalUser -Name "Administrator"
      $UserAccount | Set-LocalUser -Password $Password

      # Enable RDP and OpenSSH Server
      Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -name "fDenyTSConnections" -value 0
      Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
      Set-Service -Name sshd -StartupType 'Automatic'
      Start-Service sshd

      # Configure SSH key authentication for Administrator
      $AdminSSHDir = "C:\ProgramData\ssh"
      $AdminAuthorizedKeysFile = "$AdminSSHDir\administrators_authorized_keys"
      $PublicKey = "{{ my_ssh_public_key }}"
      Set-Content -Path "$AdminAuthorizedKeysFile" -Value $PublicKey
      
      # Set correct permissions with icacls
      icacls $AdminSSHDir /inheritance:r
      icacls $AdminSSHDir /grant:r "Administrator:(OI)(CI)F"
      icacls $AdminSSHDir /grant:r "SYSTEM:(OI)(CI)F"
      icacls "$AdminAuthorizedKeysFile" /inheritance:r
      icacls "$AdminAuthorizedKeysFile" /grant:r "Administrator:F"
      icacls "$AdminAuthorizedKeysFile" /grant:r "SYSTEM:F"
      </powershell>
```

### Implemented Windows Configuration Pattern
```yaml
# configure-aws-windows.yml (implemented and working)
- name: Configure RDP settings for better performance
  win_shell: |
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "ColorDepth" -Value 4 -Type DWord
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "fDisableClip" -Value 0 -Type DWord

- name: Install Chocolatey package manager
  win_shell: |
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  args:
    creates: C:\ProgramData\chocolatey\bin\choco.exe
```

## Design Principles

### Achieved Windows Server Adaptation Principles
- **Consistency**: Same command patterns as Linux implementation ✅ ACHIEVED
- **Reuse**: Leveraged existing AWS infrastructure patterns ✅ ACHIEVED
- **Simplicity**: Minimal Windows-specific configuration ✅ ACHIEVED
- **Cost Awareness**: Optimized for intermittent usage patterns ✅ ACHIEVED

### Implemented Security Model for Windows
- **SSH Access**: Restricted to user's IP address only (port 22) ✅ IMPLEMENTED
- **RDP Access**: Restricted to user's IP address only (port 3389) ✅ IMPLEMENTED
- **Windows Firewall**: Configured for minimal exposure via PowerShell ✅ IMPLEMENTED
- **User Authentication**: Administrator account with SSH key authentication ✅ IMPLEMENTED
- **Credential Management**: SSH keys and Windows passwords via Ansible Vault ✅ IMPLEMENTED

### Achieved Cost Optimization Strategy
- **On-Demand Usage**: Complete provision → use → destroy lifecycle ✅ IMPLEMENTED
- **Instance Sizing**: t3.large for optimal Windows Server GUI performance ✅ IMPLEMENTED
- **Storage Optimization**: 50GB GP3 for cost-effectiveness ✅ IMPLEMENTED
- **Usage Patterns**: On-demand sessions significantly reduce costs ✅ ACHIEVED

## AI Agent Safety Architecture ⚠️ CRITICAL IMPLEMENTATION REQUIRED

### Command Restriction System Requirements
**Core Challenge**: Claude Code creates independent shell sessions for each command execution, bypassing traditional bash function-based restrictions.

**Required Architecture Patterns**:
```
AI Agent Safety System:
├── Sub-Shell Resistant Blocking:
│   ├── Option A: Wrapper Scripts with PATH manipulation
│   ├── Option B: Environment Detection with persistent markers
│   ├── Option C: direnv Integration with automatic loading
│   └── Option D: Shell Initialization with BASH_ENV/project .bashrc
├── Comprehensive Command Coverage:
│   ├── Infrastructure: ansible*, vagrant, docker, tart
│   ├── Cloud Providers: aws, hcloud
│   └── Project-Scoped: Only within ansible-all-my-things directory
└── Verification & Status:
    ├── Cross-Session Status Checking
    ├── Clear Error Messages
    └── User Override Capability
```

**Implementation Success Criteria**:
- **Persistent Blocking**: Commands blocked across separate Claude tool calls
- **Status Verification**: Reliable `--status` command across sessions
- **Project Scope**: Restrictions only apply in project directory
- **User Override**: Normal user command execution unaffected

**Technical Constraints**:
- Must work with Claude Code's independent bash session architecture
- No modification of Claude Code tool behavior allowed
- Must be maintainable and easily debuggable
- Should not impact normal development workflow

## Extension Points

### Enhanced Inventory System (Completed Implementation)
**Completed Enhancement Features:**
1. **Dual Keyed Groups**: Cross-provider platform groups (@linux, @windows) plus provider-specific groups (@aws_ec2_linux, @hcloud_linux)
2. **Improved Tag Semantics**: Changed from `ansible_group` to `platform` tags for clearer automation intent
3. **Enhanced Variable Structure**: Four-tier precedence (all → platform → provider → provider_platform)
4. **Group Vars Reorganization**: Provider directories renamed (aws → aws_ec2) and provider-platform directories added
5. **Provisioner Updates**: All provisioners updated to use new platform tag semantics
6. **Backward Compatibility**: Existing playbooks continue working while new targeting capabilities available

**Achieved Group Structure:**
```
@all:
  |--@aws_ec2:              # Provider group (automatic)
  |  |--moria
  |  |--rivendell
  |--@aws_ec2_linux:        # Provider-platform group (enhanced)
  |  |--rivendell
  |--@aws_ec2_windows:      # Provider-platform group (enhanced)
  |  |--moria
  |--@hcloud:               # Provider group (automatic)
  |  |--hobbiton
  |--@hcloud_linux:         # Provider-platform group (enhanced)
  |  |--hobbiton
  |--@linux:                # Cross-provider platform group (maintained)
  |  |--hobbiton
  |  |--rivendell
  |--@windows:              # Cross-provider platform group (maintained)
  |  |--moria
```

**Enhanced Variable Precedence Strategy:**
- `all` → `platform` (linux/windows) → `provider` (aws_ec2/hcloud) → `provider_platform` (aws_ec2_linux, hcloud_linux, aws_ec2_windows)
- Handles admin user differences: AWS Linux (ubuntu), Hetzner Linux (root), AWS Windows (Administrator)
- Enhanced granularity for provider-specific automation while maintaining cross-provider capabilities

### Windows Application Support (Framework Ready)
**Established Pattern for Additional Applications**:
1. Use existing Windows Server infrastructure (provisioners/aws-windows.yml)
2. Extend configure-aws-windows.yml with additional Chocolatey packages
3. Leverage established SSH and RDP access patterns
4. Test via SSH for command-line functionality and RDP for desktop applications

### Future Windows Development Environment
**Available Extensions**:
- Visual Studio installation via Chocolatey
- .NET development environment setup
- Windows-specific development tools (Git, Docker Desktop, etc.)
- Multiple Windows-only applications per instance

## Provider Differences Reference (Current Implementation)

| Aspect | AWS Linux (Production) | AWS Windows (Production) | Hetzner Linux (Production) |
|--------|-----------------------|--------------------------|----------------------------|
| Connection | SSH (port 22) | SSH (port 22) + RDP (port 3389) | SSH (port 22) |
| Default User | `ubuntu` | `Administrator` | `root` |
| Package Manager | APT | Chocolatey | APT |
| Instance Type | t3.micro/small | t3.large | cx22 |
| Storage | 20GB | 50GB | 40GB SSD |
| Desktop Access | SSH + X11 forwarding | SSH (command) + RDP (desktop) | SSH + full GNOME |
| Cost (monthly) | ~$8-10 | ~$60 (optimizable to ~$15) | ~$4 |
| Authentication | SSH keys | SSH keys + RDP | SSH keys |
| Provisioning Time | ~3-5 minutes | ~5 minutes | ~10-15 minutes |
| Inventory Groups | @aws_ec2, @aws_ec2_linux, @linux | @aws_ec2, @aws_ec2_windows, @windows | @hcloud, @hcloud_linux, @linux |

## Windows-Specific Technical Implementation

### Implemented Ansible Collections
```yaml
# Successfully implemented collections
collections:
  - name: ansible.windows  # ✅ WORKING
  - name: community.windows  # ✅ AVAILABLE
  - name: amazon.aws  # ✅ WORKING
```

### Achieved Windows Server Configuration
- **OpenSSH Server**: ✅ Enabled SSH via PowerShell user data
- **Desktop Experience**: ✅ Windows Server 2025 with GUI
- **PowerShell Integration**: ✅ PowerShell as default SSH shell
- **Windows Firewall**: ✅ Configured for SSH and RDP access
- **SSH Key Authentication**: ✅ Administrator access with icacls permissions

### Implemented RDP Optimization
- **Performance Settings**: ✅ 32-bit color depth configured
- **Display Configuration**: ✅ Optimized for desktop application responsiveness
- **Clipboard Sharing**: ✅ Enabled clipboard between host and Windows Server
- **Security**: ✅ IP-restricted RDP access from user's public IP only
