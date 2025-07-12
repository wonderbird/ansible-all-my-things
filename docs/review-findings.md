# Inventory Group Structure Improvement

## Overview
Replace `ansible_group` tags with `platform` tags to create both cross-provider groups (`@linux`, `@windows`) and provider-specific groups (`@aws_ec2_linux`, `@hcloud_linux`) automatically.

**Impact:** Low-risk additive change that maintains backward compatibility while adding provider-specific targeting capabilities.

## Expected Result
```
@all:
  |--@aws_ec2:
  |  |--moria
  |  |--rivendell
  |--@aws_ec2_linux:
  |  |--rivendell
  |--@aws_ec2_windows:
  |  |--moria
  |--@hcloud:
  |  |--hobbiton
  |--@hcloud_linux:
  |  |--hobbiton
  |--@linux:
  |  |--hobbiton
  |  |--rivendell
  |--@windows:
  |  |--moria
```

## Benefits
- **Backward compatible:** Existing `hosts: linux/windows` playbooks continue working
- **Enhanced targeting:** New provider-specific groups enable fine-grained control
- **Better semantics:** `platform: "linux"` is clearer than `ansible_group: "linux"`
- **Automatic management:** Groups created from instance metadata, no manual configuration

## Implementation

### 1. Update Provisioner Tags/Labels
**AWS provisioners (`provisioners/aws-linux.yml`, `provisioners/aws-windows.yml`):**
```yaml
# Change from:
tags:
  ansible_group: "linux"  # or "windows"
# To:
tags:
  platform: "linux"      # or "windows"
```

**Hetzner provisioner (`provisioners/hcloud.yml`):**
```yaml
# Change from:
labels:
  ansible_group: "linux"
# To:
labels:
  platform: "linux"
```

### 2. Update Inventory Configurations
**AWS inventory (`inventories/aws_ec2.yml`):**
```yaml
plugin: amazon.aws.aws_ec2
regions:
  - eu-north-1
keyed_groups:
  - key: tags.platform     # Creates @linux, @windows
    prefix: ""
    separator: ""
  - key: tags.platform     # Creates @aws_ec2_linux, @aws_ec2_windows
    prefix: "aws_ec2"
    separator: "_"
filters:
  instance-state-name: ["running", "pending", "stopping", "stopped"]
```

**Hetzner inventory (`inventories/hcloud.yml`):**
```yaml
plugin: hetzner.hcloud.hcloud
keyed_groups:
  - key: labels.platform   # Creates @linux
    prefix: ""
    separator: ""
  - key: labels.platform   # Creates @hcloud_linux
    prefix: "hcloud"
    separator: "_"
```

### 3. Rename Group Variables
```
inventories/group_vars/aws/ → inventories/group_vars/aws_ec2/
inventories/group_vars/aws_linux/ → inventories/group_vars/aws_ec2_linux/
inventories/group_vars/aws_windows/ → inventories/group_vars/aws_ec2_windows/
```

### 4. Update Group References
Search and replace in playbooks:
- `hosts: aws` → `hosts: aws_ec2`
- `hosts: aws_linux` → `hosts: aws_ec2_linux`
- `hosts: aws_windows` → `hosts: aws_ec2_windows`

## Technical Details
- Dual `keyed_groups` entries create both cross-provider and provider-specific groups
- Existing `@linux`/`@windows` groups preserved (11 playbooks require no changes)
- Provider groups (`@aws_ec2`, `@hcloud`) created automatically by plugins
- Migration is gradual - existing instances work until next provision cycle

## Testing
Follow test procedure in `test/test_unified_inventory.md` to verify group structure matches expected output.

## Migration Checklist
- [ ] Update 3 provisioner files (tag/label changes)
- [ ] Update 2 inventory files (keyed_groups configuration)  
- [ ] Rename 3 group_vars directories
- [ ] Update playbook group references (search/replace)
- [ ] Test inventory output matches expected structure