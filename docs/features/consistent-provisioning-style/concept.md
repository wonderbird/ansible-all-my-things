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

**Vagrant Docker (dagorlad) — target command:**
```bash
ansible-playbook provision.yml --extra-vars "provider=vagrant_docker platform=linux"
```

## Provider Differences

| Property | Hetzner Linux | AWS Linux | Vagrant Docker |
|---|---|---|---|
| Connection | SSH | SSH | SSH (port 2223) |
| Default User | root → galadriel | ubuntu → galadriel | vagrant |
| Package Manager | apt | apt | apt |
| Provisioning | hcloud server create | EC2 launch | vagrant up |
| Cost | ~$4/mo (persistent) | ~$8-10/mo (on-demand) | free |
| Inventory Groups | @hcloud, @hcloud_linux | @aws_ec2, @aws_ec2_linux | @vagrant_docker, @linux |

## Vagrant Docker Specifics

The `provisioners/vagrant_docker-linux.yml` provisioner uses the Ansible `shell` module to execute `vagrant up` from the `test/docker/` directory, then calls `meta: refresh_inventory` so subsequent tasks see the newly started container in the inventory.

- Admin user on fresh system: `vagrant`
- Estimated provisioning time: 2–3 minutes
- Docker backend; no cloud account required
- Inventory source: `inventories/vagrant_docker.yml`
- Group vars: `inventories/group_vars/vagrant_docker/`

## Inventory Integration

The `inventories/vagrant_docker.yml` inventory file is referenced by `ansible.cfg` alongside the cloud provider inventories. Variable loading follows the same 4-tier precedence as production environments:

1. `group_vars/all/` — shared defaults
2. `group_vars/linux/` — platform-level vars
3. `group_vars/vagrant_docker/` — provider-level vars
4. `group_vars/vagrant_docker_linux/` — provider+platform combination vars

This means `ansible-inventory --graph` shows dagorlad in the `@vagrant_docker` and `@linux` groups, and vault-managed variables (SSH keys, secrets) load automatically via `ansible.cfg`'s `vault_password_file`.

## Out of Scope

- Other Vagrant providers (Tart, VirtualBox)
- Vagrant destroy command unification
- Advanced error handling and edge cases beyond fail-fast behaviour
- Performance optimisation
- Advanced Vagrant configuration options
