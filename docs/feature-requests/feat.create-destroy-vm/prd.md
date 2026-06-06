# PRD: Create and Destroy VM Playbooks

## Problem

VM lifecycle management is fragmented and inconsistent:

- `provision.yml` dispatches via `import_playbook` (static, parse-time resolution)
- `destroy.yml` dispatches via `include_tasks` (dynamic, runtime resolution)
- Two different mechanisms for the same conceptual operation create cognitive load
- Vagrant Docker and Vagrant Tart are not unified with cloud providers under a
  single command
- `provision.yml` requires `platform` as a mandatory extra-var, adding friction
  for the common Linux case
- VM hostnames are assigned ad-hoc with no self-documenting convention that
  communicates provider or OS type at a glance

## Goal

Replace `provision.yml` and `destroy.yml` with two unified playbooks:

```bash
ansible-playbook create-vm.yml --extra-vars "profile=<profile> [provider=<provider>]"
ansible-playbook destroy-vm.yml --extra-vars "hostname=<hostname>"
```

Each invocation of `create-vm.yml` creates one new VM, registers it in
inventory, and configures it according to its profile. VM names are drawn from
a LOTR-inspired regional pool that encodes provider at a glance.

## Parameters

### `create-vm.yml`

| Parameter  | Required | Values                            | Default |
| ---------- | -------- | --------------------------------- | ------- |
| `profile`  | yes      | `basic`, `desktop`                | —       |
| `provider` | no       | `tart`, `docker`, `hcloud`, `aws` | `tart`  |

- `basic` — minimal Ubuntu, console only
- `desktop` — Ubuntu with desktop environment

### `destroy-vm.yml`

| Parameter  | Required | Values                            |
| ---------- | -------- | --------------------------------- |
| `hostname` | yes      | any hostname present in inventory |

## Behaviour

`create-vm.yml` always creates a new VM; it does not reuse or reprovision an
existing one. Each invocation draws the next unused hostname from the
provider+profile name pool. If the pool is exhausted, the playbook fails with
an explicit error naming the exhausted pool (Constitution Principle XII).

The assigned hostname is printed on completion.

## Scope

### In scope

- `create-vm.yml` — create VM, assign hostname from regional pool, register in
  inventory, apply profile configuration
- `destroy-vm.yml` — destroy VM, remove from inventory
- LOTR-regional hostname pools per provider
- Static inventory updates for `tart` and `docker` providers
- Dynamic inventory integration for `hcloud` and `aws` providers
- Documentation update: `docs/user-manual/create-vm.md`
- Deletion of superseded artefacts: `provision.yml`, `destroy.yml`,
  `provisioners/`

### Out of scope

- Changes to `configure-linux.yml` or existing configuration roles
- Resize, snapshot, or any lifecycle operation beyond create and destroy
- Windows VM creation (existing `moria` AWS Windows host is not affected)
- Provider-specific advanced options (instance types, regions) beyond current
  defaults

## Naming Convention

VM hostnames are drawn from ordered pools of LOTR place names. The region on
the LOTR map encodes the provider:

| Provider | LOTR Region                        | Example names              |
| -------- | ---------------------------------- | -------------------------- |
| `hcloud` | North-West (Eriador)               | hobbiton, Bree, Fornost, … |
| `aws`    | North-East (Iron Hills / Dale)     | rivendell, Erebor, Dale, … |
| `tart`   | Middle / South-West (Rohan/Gondor) | lorien, Edoras, Pelargir … |
| `docker` | Middle / South-West (Rohan/Gondor) | dagorlad, …                |

Existing hostnames (`hobbiton`, `rivendell`, `lorien`, `dagorlad`) are
grandfathered as the first entries in their respective pools. The AWS Windows
host `moria` is grandfathered into a South-East (Mordor / sinister realms)
pool reserved for future Windows support.

`profile` (`basic` vs `desktop`) shares the same provider pool — profile
affects configuration, not naming region.

## Acceptance Criteria

```gherkin
Scenario: Create hcloud Linux VM
  Given no VM named from the hcloud pool is running
  When ansible-playbook create-vm.yml --extra-vars "profile=basic provider=hcloud" completes
  Then a new Linux VM is running on Hetzner Cloud
  And its hostname is drawn from the North-West LOTR pool
  And ansible-inventory --graph shows the hostname under @hcloud and @linux groups
  And the VM is reachable via SSH

Scenario: Name pool exhaustion fails loud
  Given all hostnames in the tart pool are in use
  When ansible-playbook create-vm.yml --extra-vars "profile=basic provider=tart" runs
  Then the playbook fails immediately with an error message naming the exhausted pool

Scenario: Each run creates a new VM
  Given one tart VM already exists
  When ansible-playbook create-vm.yml --extra-vars "profile=basic provider=tart" runs again
  Then a second VM is created with a different hostname from the pool

Scenario: Destroy removes VM and inventory entry
  Given a VM with hostname=edoras exists in inventory
  When ansible-playbook destroy-vm.yml --extra-vars "hostname=edoras" completes
  Then the VM is deleted from the provider
  And edoras no longer appears in ansible-inventory --graph

Scenario: Static inventory updated for local providers
  Given provider is tart or docker
  When create-vm.yml completes
  Then the new hostname appears in the corresponding static inventory file
  And ansible-inventory --graph shows it under the correct groups

Scenario: Documentation reflects new commands
  Given both playbooks are implemented
  Then docs/user-manual/create-vm.md documents create-vm.yml and destroy-vm.yml
  And no references to provision.yml or destroy.yml remain in user-facing docs
```
