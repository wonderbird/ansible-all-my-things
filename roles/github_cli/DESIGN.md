# github_cli — Design Notes

## Installation method

GitHub CLI is installed via the official apt repository at `cli.github.com`,
not from a binary tarball. This matches the installation method recommended by
the GitHub CLI team and ensures `apt` handles upgrades and dependency
management.

## GPG key

The keyring is downloaded with `ansible.builtin.get_url` to
`/usr/share/keyrings/githubcli-archive-keyring.gpg`. The `apt_key` module is
intentionally avoided: it writes to the deprecated `/etc/apt/trusted.gpg`
keyring and is not idempotent under all Ansible versions. The `signed-by=`
field in the apt source line pins the keyring file, following Debian's
recommended practice for third-party repositories.

## Version pinning

`github_cli_version` pins the installed package to a specific release. The
variable stores the git tag format (`v2.95.0`); the `v` prefix is stripped at
install time via `regex_replace`. Version updates are applied automatically by
`playbooks/update-versions/perform-updates.yml`.

## Architecture support

AMD64 and ARM64 are supported. `ansible_facts['architecture']` is mapped to
the Debian architecture name via `github_cli_arch_map`. An `assert` task fails
loudly (Principle XII) if the host architecture is not in the map.

## Authentication

`gh auth login` is intentionally not automated. Automation of OAuth device
flows or token injection is out of scope for this role (Principle IV: YAGNI).
The README documents the manual post-install step.
