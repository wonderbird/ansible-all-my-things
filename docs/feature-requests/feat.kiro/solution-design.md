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

---

## Section 2: Port `kiro` Branch Enhancements — Approach and Steps

### Approach

Prefer atomic `git cherry-pick` for self-contained commits that touch only
non-Kiro logic. Fall back to manual re-implementation for commits that
interleave Kiro-specific and general changes. Port one category of changes
at a time to keep review surface small.

### Tools

- `git diff main..kiro` — show all changes on `kiro` not yet on `main`
- `git log main..kiro --oneline` — list commits to categorize
- `git cherry-pick <sha>` — apply a self-contained commit atomically

### Steps

1. **Analyze the branch diff** — run `git diff main..kiro` and
   `git log main..kiro --oneline`. Produce a list of all commits on `kiro`
   that are not yet on `main`.
2. **Categorize commits** — classify each commit as one of:
   - `refactoring` — code cleanup with no behavior change
   - `bug-fix` — fixes a defect present on `main`
   - `dependency-update` — requirements.txt / requirements.yml / Galaxy
   - `kiro-specific` — directly implements Kiro IDE support
   Mixed commits (Kiro + non-Kiro) must be split or manually re-implemented.
3. **Author a port plan** — group non-Kiro commits by category; plan one
   logical PR or commit batch per category to keep review surface small.
4. **Execute cherry-picks / manual ports** — apply changes incrementally to
   `main`, using conventional-commit messages (Constitution Principle V).
   One commit per logical change.
5. **Rebase `kiro` onto updated `main`** — after all non-Kiro changes land
   on `main`, rebase the `kiro` branch: `git rebase main`. Verify that
   `git diff main..kiro` now contains only Kiro-specific content.
