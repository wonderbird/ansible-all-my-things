# System Patterns — feat.podman.role

## Role Structure

Follows the project-wide pattern for Linux roles:

```text
roles/podman/
├── defaults/
│   └── main.yml        # four role variables + desktop_user_names default
├── meta/
│   └── main.yml        # galaxy_info, MIT-0 licence, Ubuntu platform
├── tasks/
│   └── main.yml        # four tasks (see below)
├── DESIGN.md           # non-obvious design decisions (FR-012)
└── README.md           # variables table, example playbook, licence
```

## Task Flow

```text
apt install podman
    │
    ▼
lineinfile /etc/subuid  ← loop over desktop_user_names
    │
    ▼
lineinfile /etc/subgid  ← loop over desktop_user_names
    │
    ▼
podman system migrate   ← loop over desktop_user_names
                          changed_when: false
```

## Key Design Decisions

### D1 — Package source: Ubuntu apt

Podman is installed via `ansible.builtin.apt` (`state: present`, not
`latest`). No PPA needed — Ubuntu 22.04+ ships Podman 3.4+; Ubuntu 24.04+
ships Podman 4.x, which supports `--mount=type=cache` natively.

### D2 — subuid/subgid via lineinfile (not usermod)

`ansible.builtin.user` has no subuid/subgid support in any released Ansible
version. `usermod --add-subuids` is non-idempotent (duplicates on re-run).
`ansible.builtin.lineinfile` with `regexp: '^{{ item }}:'` is fully
idempotent and declarative — it enforces the exact `username:start:count`
line, replacing any differing value in-place.

### D3 — podman system migrate: unconditional with changed_when: false

Runs on every playbook execution. Always reports `ok` (never `changed`),
making it safe to re-run. A handler would suppress migration on idempotency
re-runs where no `changed` signal is emitted. Avoids introducing a
`handlers/` directory for a single side-effect-free command.

### D4 — Shared subuid/subgid start value (100000) for all users

Single-person workstation use case: YAGNI. All users in `desktop_user_names`
share start=100000, count=65536. Callers on multi-user servers must override
`podman_subuid_start` / `podman_subgid_start` per user via `host_vars` or
`group_vars` if non-overlapping ranges are required.

### D5 — No docker shim, no registries.conf, no linger

- No `podman-docker`: callers use `podman build` / `podman run` directly
- No `registries.conf`: all image refs are fully qualified (`docker.io/…`)
- No `loginctl enable-linger`: interactive use only, not container services

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `podman_subuid_start` | `100000` | First sub-UID allocated per user |
| `podman_subuid_count` | `65536` | Number of sub-UIDs allocated |
| `podman_subgid_start` | `100000` | First sub-GID allocated per user |
| `podman_subgid_count` | `65536` | Number of sub-GIDs allocated |
| `desktop_user_names` | `[]` | Users to configure for rootless Podman |

## Idempotency Mechanisms

| Task | Guard |
| --- | --- |
| `apt install podman` | `state: present` |
| `lineinfile /etc/subuid` | `regexp: '^{{ item }}:'` |
| `lineinfile /etc/subgid` | `regexp: '^{{ item }}:'` |
| `podman system migrate` | `changed_when: false` |

## Playbook Integration

The role is the first entry in `configure-linux-roles.yml`:

```yaml
roles:
  - role: podman
```

`become: true` is set at play level — the role does not set it per-task.
