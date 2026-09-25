<!-- SPDX-License-Identifier: MIT-0 -->
# nerd_font

Ansible role that installs the Hack Nerd Font into each login user's personal
font directory on Linux and rebuilds that user's font cache.

## Boundary

The role downloads the pinned `Hack.zip` release, extracts it into
`~/.local/share/fonts` for every user in `login_user_names`, and runs
`fc-cache` as that user. It does not install any other Nerd Font family, does
not install fonts system-wide, and does not configure any terminal,
editor or desktop setting to use the font.

## Requirements

- Ansible 2.19+
- Linux with `fc-cache` (fontconfig) available on the target host
- Internet access to `github.com` from the target host
- Each name in `login_user_names` already exists as a local user with a home
  directory under `/home`

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to install the font for. Must contain at least one name; the role fails loudly if it is undefined or empty. |
| `nerd_font_version` | `"v3.5.1"` | Pinned nerd-fonts release tag (`v`-prefixed). One universal `Hack.zip` serves every architecture. |

The pinned version is updated by
`playbooks/update-versions/perform-updates.yml`.

## Dependencies

None. See `meta/main.yml`.

## Example Playbook

```yaml
- hosts: desktop
  become: true
  roles:
    - role: nerd_font
      vars:
        login_user_names:
          - alice
          - bob
```

## License

MIT-0
