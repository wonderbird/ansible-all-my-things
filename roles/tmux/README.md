<!-- SPDX-License-Identifier: MIT-0 -->
# tmux

Ansible role that installs tmux and gitmux on Linux and configures both for
every login user, including the tmux plugins the shipped configuration
expects.

## Boundary

The role installs the distribution `tmux` package, installs the pinned
`gitmux` binary to `/usr/local/bin/gitmux`, clones the plugins listed in
`defaults/main.yml` into each user's `~/.tmux/plugins`, and deploys the
role's own `.tmux.conf` and `.gitmux.conf` to each user's home directory. It
overwrites those two files rather than merging into a user's existing
configuration, and it does not start, attach or reload any tmux server.

## Requirements

- Ansible 2.19+
- Debian or Ubuntu Linux on x86_64 or aarch64 (the role uses `apt`, and
  fails loudly on any other architecture)
- Internet access to `github.com` from the target host
- Each name in `login_user_names` already exists as a local user with a home
  directory under `/home`

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to configure tmux for. Must contain at least one name; the role fails loudly if it is undefined or empty. |
| `tmux_gitmux_version` | `"v0.11.5"` | Pinned gitmux release tag (`v`-prefixed). |
| `tmux_gitmux_arch_map` | *(see defaults)* | Maps `ansible_facts['architecture']` to the gitmux release architecture suffix. |
| `tmux_plugin_tpm_repo` | *(see defaults)* | Git URL of the tmux plugin manager. |
| `tmux_plugin_catppuccin_repo` | *(see defaults)* | Git URL of the catppuccin theme plugin. |
| `tmux_plugin_cpu_repo` | *(see defaults)* | Git URL of the tmux-cpu plugin. |

The pinned gitmux version is updated by
`playbooks/update-versions/perform-updates.yml`. The plugin repositories are
cloned at `HEAD` and are not version-pinned.

## Dependencies

The `git` role, declared in `meta/main.yml`: cloning the plugins requires a
`git` binary on the target host.

## Example Playbook

```yaml
- hosts: base
  become: true
  roles:
    - role: tmux
      vars:
        login_user_names:
          - alice
          - bob
```

## License

MIT-0
