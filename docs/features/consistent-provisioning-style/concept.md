# Consistent Provisioning Style

## Description

All environments use the same `ansible-playbook provision.yml --extra-vars "provider=<provider> platform=<platform>"` command to provision a VM. The provider and platform values select the correct provisioner module and configure playbook automatically, so users never need to remember provider-specific commands or manually chain separate steps.

## User Value

Before this feature, provisioning Vagrant Docker environments (dagorlad) required two separate commands (`vagrant up` followed by `ansible-playbook configure-linux.yml`), while cloud environments used a single unified command. This inconsistency created cognitive load when switching between environments and added maintenance complexity. The consistent provisioning style eliminates that gap: one command pattern works across all providers.

## Design Rationale

### Provider/platform parameter system

The `provision.yml` playbook accepts two extra-vars: `provider` and `platform`. These two values determine which provisioner module is included via the template path `provisioners/{{ provider }}-{{ platform }}.yml`. This keeps provider-specific logic isolated in one file per provider/platform combination and makes adding a new provider a matter of creating a single file.

### Provisioner module per provider

Each provider has its own provisioner module under `provisioners/`:

- `provisioners/hcloud-linux.yml` — Hetzner Cloud Linux
- `provisioners/aws-linux.yml` — AWS Linux
- `provisioners/aws-windows.yml` — AWS Windows

The provisioner module handles provider-specific VM lifecycle (e.g., Hetzner server creation, EC2 instance launch, or Vagrant container startup) and then hands off to the shared configure playbook.

### Shared configure playbook

After provisioning, `provision.yml` calls `configure-linux.yml` (or `configure-aws-windows.yml` for Windows). All environment-specific variable differences are resolved via the 4-tier group_vars precedence system (`all` → `platform` → `provider` → `provider_platform`), so the configure playbook itself is provider-agnostic.

## Command Reference

**Hetzner Linux (hobbiton):**
```bash
ansible-playbook provision.yml --extra-vars "provider=hcloud platform=linux"
```

**AWS Linux (rivendell):**
```bash
ansible-playbook provision.yml --extra-vars "provider=aws platform=linux"
```

**AWS Windows (moria):**
```bash
ansible-playbook provision.yml --extra-vars "provider=aws platform=windows"
```

Vagrant Docker and Tart provisioner support is planned; see [docs/feature-requests/feat.consistent.provisioning.style/prd.md](../../feature-requests/feat.consistent.provisioning.style/prd.md).

## Out of Scope

- Other Vagrant providers (Tart, VirtualBox)
- Vagrant destroy command unification
- Advanced error handling and edge cases beyond fail-fast behaviour
- Performance optimisation
- Advanced Vagrant configuration options
