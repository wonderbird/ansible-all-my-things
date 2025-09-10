# Design Document

## Overview

This design adds Kiro IDE installation to the existing Ansible playbook infrastructure. The implementation follows the established patterns used for VSCode installation, integrating seamlessly with the current playbook structure while respecting host group exclusions for virtualized environments.

## Architecture

The Kiro installation will be integrated into the existing playbook flow by:

1. **New Playbook**: Create `playbooks/setup-kiro.yml` following the same pattern as `setup-desktop-apps.yml`
2. **New Task File**: Create `playbooks/tasks/setup-kiro.yml` following the same pattern as `setup-vscode.yml`
3. **Integration Point**: Add the new playbook to `configure-linux.yml` in the desktop apps section
4. **Host Filtering**: Use the existing `not-supported-on-vagrant-docker` tag pattern to exclude virtualized environments

### Installation Flow

```
configure-linux.yml
├── setup-basics.yml
├── setup-homebrew.yml
├── setup-nodejs-typescript.yml
├── setup-desktop.yml
├── setup-keyring.yml
├── setup-desktop-apps.yml
└── setup-kiro.yml (NEW)
```

## Components and Interfaces

### 1. Main Playbook (`playbooks/setup-kiro.yml`)

**Purpose**: Entry point for Kiro installation
**Target Hosts**: `linux` group
**Tags**: `not-supported-on-vagrant-docker`, `not-supported-on-arm64`
**Dependencies**: Requires desktop environment setup (runs after setup-desktop.yml)

**Interface**:
- Input: Host inventory with Linux systems
- Output: Kiro IDE installed and configured on compatible hosts
- Variables: Uses existing `desktop_users` and `my_ansible_user` variables
- Tag-based Exclusions: ARM64 and virtualized environments excluded via Ansible tags

### 2. Task Implementation (`playbooks/tasks/setup-kiro.yml`)

**Purpose**: Core installation logic
**Installation Method**: Official Kiro installation script or AppImage (x86_64 only)
**Idempotency**: Check existing installation before downloading
**Architecture Support**: x86_64 only (ARM64 excluded via tags)

**Key Functions**:
- Version detection and comparison
- Download and installation
- Desktop integration setup
- User configuration

### 3. Host Group Integration

**Target Hosts**: `linux` group (all Linux hosts)

**Exclusion Strategy**: Use Ansible tags to exclude incompatible environments
- Tag: `not-supported-on-vagrant-docker` (excludes Docker/Tart environments)
- Tag: `not-supported-on-arm64` (excludes ARM64 architecture)

**Included Hosts**:
- AWS EC2 Linux instances (x86_64 architecture)
- Hetzner Cloud Linux instances (x86_64 architecture)
- Any other physical Linux hosts (x86_64 architecture)

**Excluded Hosts**:
- Vagrant Docker instances (via tag exclusion)
- Vagrant Tart instances (via tag exclusion)
- ARM64 Linux systems (via tag exclusion)

## Data Models

### Installation State Tracking

```yaml
kiro_installation:
  current_version: "string|null"
  target_version: "latest"
  installation_path: "/usr/share/kiro"
  binary_link: "/usr/bin/kiro"
  desktop_integration: boolean
```

### User Configuration

```yaml
kiro_users:
  - name: "username"
    home_dir: "/home/username"
    config_applied: boolean
```

## Error Handling

### Installation Failures

1. **Network Issues**: Retry download with exponential backoff
2. **Permission Errors**: Clear error messages about sudo requirements
3. **Disk Space**: Check available space before download
4. **Unsupported Architecture**: ARM64 systems excluded via tags (no detection needed)
5. **Unsupported Environment**: Skip installation on Docker/Tart (handled by tags)

### Recovery Strategies

1. **Partial Installation**: Clean up incomplete installations before retry
2. **Version Conflicts**: Remove old versions before installing new ones
3. **Desktop Integration Failures**: Continue with installation even if desktop files fail

### Error Reporting

- Use Ansible's built-in error handling and reporting
- Provide actionable error messages
- Log installation attempts for debugging
- Fail gracefully without breaking the entire playbook run

## Testing Strategy

### Code Review and Validation

1. **Syntax Validation**: Review Ansible YAML syntax and task structure
2. **Logic Verification**: Validate idempotency checks and version detection logic
3. **Variable Usage**: Ensure proper use of existing variables and host groups
4. **Tag Implementation**: Verify correct tag usage for host exclusions

### User-Executed Testing

**Note**: All actual Ansible playbook execution, including testing commands like `ansible-playbook`, `vagrant`, and `tart`, must be performed by the user. The implementation will provide step-by-step instructions for testing, with clear explanations of intent and expected outcomes for each command.

### Testing Phases

1. **Syntax Testing**: User validates Ansible syntax with `ansible-playbook --syntax-check`
2. **Dry Run Testing**: User performs dry runs with `--check` flag to verify task logic
3. **Fresh Installation Testing**: User tests on clean systems without Kiro
4. **Idempotency Testing**: User runs playbook multiple times to ensure no changes on subsequent runs
5. **Environment Testing**: User tests on different host types (AWS EC2, Hetzner Cloud)
6. **Exclusion Testing**: User verifies Docker/Tart hosts are properly skipped

### Manual Verification (User-Performed)

1. **Desktop Integration**: User verifies Kiro appears in application menus
2. **File Associations**: User checks that Kiro can open relevant file types
3. **User Access**: User confirms all desktop users can launch Kiro
4. **Installation Paths**: User verifies files are installed to `/usr/share/kiro` with symlink at `/usr/bin/kiro`

## Implementation Approach

### Phase 1: Basic Installation
- Create task file with download and installation logic
- Implement version detection and idempotency
- Add basic error handling

### Phase 2: Desktop Integration
- Create desktop files and menu entries
- Set up file associations
- Configure for multiple users

### Phase 3: Playbook Integration
- Create main playbook file
- Add to configure-linux.yml
- Test host filtering and exclusions

### Phase 4: Testing and Refinement
- Test across different environments
- Refine error handling
- Optimize performance and reliability