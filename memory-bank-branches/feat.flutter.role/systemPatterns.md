# System Patterns: feat.flutter.role

## Role Structure Convention

All roles follow `roles/android_studio/` as the canonical template:

```
roles/flutter/
├── defaults/main.yml     # flutter_version, flutter_sha256
├── meta/main.yml         # galaxy_info, dependencies: []
├── tasks/main.yml        # all tasks in a single file
├── README.md             # prerequisites, variables table
└── DESIGN.md             # non-obvious implementation decisions
```

## ARM64 Skip Pattern

Tag `not-supported-on-vagrant-arm64` is applied ONLY at the role entry
level in `configure-linux-roles.yml`. Individual tasks inside the role
carry NO tags. This is the project-wide convention.

```yaml
# configure-linux-roles.yml
- role: flutter
  tags: not-supported-on-vagrant-arm64
```

CRITICAL: if role is ever invoked via `ansible.builtin.include_role`, the
caller MUST pass `apply: {tags: [not-supported-on-vagrant-arm64]}` or the
skip will not propagate to inner tasks.

## Idempotency Pattern (Stamp File Guard)

Flutter 3.x does NOT ship a `version` file at the SDK root. Use a stamp
file written by Ansible instead:

1. `stat` → `/home/{{ item }}/flutter/.ansible_installed_version` — exists?
2. `slurp` → read the version string if file exists
3. `set_fact` → build `flutter_installed_versions` dict keyed by username
4. `file: state=absent` → remove old SDK dir if version mismatches
5. `unarchive` → extract only when version mismatches
6. `copy` → write `flutter_version` to stamp file after extraction
7. `blockinfile` → PATH setup (always runs; idempotent via marker)

The `get_url` task runs unconditionally — `get_url` checksum idempotency
prevents re-download if the archive already exists in `/tmp/` with correct
checksum.

## PATH Setup Pattern

`blockinfile` in `~/.bashrc` per user, same as the `claude_code` role.
Unique marker: `# {mark} ANSIBLE MANAGED BLOCK - Flutter PATH`

```yaml
- name: Add Flutter to PATH in .bashrc
  ansible.builtin.blockinfile:
    path: "/home/{{ item }}/.bashrc"
    block: 'export PATH="$HOME/flutter/bin:$PATH"'
    marker: "# {mark} ANSIBLE MANAGED BLOCK - Flutter PATH"
    append_newline: true
    state: present
  become_user: "{{ item }}"
  loop: "{{ desktop_user_names }}"
```

## Checksum Pattern

Both `flutter_version` and `flutter_sha256` live in `defaults/main.yml`.
They must always be bumped together. Source of truth for checksums:
`https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json`

## Role Dependency Convention

No `meta/main.yml` dependencies in this project (all roles keep
`dependencies: []`). Prerequisites are documented in `README.md` only.
Reasons: meta deps are invisible to playbook readers, break tag filtering,
and are designed for redistributed roles — not single-playbook provisioners.

## Playbook Integration

`configure-linux.yml` → imports `configure-linux-roles.yml` → lists roles.
Role order in `configure-linux-roles.yml` is the authoritative dependency
contract. `flutter` must appear after `android_studio` and `google_chrome`.

## FQCN Convention

All Ansible module calls use fully qualified collection names
(e.g. `ansible.builtin.apt`, not `apt`). Enforced project-wide.

## `changed_when: false` on daemon-reload

`ansible.builtin.systemd` with `daemon_reload: true` always reports
`changed`. Add `changed_when: false` to preserve idempotency acceptance
criteria (zero changed tasks on second run).
