# Solution Design: Kiro IDE — Install and Branch Hygiene

## Section 1: Install Kiro IDE — Approach and Steps

### Approach

Follow Constitution Principle II (Role-First Organisation): all installation
logic lives in `roles/setup-kiro-ide/`. Playbooks only orchestrate the role.
Do not add tasks directly to any `setup-*.yml` playbook (see TD-002 in
`docs/architecture/solution-strategy.md`).

The role follows the established pattern used by `setup-vscode` and
`setup-git`: one role per software tool, idempotent tasks, applied via the
existing playbook(s) that target the `linux` host group
(`configure.yml` / `configure-linux.yml`).

### Role Structure

```
roles/setup-kiro-ide/
  defaults/main.yml   # kiro_version, kiro_install_path
  tasks/main.yml      # download → install → verify
  meta/main.yml       # platforms: Ubuntu
  molecule/default/   # Molecule scenario (see molecule-testing skill)
```

### Steps

1. **Research Kiro install procedure on Ubuntu** — determine the delivery
   mechanism (apt repository, tarball download, snap, or other). Document
   the install command and any prerequisites.
2. **Scaffold the role** — create `roles/setup-kiro-ide/` with `tasks/main.yml`,
   `defaults/main.yml` (version + install path variables), and `meta/main.yml`
   (platforms = Ubuntu). Use `creates:` or equivalent idempotency guards on
   any `command`/`shell` tasks (Constitution Principle I).
3. **Wire role into the configure playbook** — add `setup-kiro-ide` to the
   role list in `configure-linux.yml` (or the equivalent playbook targeting
   the `linux` group) for the `rivendell` and `hobbiton` hosts.
4. **Add Molecule scenario** — invoke the `molecule-testing` skill to scaffold
   the full `create → prepare → converge → idempotence → verify → destroy`
   lifecycle. Verify scenario runs cleanly in a container.
5. **End-to-end validation** — run the playbook against `hobbiton` or
   `rivendell`; confirm Kiro IDE is installed and accessible to user
   `galadriel`. Re-run to confirm idempotency (no changes reported).

