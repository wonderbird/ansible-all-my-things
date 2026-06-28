# Create and Destroy VMs

Manage local Ubuntu VMs using `playbooks/create-vm.yml` /
`playbooks/destroy-vm.yml`. Four providers are available, selected via
`-e provider=<tart|docker|hcloud|aws>` (default: `tart`):

- **`tart`** (default, this document) — macOS ARM64 only, described below.
- **`docker`** — any host with a Docker daemon. Both providers run the same
  Ubuntu 24.04 guest; differences are called out per section below as
  "Docker differs: ...". For an SSH-into-container walkthrough, see
  [specs/011-docker-vm-provider/quickstart.md](../../../specs/011-docker-vm-provider/quickstart.md).
- **`hcloud`** — a disposable Hetzner Cloud server. Differences are called
  out per section below as "Hcloud differs: ...". For a step-by-step
  walkthrough, see
  [specs/012-hcloud-vm-provider/quickstart.md](../../../specs/012-hcloud-vm-provider/quickstart.md).
- **`aws`** — a disposable AWS EC2 instance. Differences are called out per
  section below as "AWS differs: ...". For a step-by-step walkthrough, see
  [specs/013-aws-vm-provider/quickstart.md](../../../specs/013-aws-vm-provider/quickstart.md).

## Requirements

