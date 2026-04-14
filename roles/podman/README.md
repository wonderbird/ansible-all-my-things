# Role: podman

Installs Podman from the Ubuntu distribution repository and configures
rootless container operation for every user listed in `desktop_user_names`.

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `desktop_user_names` | `[]` | Users to configure for rootless Podman. Defaults to an empty list: Podman is installed system-wide but per-user rootless configuration is skipped. |
| `podman_subuid_start` | `100000` | First UID in the subordinate UID range |
| `podman_subuid_count` | `65536` | Number of UIDs in the subordinate UID range |
| `podman_subgid_start` | `100000` | First GID in the subordinate GID range |
| `podman_subgid_count` | `65536` | Number of GIDs in the subordinate GID range |

## Example Playbook

```yaml
- name: Configure desktop
  hosts: linux
  become: true

  vars:
    desktop_user_names:
      - alice
      - bob

  roles:
    - podman
```

## Requirements

- Ubuntu 22.04 LTS (Jammy) or later.
- Ansible 2.19+.
- The calling play must set `become: true` at play level.

## Licence

SPDX-License-Identifier: MIT-0
