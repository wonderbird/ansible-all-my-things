# Solution Design: Create and Destroy VM Playbooks

## Supersedes

This document supersedes the following artefacts, which are deleted as part of
this feature:

- `docs/feature-requests/feat.consistent.provisioning.style/` — the narrower
  goal of unifying Docker provisioning under `provision.yml` is subsumed by
  this broader redesign
- `docs/features/consistent-provisioning-style/concept.md` — documents the
  `provision.yml` + `provisioners/` pattern being replaced

Git history preserves their content.

## Dispatch Mechanism

Both playbooks use identical dynamic dispatch:

```yaml
# create-vm.yml
- ansible.builtin.include_tasks: "playbooks/tasks/create/{{ provider }}.yml"

# destroy-vm.yml
- ansible.builtin.include_tasks: "playbooks/tasks/destroy/{{ provider }}.yml"
```

Provider values are validated via `assert` before the include, following
Constitution Principle XII (Fail Loud):

```yaml
- ansible.builtin.assert:
    that: provider in ['tart', 'docker', 'hcloud', 'aws']
    fail_msg: >
      Unknown provider '{{ provider }}'.
      Valid values: tart, docker, hcloud, aws.
```

Dynamic `include_tasks` with a variable filename is the idiomatic pattern for
localhost orchestration in this project (already used in `destroy.yml`) and
follows community convention: cloud provisioning runs against
`hosts: localhost / connection: local` and is not a role-style capability
running on a target host. Roles are reserved for configuration that runs on the
provisioned VM and can be Molecule-tested.

## File Structure

```text
playbooks/
  create-vm.yml            # replaces provision.yml
  destroy-vm.yml           # replaces destroy.yml
  tasks/
    create/
      tart.yml
      docker.yml
      hcloud.yml
      aws.yml
    destroy/
      tart.yml
      docker.yml
      hcloud.yml
      aws.yml
```

The `provisioners/` directory, `provision.yml`, and `destroy.yml` are deleted.

## Name Pool Design

Hostname pools are defined in a vars file (or files — the implementing agent
decides whether one shared file or per-provider files better fits the project
style). Each pool is an ordered list of LOTR place names.

At runtime, `create-vm.yml`:

1. Loads the pool for the requested provider.
2. Queries the current inventory to determine which names are already in use.
3. Selects the first unused name.
4. Fails loud if no unused name remains (Principle XII).

### Regional mapping

| Pool key       | LOTR region                        | Seed names (grandfathered) | Direction for new names         |
| -------------- | ---------------------------------- | -------------------------- | ------------------------------- |
| `hcloud`       | North-West Eriador                 | hobbiton                   | Bree, Fornost, Annúminas, …     |
| `aws_linux`    | North-East (Iron Hills / Dale)     | rivendell                  | Erebor, Dale, Esgaroth, …       |
| `aws_windows`  | South-East (Mordor / sinister)     | moria                      | Barad-dûr, Gorgoroth, …         |
| `tart`         | Middle / South-West (Rohan/Gondor) | lorien                     | Edoras, Minas Tirith, Pelargir… |
| `docker`       | Middle / South-West (Rohan/Gondor) | dagorlad                   | …                               |

`aws_windows` is listed for completeness and to anchor `moria`; Windows VM
creation is out of scope for `create-vm.yml`.

`profile` (`basic` vs `desktop`) shares the provider's pool — profile affects
configuration, not naming.

## Inventory Strategy

| Provider | Inventory mechanism                          | Update action on create                         |
| -------- | -------------------------------------------- | ----------------------------------------------- |
| `tart`   | Static file `inventories/vagrant_tart.yml`   | Append host entry with connection vars + groups |
| `docker` | Static file `inventories/vagrant_docker.yml` | Append host entry with connection vars + groups |
| `hcloud` | Dynamic plugin `inventories/hcloud.yml`      | None — plugin reads live Hetzner state          |
| `aws`    | Dynamic plugin `inventories/aws_ec2.yml`     | None — plugin reads live EC2 state              |

After creating a cloud VM, `ansible.builtin.meta: refresh_inventory` is called
so subsequent plays in the same run see the new host.

On destroy, static inventory entries are removed; cloud VMs are deregistered
automatically when the dynamic plugin no longer finds them.

## Profile Handling

`profile` is passed as a variable through `create-vm.yml` but does not
influence which provider task file is included. After VM creation and inventory
registration, `create-vm.yml` delegates to the existing `configure-linux.yml`
(for `basic`) or `configure-desktop.yml` (for `desktop`) with the new host as
target. No new configuration roles are introduced.

## Idempotency and Guards

- Cloud modules (`hetzner.hcloud.server`, `amazon.aws.ec2_instance`) use
  `state: present` — idempotent by module design.
- Tart and Docker task files use `creates:` guards on shell tasks or check for
  existing `.vagrant/` state (Constitution Principle I).
- Name uniqueness is enforced by the pool-check logic: a hostname already
  present in inventory is never reassigned.

## Superseded Artefacts to Delete

The following files are deleted as part of this feature. Git history preserves
their content.

- `provision.yml` — replaced by `create-vm.yml`
- `destroy.yml` — replaced by `destroy-vm.yml`
- `provisioners/` (entire directory) — replaced by `playbooks/tasks/create/`
- `docs/feature-requests/feat.consistent.provisioning.style/` — superseded
- `docs/features/consistent-provisioning-style/concept.md` — documents the
  replaced design

## Documentation to Update

- `docs/user-manual/create-vm.md` — replace `provision.yml` / `destroy.yml`
  commands with `create-vm.yml` / `destroy-vm.yml`

## Definition of Done

- `create-vm.yml` and `destroy-vm.yml` exist and dispatch correctly for all
  four providers
- Name pool selection works; pool exhaustion fails loud with an actionable error
- Static inventory updated correctly for `tart` and `docker` on create and
  destroy
- Dynamic inventory (hcloud, aws) reflects the new VM after `refresh_inventory`
- `provision.yml`, `destroy.yml`, and `provisioners/` are deleted
- All acceptance criteria in the PRD pass
- `docs/user-manual/create-vm.md` is updated; no user-facing doc references
  `provision.yml` or `destroy.yml`
