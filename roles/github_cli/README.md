# github_cli

Installs [GitHub CLI](https://cli.github.com/) (`gh`) from the official apt
repository at `cli.github.com`.

## Requirements

None beyond Ansible itself. The role installs its own apt repository and GPG
keyring.

## Role variables

| Variable | Default | Description |
| --- | --- | --- |
| `github_cli_version` | `"v2.95.0"` | Version to install (git tag format, e.g. `"v2.95.0"`). |
| `github_cli_arch_map` | `{x86_64: amd64, aarch64: arm64}` | Maps kernel architecture names to Debian package architecture names. |

## Dependencies

None.

## Example playbook

```yaml
- hosts: all
  become: true
  roles:
    - role: github_cli
```

## Post-install

Authentication is not automated. After installation, run:

```shell
gh auth login
```

## Molecule testing

```shell
cd roles/github_cli
molecule test
```

## License

MIT-0
