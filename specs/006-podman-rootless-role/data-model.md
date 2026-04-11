# Data Model: Rootless Podman Ansible Role

**Feature**: `006-podman-rootless-role`
**Date**: 2026-04-11

## Role Variables

These are the entities (variables) the role operates on. All defaults are
declared in `roles/podman/defaults/main.yml`.

### Input Variables

| Variable | Type | Default | Source | Description |
| --- | --- | --- | --- | --- |
| `desktop_user_names` | list of strings | (none — caller must supply) | playbook `vars:` | Usernames of all desktop users to configure for rootless Podman. Defined by the calling playbook as `"{{ desktop_users \| map(attribute='name') \| list }}"`. |
| `podman_subuid_start` | integer | `100000` | `defaults/main.yml` | First sub-UID in the range allocated to each desktop user. |
| `podman_subuid_count` | integer | `65536` | `defaults/main.yml` | Number of sub-UIDs allocated to each desktop user. |
| `podman_subgid_start` | integer | `100000` | `defaults/main.yml` | First sub-GID in the range allocated to each desktop user. |
| `podman_subgid_count` | integer | `65536` | `defaults/main.yml` | Number of sub-GIDs allocated to each desktop user. |

### Validation Rules

- `desktop_user_names` MUST be defined by the caller. An empty list (`[]`) is
  valid: the install task runs but per-user loops are skipped.
- Each entry in `desktop_user_names` MUST correspond to an existing system
  user. The role does not create users (out of scope).
- `podman_subuid_start` and `podman_subuid_count` MUST be positive integers.
  No runtime validation is added (YAGNI for a single-person project).

## System File Entities

These are the files the role reads from or writes to on the target host.

| File | Module | Operation | Idempotency Mechanism |
| --- | --- | --- | --- |
| `/etc/subuid` | `ansible.builtin.lineinfile` | Ensure line `username:start:count` present | `regexp: '^{{ item }}:'` matches existing line; no duplicate created |
| `/etc/subgid` | `ansible.builtin.lineinfile` | Ensure line `username:start:count` present | `regexp: '^{{ item }}:'` matches existing line; no duplicate created |

## Task Flow

```text
1. Install podman (apt)
   └─ ansible.builtin.apt: name=podman state=present

2. For each user in desktop_user_names:
   ├─ Ensure subuid entry (lineinfile on /etc/subuid)
   ├─ Ensure subgid entry (lineinfile on /etc/subgid)
   └─ Run podman system migrate (command, become_user=item, changed_when=false)
```

## State Transitions

| System State Before | Task | System State After |
| --- | --- | --- |
| Podman not installed | apt install podman | Podman binary present at `/usr/bin/podman` |
| No subuid entry for user | lineinfile /etc/subuid | Entry `user:100000:65536` present |
| No subgid entry for user | lineinfile /etc/subgid | Entry `user:100000:65536` present |
| subuid/subgid entries exist | lineinfile (regexp matches) | No change; file unchanged |
| User namespace mapping stale | podman system migrate | Mapping updated; `changed_when: false` |
| All already configured | all tasks | All tasks report `ok`; zero `changed` |
