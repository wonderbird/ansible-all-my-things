# Tech Context — feat.podman.role

## Technologies Used

- **Ansible 2.19+** — automation engine; all modules use `ansible.builtin.*`
  FQCNs; no Galaxy collections required for this role
- **Podman 4.x** — rootless container runtime; installed from Ubuntu apt
- **Ubuntu 22.04 LTS / 24.04 LTS** — primary target OS (24.04 ships
  Podman 4.x with native `--mount=type=cache` support)
- **buildah** (bundled with Podman) — OCI build backend; handles
  `RUN --mount=type=cache` without external BuildKit

## Development Setup

### Local Test VM

- Vagrant + Docker (Linux hosts) or Vagrant + Tart (macOS ARM64 hosts)
- SSH target configured for `vagrant` user
- `configure-linux-roles.yml` used to apply the role in isolation

### Test Procedure (from CONTRIBUTING.md)

1. Isolate the role: ensure only `podman` is active in
   `configure-linux-roles.yml`
2. Run: `ansible-playbook configure-linux-roles.yml -i inventories/local`
3. Verify all four acceptance criteria (see `specs/006-podman-rootless-role/
   quickstart.md`)

## Spec Artifacts

All located at `specs/006-podman-rootless-role/`:

| File | Purpose |
| --- | --- |
| `spec.md` | Functional requirements, user stories, acceptance criteria |
| `plan.md` | Technical context, constitution check, source layout |
| `tasks.md` | 21 implementation tasks (T001–T021) |
| `research.md` | 6 resolved design decisions |
| `data-model.md` | Role variables, system file entities, task-flow diagram |
| `quickstart.md` | Local VM test procedure, acceptance test checklist |

## Constraints

- `become: true` must be set at play level (role does not set it per-task)
- `desktop_user_names` must contain valid system users; the role does not
  validate user existence (YAGNI) — an orphaned `/etc/subuid` entry is
  the failure mode for non-existent users
- Ansible Vault: not relevant for this role (no secrets)
- Architecture: the Ubuntu `podman` apt package supports AMD64 and ARM64
  natively — no architecture branching needed

## File Conventions

- YAML files: `#SPDX-License-Identifier: MIT-0` (no space after `#`)
- Markdown files: ATX headings, blank lines around lists, no trailing
  whitespace, one trailing newline, max 80 chars per line (MD013)
