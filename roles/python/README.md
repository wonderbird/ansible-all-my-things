<!-- SPDX-License-Identifier: MIT-0 -->

# python

Ansible role that installs Python and pipx on Ubuntu Linux via apt.

## Requirements

- Ansible 2.19+
- Ubuntu 24.04 target host
- Universe apt repository enabled (present by default on Ubuntu 24.04)

## Role Variables

None.

## Dependencies

None. See `meta/main.yml` for details.

## Example Playbook

```yaml
- hosts: all
  roles:
    - role: python
```

## What This Role Does

1. Installs `python3-full` — full Python 3 standard library including `venv` support.
2. Installs `pipx` — runs Python CLI tools in isolated environments.
