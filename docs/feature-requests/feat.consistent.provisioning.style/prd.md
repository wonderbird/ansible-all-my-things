# PRD: Unified Vagrant Docker Provisioning

## Problem

The Vagrant Docker test VM (dagorlad) is provisioned with a separate
`vagrant up` command followed by a manual `configure-linux.yml` run.
All other providers (Hetzner, AWS Linux, AWS Windows) use a single unified
command:

```bash
ansible-playbook provision.yml --extra-vars "provider=<provider> platform=<platform>"
```

This inconsistency creates cognitive load for anyone switching between
providers and breaks the project's cross-provider automation promise.

## Goal

Extend the existing `provisioners/{{ provider }}-{{ platform }}.yml` template
pattern to cover Vagrant Docker so that dagorlad can be provisioned with:

```bash
ansible-playbook provision.yml --extra-vars "provider=vagrant_docker platform=linux"
```

## Scope

### In scope

- Create `provisioners/vagrant_docker-linux.yml` using the `shell` module
  with `chdir: test/docker` and a `creates:` guard
- Verify that `provision.yml` already routes `provider=vagrant_docker
  platform=linux` to the new provisioner (no parameter-system changes expected)
- Update `docs/user-manual/create-vm.md` to document the Vagrant Docker command
- Update `test/docker/README.md` with the unified command
- Implement idempotency and inventory-integration acceptance tests

### Out of scope

- Vagrant Tart provider unification (lorien)
- `vagrant destroy` / teardown unification
- Advanced error-handling or retry logic
- Any other VM or provider beyond dagorlad

## Provider Comparison

| Focus Area | Hetzner (hobbiton) | Vagrant Docker (dagorlad) |
|---|---|---|
| Connection | SSH to public IP | SSH to `localhost:2223` |
| Default User | `root` then `galadriel` | `vagrant` |
| Package Manager | `apt` | `apt` |
| Provisioning | `ansible-playbook provision.yml` | `vagrant up` + separate configure (current gap) |
| Cost | ~$4/month | Free (local Docker) |
| Inventory Groups | `@hcloud`, `@hcloud_linux`, `@linux` | `@vagrant_docker`, `@linux` |

## Acceptance Criteria

```gherkin
Scenario: Clean provisioning
  Given dagorlad is not running
  When ansible-playbook provision.yml --extra-vars "provider=vagrant_docker platform=linux" completes
  Then dagorlad is reachable via SSH as vagrant@<ip> -p 2223

Scenario: Idempotency
  Given dagorlad is already provisioned
  When the same provision.yml command is re-run
  Then no tasks report "changed" for already-configured state
  And dagorlad remains reachable

Scenario: Inventory integration
  Given dagorlad has been provisioned
  When ansible-inventory --graph is run
  Then dagorlad appears under @linux and @vagrant_docker groups

Scenario: Variable loading
  Given inventories/vagrant_docker/vars.yml exists
  When the provisioner runs
  Then admin_user_on_fresh_system resolves to "vagrant"
  And host variables load correctly from the vagrant_docker group_vars

Scenario: Documentation updated
  Given provisioning is working
  Then docs/user-manual/create-vm.md documents the unified Vagrant Docker command
  And test/docker/README.md references the unified command
```
