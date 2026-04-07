# Tech Context: feat.flutter.role

## Key Files

| File | Purpose |
| --- | --- |
| `roles/flutter/defaults/main.yml` | `flutter_version: "3.41.6"`, `flutter_sha256` |
| `roles/flutter/tasks/main.yml` | All role tasks |
| `roles/flutter/meta/main.yml` | `dependencies: []` |
| `roles/flutter/README.md` | Prerequisites, variables |
| `roles/flutter/DESIGN.md` | Non-obvious decisions |
| `configure-linux-roles.yml` | Role entry with ARM64 tag |
| `specs/004-flutter-role/spec.md` | Requirements (Status: Clarified) |
| `specs/004-flutter-role/tasks.md` | 22 tasks, all marked [X] |
| `specs/004-flutter-role/plan.md` | Technical plan |
| `specs/004-flutter-role/research.md` | Resolved open questions |
| `specs/004-flutter-role/data-model.md` | Variables, task sequence |
| `specs/004-flutter-role/quickstart.md` | Upgrade procedure |

## Flutter SDK

- Version: `3.41.6` (pinned in `defaults/main.yml`)
- SHA-256: `503b3e6b7d352fca5d21b6474eca95ad544d8fc3b053782eab63a360c7fc7569`
- Download URL pattern:
  `https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_{{ flutter_version }}-stable.tar.xz`
- Checksum manifest: `https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json`
- Install path: `/home/{{ item }}/flutter/` per user in `desktop_user_names`
- Version file: `/home/{{ item }}/flutter/version` (used for idempotency guard)

## Apt Dependencies (proven from manual installs)

```
clang cmake ninja-build pkg-config libgtk-3-dev mesa-utils
```

Followed by `systemctl daemon-reload` (`changed_when: false`).

## Target Host

- Name: `hobbiton`
- Provider: Hetzner Cloud
- Architecture: AMD64
- OS: Ubuntu/Debian-based Linux
- Variable `desktop_user_names` defined in `group_vars/` or `host_vars/`

## Tool Stack

- Ansible 2.19+ with `community.general` collection
- `speckit` skill suite for spec-driven development
- `markdownlint` for all `.md` files
- Git conventional commits (`feat:`, `fix:`, `docs:`)

## Commit History (this branch)

```
eecc8ef feat: provision Flutter SDK for Chrome/web development
e8e9e50 docs: flutter role specification, plan, and task breakdown
81b81a8 fix: home-folder-files restore failed when .envrc is absent
```

## Upgrading Flutter Version

1. Find new stable version + SHA-256 in the checksum manifest URL above
2. Update `flutter_version` and `flutter_sha256` in `defaults/main.yml`
3. Run playbook — version mismatch triggers remove + re-extract per user
