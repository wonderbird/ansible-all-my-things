<!-- SPDX-License-Identifier: MIT-0 -->
# skill_manager

Ansible role that builds and installs the
[Skill Manager](https://github.com/omrikais/skill-manager) (`sm`) CLI — unified
skill management for Claude Code and Codex CLI — as a system-wide command at
`/usr/local/bin/sm` on Linux.

Upstream ships no release artefacts, so the role builds from source at a pinned
commit SHA (clone → `npm ci` → `npm run build` → prune dev dependencies).

See [DESIGN.md](DESIGN.md) for non-obvious decisions.

## Boundary

The role installs the `sm` binary only. It does not import, deploy, or sync any
skills, nor configure Claude Code / Codex directories — those are runtime `sm`
operations outside this role's scope.

## Requirements

- Ansible 2.19+
- Linux (x86_64 or aarch64)
- Node.js 20+ and npm, provisioned by the `nodejs` role (a declared dependency)
- Internet access to `github.com` and the npm registry from the target host

## Role Variables

All variables have safe defaults. None are required from the caller.

| Variable | Default | Description |
| --- | --- | --- |
| `skill_manager_repo` | `https://github.com/omrikais/skill-manager.git` | Upstream source repository. |
| `skill_manager_version` | *(see defaults)* | Pinned full 40-character git commit SHA. |
| `skill_manager_install_dir` | `/usr/local/lib/skill-manager` | Built project location (dist + runtime node_modules). |
| `skill_manager_bin_path` | `/usr/local/bin/sm` | Symlink to the `sm` entrypoint. |

`skill_manager_version` is updated by
`playbooks/update-versions/perform-updates.yml`.

## Dependencies

- `nodejs` (declared in `meta/main.yml`) — provides node/npm required to build.
- `git` (declared in `meta/main.yml`) — provides the `git` binary the
  pinned-commit clone task requires.

## Example Playbook

```yaml
- hosts: developers
  roles:
    - role: nodejs
    - role: skill_manager
```

## License

MIT-0
