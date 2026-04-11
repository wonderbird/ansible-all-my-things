# Quickstart: Rootless Podman Ansible Role

**Feature**: `006-podman-rootless-role`
**Date**: 2026-04-11

## Prerequisites

- Ubuntu 22.04 LTS or later target host (AMD64 or ARM64).
- Ansible 2.19+ on the control node.
- SSH access to the target with sudo privileges.
- `desktop_user_names` list populated (via the playbook `vars:` block or
  inventory).

## Local Test (Vagrant + Docker VM)

Follow the standard CONTRIBUTING.md procedure:

1. Edit `configure-linux-roles.yml` and set the `roles:` list to only
   `podman` (comment out all other roles).
2. Run the playbook against the local VM:

   ```bash
   ansible-playbook configure-linux-roles.yml -i inventories/local
   ```

3. Verify idempotency — run again and confirm zero changed tasks:

   ```bash
   ansible-playbook configure-linux-roles.yml -i inventories/local
   ```

4. Log in as one of the target users and verify rootless Podman works:

   ```bash
   podman --version
   podman build -t devcontainer .devcontainer/
   podman run --rm devcontainer ansible --version
   ```

## Adding the Role to configure-linux-roles.yml

Once local testing passes, add `podman` to the `roles:` list in
`configure-linux-roles.yml`:

```yaml
roles:
  - podman
  - claude_code
  # ... other roles
```

## Role Variables Reference

| Variable | Default | Override in |
| --- | --- | --- |
| `podman_subuid_start` | `100000` | `group_vars/`, `host_vars/`, or playbook `vars:` |
| `podman_subuid_count` | `65536` | same |
| `podman_subgid_start` | `100000` | same |
| `podman_subgid_count` | `65536` | same |

`desktop_user_names` has no default and must be supplied by the caller.

## Acceptance Test Checklist

- [ ] `podman --version` succeeds for every user in `desktop_user_names`.
- [ ] `/etc/subuid` contains a valid entry for every user.
- [ ] `/etc/subgid` contains a valid entry for every user.
- [ ] `podman build -t devcontainer .devcontainer/` succeeds as a listed user.
- [ ] `podman run --rm devcontainer ansible --version` prints a version string.
- [ ] Second playbook run reports zero changed tasks.
