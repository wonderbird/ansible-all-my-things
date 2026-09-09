<!-- SPDX-License-Identifier: MIT-0 -->

# git

Ansible role that installs the git version control tool on Ubuntu Linux via
apt.

## Requirements

- Ansible 2.19+
- Ubuntu 24.04 target host

## Role Variables

None.

## Dependencies

None. See `meta/main.yml` for details.

## Example Playbook

```yaml
- hosts: all
  roles:
    - role: git
```

## What This Role Does

Installs the `git` package via apt, unpinned (whatever version the
configured apt repositories currently serve).

Several other roles in this repository depend on this role instead of
installing `git` themselves — see `DESIGN.md` for why.
