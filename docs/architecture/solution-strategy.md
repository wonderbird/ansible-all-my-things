# Solution Strategy

> Arc42 Section 4 — <https://docs.arc42.org/section-4/>
>
> A brief summary of the fundamental decisions and solution strategies that
> shape the architecture of this repository, and the rationale behind them.

This repository automates the provisioning and ongoing maintenance of one
person's personal infrastructure: a Linux desktop, cloud VMs on AWS and
Hetzner, and a Windows Server VM. All infrastructure state is expressed as
Ansible code — no manual steps required.

## Repository Structure

The repository is divided into four top-level directories:

```text
roles/          ← reusable capability units (single responsibility each)
playbooks/      ← orchestration only; no implementation logic
inventories/    ← host groups and variables
configuration/  ← committed configuration files and backup archives
```

Every reusable capability lives in a role. Playbooks only import or include
roles and task files; they do not contain tasks directly — except for the
backup/restore pattern described in the
[Backup and Restore Pattern](#backup-and-restore-pattern) section below.

## Technology Choices

| Concern | Choice | Rationale |
| --- | --- | --- |
| Infrastructure automation | Ansible | Declarative, agentless, idempotent by design; wide community; no daemon required on managed hosts. |
| Local test VMs — macOS host | Vagrant + Tart (ARM64) | Tart provides lightweight, fast ARM64 VMs on Apple Silicon; Vagrant gives a reproducible workflow. |
| Local test VMs — Linux host | Vagrant + Docker | Docker-based Vagrant boxes start faster than full VMs on Linux; sufficient for most role tests. |
| Cloud targets | AWS EC2, Hetzner Cloud | Existing provider choice; not changed by automation tooling. |
| Guest OS | Ubuntu Linux (primary), Windows Server 2025 (secondary) | Ubuntu is the dominant desktop/server target; Windows Server added to run applications that are only available on Windows. |
| Secret management | Ansible Vault | Native Ansible integration; avoids third-party secret stores for a single-person project. |
| Scripting — simple | Bash | Minimal dependency; used only for bootstrap and helper scripts not suited to Ansible. |
| Scripting — complex | Python | Required for Ansible AWS modules; enables structured programming and unit testing for scripts too complex for Bash. |

New languages or runtimes may only be added with explicit justification
documented in this file and in the relevant `specs/<feature>/plan.md`.

## Quality Approach

| Quality Goal | Approach |
| --- | --- |
| **Idempotency** | Use built-in Ansible modules with idempotent semantics (running twice yields the same result as running once). Raw `command`/`shell` tasks require an explicit `creates:` or `changed_when:` guard. |
| **Testability** | Validate every change on a local VM (Vagrant + Tart or Docker) before applying to cloud targets. Isolate the role under test in `configure-linux-roles.yml`. |
| **Simplicity** | YAGNI (You Aren't Gonna Need It): minimum working solution. Parameterise only confirmed needs; no speculative abstraction. |
| **Traceability** | Conventional commits; co-authorship trailers for AI-assisted changes. Git is the sole source of version and author history. |

## Backup and Restore Pattern

Application backup and restore are implemented as thin playbooks in
`playbooks/backup/` and `playbooks/restore/` that delegate to two shared task
files (`playbooks/backup/backup.yml`, `playbooks/restore/restore.yml`). Each
application playbook supplies only the application-specific variables: source
path, archive name, exclusion patterns, and restore destination. This keeps
archival logic in one place while keeping each application playbook
independently readable and executable.

This is a deliberate exception to the role-first rule: these playbooks
pre-date Constitution Principle II. Whether they should be migrated to roles
is an open question (see [Known Technical Debt](#known-technical-debt)).

## Platform Constraints

Some playbooks are not compatible with all test environments. Ansible tags
mark these exceptions so they can be skipped selectively:

- **`not-supported-on-vagrant-docker`**: Applied to desktop application
  playbooks. Docker-based Vagrant boxes do not include a desktop environment,
  so desktop application roles and their backup/restore playbooks must be
  skipped on Docker targets.
- **`not-supported-on-vagrant-arm64`**: Applied to AMD64-only software (e.g.,
  Google Chrome, which has no ARM64 Linux package). Skips those playbooks on
  Tart (ARM64) VMs.

## Known Technical Debt

The full technical debt register is maintained in
[`docs/architecture/technical-debt/technical-debt.md`](technical-debt/technical-debt.md).
New entries are added during code reviews; each entry records context, risk,
and why it was accepted or deferred.

Two items are most relevant to architectural understanding:

- **TD-002 — Playbooks contain implementation logic** (High severity): eight
  `setup-*.yml` playbooks pre-date Constitution Principle II (Role-First
  Organisation) and contain direct task lists instead of delegating to roles.
  These are to be migrated to `roles/` one at a time as a dedicated
  refactoring effort.
- **Backup/restore pattern — open question**: the thin-delegation playbooks in
  `playbooks/backup/` and `playbooks/restore/` also pre-date the constitution.
  Whether this pattern should become Ansible roles is an open question.
  No change is made until this is resolved.

## References

- Project principles and development workflow:
  [`.specify/memory/constitution.md`](../../.specify/memory/constitution.md)
- Agent runtime guidance:
  [`CLAUDE.md`](../../CLAUDE.md),
  [`.cursor/rules/`](../../.cursor/rules/)
- Commit format and co-authorship:
  [`.cursor/rules/general/330-git-usage.mdc`](../../.cursor/rules/general/330-git-usage.mdc)
- Architecture Decision Records:
  [`docs/architecture/decisions/`](decisions/)
