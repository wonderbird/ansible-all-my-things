# Playbook Classes

Constitution Principle II keeps the state of a managed host in roles and lets
playbooks compose them. This document is the authoritative definition of what
else a playbook may contain.

## The Test

For any task, handler or template in a playbook, ask: **must a fresh host get
this to be correct?** If yes, it belongs in a role. If no, it fits one of the
classes below.

The question catches installs too: after a package install a second run has
nothing left to do, yet a fresh host without the package is wrong, so the
install belongs in a role.

## Classes

A playbook MAY contain tasks, handlers or templates only for these classes.

### 1. Precondition Assertions

Assertions that fail loud on missing or invalid input before anything
changes, e.g. the `pre_tasks` of `configure-profile.yml`.

### 2. Procedures

Logic that does not define what a host must have:

- **Control-node operations** act on local files or provider APIs: creating
  and destroying VMs, editing the inventory, updating version pins. Examples:
  `create-vm.yml`, `destroy-vm.yml`, `enable-swapfile.yml`,
  `playbooks/update-versions/`.
- **One-shot actions** run to an end instead of converging to a state, e.g.
  `reboot-if-required.yml`.
- **Bootstrap access** covers the steps inside VM creation that enable the
  first login before any inventory play can connect: installing the
  operator's SSH key, or Windows `user_data` (ADR-004). `setup-users.yml` is
  not bootstrap access: it runs as an inventory play.

### 3. User-Environment Transfer

Playbooks that move one user's own files and preferences to and from a host:
`playbooks/backup/` and `playbooks/restore/`. Roles and procedures treat the
machine the same for every user; these playbooks carry what one user chose.

- They MUST NOT install software or change system configuration.
- They MAY overwrite configuration files a role placed in that user's home
  directory: the user's choice wins. Roles therefore create such files only if
  missing or merge only their own keys, so the user's version survives the
  next configure run.

## Rules for Classes 2 and 3

- Logic that several playbooks share lives in task files under
  `playbooks/tasks/` or the playbook's own directory.
- They are validated as Principle III requires: on a local VM, or with fixture
  tests as in `playbooks/update-versions/tests/`.
- A new playbook of either class MUST be justified in a plan that names its
  class and the rejected role alternative; the plan's architect review
  decides.

## Known Deviations

Playbooks and task files that configure managed hosts directly are recorded
in the [technical debt register](../technical-debt/technical-debt.md) as
TD-002. No new task that fails the test may be added to a playbook.
