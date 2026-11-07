<!-- SPDX-License-Identifier: MIT-0 -->

# shellcheck

Ansible role that installs [ShellCheck](https://www.shellcheck.net), the
static analysis tool for shell scripts, on Ubuntu Linux via apt.

See [DESIGN.md](DESIGN.md) for why the role uses the distribution package.

## Boundary

The role installs the `shellcheck` package system-wide. It does not configure
ShellCheck (no `.shellcheckrc`), and does not hook it into editors, git hooks
or CI.

## Requirements

- Ansible 2.19+
- Ubuntu Linux target host

## Role Variables

None.

## Dependencies

None. See `meta/main.yml`.

## Example Playbook

```yaml
- hosts: all
  become: true
  roles:
    - role: shellcheck
```

## License

MIT-0
