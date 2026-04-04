# Data Model: Flutter Ansible Role

**Branch**: `004-flutter-role` | **Date**: 2026-04-04

## Role Variables

### `defaults/main.yml`

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `flutter_version` | string | `"3.41.6"` | Pinned Flutter stable release. Bump to trigger an upgrade. |
| `flutter_sha256` | string | `"503b3e6b7d352fca5d21b6474eca95ad544d8fc3b053782eab63a360c7fc7569"` | SHA-256 of the `.tar.xz` archive for `flutter_version`. Must be updated when `flutter_version` changes. |

### Inventory Variables (consumed, not defined by this role)

| Variable | Source | Description |
|----------|--------|-------------|
| `desktop_user_names` | `group_vars/` or `host_vars/` | List of Linux usernames for whom the Flutter SDK is installed and PATH is configured. |

## Derived Values (computed at runtime)

| Derived value | Expression |
|---------------|------------|
| Archive URL | `https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_{{ flutter_version }}-stable.tar.xz` |
| Archive dest (tmp) | `/tmp/flutter_linux_{{ flutter_version }}-stable.tar.xz` |
| SDK root per user | `/home/{{ item }}/flutter` |
| Version file per user | `/home/{{ item }}/flutter/version` |
| bashrc PATH block | `export PATH="$HOME/flutter/bin:$PATH"` |
| bashrc marker | `# {mark} ANSIBLE MANAGED BLOCK - Flutter PATH` |

## Idempotency State Machine

```text
START
  |
  v
Read /home/{{ item }}/flutter/version
  |
  +-- file absent OR version != flutter_version
  |       |
  |       v
  |   Download archive to /tmp  (get_url + sha256 checksum)
  |       |
  |       v
  |   Remove old /home/{{ item }}/flutter  (file: state=absent)
  |       |
  |       v
  |   Extract archive to /home/{{ item }}/  (unarchive)
  |
  +-- version == flutter_version
          |
          v
        SKIP download + extract

Always runs (idempotent by module semantics):
  - apt: install prerequisites
  - systemd: daemon_reload
  - blockinfile: PATH in ~/.bashrc
```

## Task Sequence

1. Install apt prerequisites (`clang`, `cmake`, `ninja-build`,
   `pkg-config`, `libgtk-3-dev`, `mesa-utils`) — system-wide, once.
2. Run `systemctl daemon-reload` via `ansible.builtin.systemd`.
3. **Per user** (`loop: "{{ desktop_user_names }}"`):
   a. Stat `/home/{{ item }}/flutter/version`.
   b. Slurp version file content (when file exists).
   c. Set `flutter_installed_version` fact.
   d. Download archive to `/tmp` when version mismatch (with SHA-256
      checksum).
   e. Remove old SDK directory when version mismatch.
   f. Extract archive to `/home/{{ item }}/` when version mismatch;
      `become_user: "{{ item }}"`.
   g. `blockinfile` to add `$HOME/flutter/bin` to `~/.bashrc`;
      `become_user: "{{ item }}"`.

## Validation Rules

- `flutter_version` MUST be a semantic version string (e.g. `3.41.6`).
- `flutter_sha256` MUST be a 64-character hex string matching the
  archive for `flutter_version`.
- `desktop_user_names` MUST be defined before the role runs; the role
  does not validate its presence.

## File Ownership

All per-user files under `/home/{{ item }}/flutter` are owned by
`{{ item }}:{{ item }}` because `become_user: "{{ item }}"` is used for
the `unarchive` task.