- macOS ARM64 host
- [`tart`](https://github.com/cirruslabs/tart) CLI
- [`sshpass`](https://github.com/hudochenkov/sshpass) — for password-based
  SSH authentication:

  ```bash
  brew install sshpass
  ```

- `ANSIBLE_VAULT_PASSWORD` environment variable set
  (see [Credentials](#credentials))

**Docker differs**: any host with a working Docker daemon (Linux primary; any
non-macOS-ARM64 host also works). No `tart` CLI needed. `sshpass` is still
required. Select with `-e provider=docker`.

**Hcloud differs**: `HCLOUD_TOKEN` exported in your shell (Hetzner Cloud API
token). Your SSH private key matching `my_ssh_key_name` (vault-configured in
`inventories/group_vars/all/vault.yml`) loaded in your SSH agent and already
registered with Hetzner Cloud under that name. `hetzner.hcloud` collection
installed (`requirements.yml`). Neither `tart` nor `sshpass` is needed. Select
with `-e provider=hcloud`.

**AWS differs**: AWS credentials configured via the standard AWS SDK
credential chain (environment variables, shared credentials file, or instance
profile). Your SSH private key matching `my_ssh_key_name` loaded in your SSH
agent and already registered with AWS as a key pair in the target region.
`amazon.aws` collection installed (`requirements.yml`). Neither `tart` nor
`sshpass` is needed. Select with `-e provider=aws`.

Both `hcloud` and `aws` additionally require the vault password available via
`ANSIBLE_VAULT_PASSWORD_FILE` (see [Credentials](#credentials)).

## Create a VM

```bash
ansible-playbook playbooks/create-vm.yml
```

No extra variables required. The playbook picks the next unused hostname
from the pool, creates the VM, waits for SSH, and registers the VM in
inventory.

Default resources: **4 vCPU, 8 GB RAM, 45 GB disk**. Override with extra
vars:

```bash
ansible-playbook playbooks/create-vm.yml \
  --extra-vars vm_cpus=2 --extra-vars vm_memory_mb=4096 --extra-vars vm_disk_size_gb=60
```

**Docker differs**: run with `--extra-vars provider=docker`. On first run this builds
the `ansible-vm-docker:latest` image (subsequent runs reuse it). Defaults are
**2 vCPU, 4 GB RAM**, set via `docker_vm_cpus` / `docker_vm_memory` (no disk
size variable — containers share the host filesystem):

```bash
ansible-playbook playbooks/create-vm.yml --extra-vars provider=docker \
  --extra-vars docker_vm_cpus=4 --extra-vars docker_vm_memory=8g
```

**Hcloud differs**: run with `--extra-vars provider=hcloud`. Creates a disposable
Hetzner Cloud server using the default server type/location/image
(overridable via `--extra-vars hcloud_server_type=...`, `--extra-vars hcloud_server_location=...`,
`--extra-vars image=...`):

```bash
ansible-playbook playbooks/create-vm.yml --extra-vars provider=hcloud
```

**AWS differs**: run with `--extra-vars provider=aws`. Ensures the shared `ansible-sg`
security group exists (SSH/22 inbound), then creates a disposable EC2 Linux
instance using the default AMI/instance type/region (overridable via
`--extra-vars aws_ami_id=...`, `--extra-vars aws_instance_type=...`,
`--extra-vars aws_region=...`):

```bash
ansible-playbook playbooks/create-vm.yml --extra-vars provider=aws
```

## Configure a VM

```bash
ansible-playbook playbooks/configure-profile.yml
```

No extra variables required. Run this against a VM created by
`playbooks/create-vm.yml` (it connects via the default `admin` account
defined in `inventories/group_vars/tart/vars.yml`). It creates the
configured users with SSH/sudo access, applies OS package and timezone
baselines, installs the Node.js toolchain for desktop users, installs the
standard development tool roles (podman, ruby, python, dolt_sql_server,
claude_code), and reboots the VM if required. Re-running the playbook on an
already-configured VM is a no-op.

## Destroy a VM

```bash
ansible-playbook playbooks/destroy-vm.yml --extra-vars hostname=vulcan
```

Destroys the VM and removes it from inventory. The hostname returns to the
pool.

**Docker differs**: add `--extra-vars provider=docker`, e.g.:

```bash
ansible-playbook playbooks/destroy-vm.yml \
  --extra-vars provider=docker --extra-vars hostname=tatooine
```

Stops and removes the container and removes it from
`inventories/docker_autogenerated.yml`.

**Hcloud differs**: add `--extra-vars provider=hcloud`, e.g.:

```bash
ansible-playbook playbooks/destroy-vm.yml \
  --extra-vars provider=hcloud --extra-vars hostname=edoras
```

Deletes the Hetzner Cloud server, removes it from
`inventories/hcloud_autogenerated.yml`, and removes its SSH host key from
`inventories/hcloud_known_hosts`.

**AWS differs**: add `--extra-vars provider=aws`, e.g.:

```bash
ansible-playbook playbooks/destroy-vm.yml \
  --extra-vars provider=aws --extra-vars hostname=arrakis
```

Terminates the EC2 instance, removes it from
`inventories/aws_autogenerated.yml`, and removes its SSH host key from
`inventories/aws_known_hosts`. The shared `ansible-sg` security group is left
in place.

## Hostname Pool

VMs are assigned names sequentially from a Star Trek TNG planet pool
(defined in `playbooks/vars/hostname_pool_tart.yml`):

`vulcan`, `romulus`, `betazed`, `qonos`, `risa`, `cardassia`, `bajor`,
`veridian`, `remus`, `baku`

Up to 10 VMs can coexist. Add names to the pool file to extend the limit.

**Docker differs**: a separate, disjoint pool of Star Wars planet names is
defined in `playbooks/vars/hostname_pool_docker.yml`:

`tatooine`, `coruscant`, `naboo`, `alderaan`, `hoth`, `dagobah`, `endor`,
`kamino`, `mustafar`, `yavin`

Same allocation rules apply; append to that file to extend the limit.

**Hcloud differs**: a separate, disjoint pool of Lord of the Rings place names
is defined in `playbooks/vars/hostname_pool_hcloud.yml`:

`edoras`, `shire`, `osgiliath`, `bree`, `isengard`, `rohan`, `angmar`,
`minas-tirith`, `helms-deep`, `mordor`

Same allocation rules apply; append to that file to extend the limit.

**AWS differs**: a separate, disjoint pool of Dune place names is defined in
`playbooks/vars/hostname_pool_aws.yml`:

`arrakis`, `caladan`, `giedi-prime`, `kaitain`, `ix`, `chusuk`, `tleilax`,
`salusa-secundus`, `wallach-ix`, `ginaz`

Same allocation rules apply; append to that file to extend the limit.

## Inventory

Created VMs are registered in
`inventories/tart_autogenerated.yml` (gitignored). This file is
managed automatically — do not edit it by hand.

**Docker differs**: containers are registered in
`inventories/docker_autogenerated.yml` (gitignored, also managed
automatically). Connection details differ from Tart: containers are reached
via `127.0.0.1` on a dynamically published host port (Docker picks a free
port and maps it to the container's SSH port 22; the assigned port is
recorded as `ansible_port` in this inventory file), not the VM's own IP on
port 22.

**Hcloud differs**: servers are registered in
`inventories/hcloud_autogenerated.yml` (gitignored, also managed
automatically), reached via the server's public IP as `ansible_user: root`.
Per ADR-003 (Principle XIV — internet-exposed host), the SSH connection uses
`StrictHostKeyChecking=accept-new` against a project-scoped, gitignored
`inventories/hcloud_known_hosts`, instead of the
`StrictHostKeyChecking=no` used by Tart/Docker. `destroy-vm.yml` removes the
corresponding entry from `inventories/hcloud_known_hosts`.

**AWS differs**: instances are registered in
`inventories/aws_autogenerated.yml` (gitignored, also managed automatically),
reached via the instance's public IP as `ansible_user: ubuntu`. Per ADR-003
(Principle XIV — internet-exposed host), the SSH connection uses
`StrictHostKeyChecking=accept-new` against a project-scoped, gitignored
`inventories/aws_known_hosts`, instead of the `StrictHostKeyChecking=no` used
by Tart/Docker. `destroy-vm.yml` removes the corresponding entry from
`inventories/aws_known_hosts`. The shared `ansible-sg` security group
(SSH/22 inbound) is created on first use and left in place across destroys.

## Credentials

VMs use the CirrusLabs Ubuntu image default credentials (`admin` /
`admin`). The password is stored in
`playbooks/vars/tart_credentials.yml`.

Before use in any non-throwaway environment, replace it with a
vault-encrypted value:

```bash
export ANSIBLE_VAULT_PASSWORD=<your-vault-password>
ansible-vault encrypt_string 'admin' --name tart_admin_password
```

Paste the output into `playbooks/vars/tart_credentials.yml`:

```yaml
---
tart_admin_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  <encrypted blob here>
```

The vault password is read at runtime from the `ANSIBLE_VAULT_PASSWORD`
environment variable via
`scripts/echo-vault-password-environment-variable.sh`.

**Docker differs**: containers use `root` / `docker` (baked into the
`ansible-vm-docker:latest` image at build time via `docker_root_password` in
`playbooks/vars/docker_credentials.yml`). To change it, edit
`docker_root_password` and remove the existing `ansible-vm-docker:latest`
image to force a rebuild — the image is otherwise built once and reused.

**Hcloud/AWS differ**: no local VM password — authentication is SSH key pair
only. Both providers reuse the `my_ssh_key_name` SSH key (vault-configured in
`inventories/group_vars/all/vault.yml`), which must already be registered with
the respective cloud provider (Hetzner Cloud / AWS) under that name.
