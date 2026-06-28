# Create a Virtual Machine

## Virtual Machines on localhost

Local VMs running Ubuntu are created directly via `create-vm.yml` with
`-e provider=tart` (macOS ARM64) or `-e provider=docker` (any Docker host).
See [Role development workflow](../architecture/concepts/role-development-workflow.md)
for the role-isolation and local VM testing procedure.

## Virtual Machines on Cloud Providers

Currently the following virtual machines can be created:

- Windows Server 2025 on Amazon AWS EC2,
- Ubuntu 24.04 LTS on Amazon AWS EC2 or on Hetzner Cloud.

> [!IMPORTANT]
> For AWS, the security group is configured to allow SSH access only from your current public IP address. If your IP changes, you may need to update the security group rules in the AWS console.

## Prerequisites for Cloud VMs

### 1. Install Dependencies

First, install the required Python packages and Ansible collections:

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Ansible collections
ansible-galaxy collection install -r requirements.yml
```

### 2. SSH Key Pair Setup

**Step 0 — Generate a key (all providers)**

```shell
ssh-keygen -t ed25519 -f ~/.ssh/id_ansible_ed25519 -C "$(whoami)@$(hostname)"
```

The `-f` flag sets a dedicated filename; the public key
(`~/.ssh/id_ansible_ed25519.pub`) is generated automatically alongside it.
Using a dedicated name keeps the Ansible key separate from other keys.

> [!NOTE]
> AWS Windows instances only support RSA and ECDSA keys. If you plan to use
> Windows on AWS, generate an RSA key instead and reuse it for Hetzner Cloud.

**Step 1 — Local providers (Tart, Docker)**

No registration step is needed. The generated key is already referenced in
`group_vars/tart/` and `group_vars/docker/`. Update `ansible_ssh_private_key_file`
there if you used a different filename.

**Step 2 — Cloud providers (AWS, Hetzner Cloud)**

Register the public key with each cloud provider before creating VMs. Follow
the instructions in the provider-specific prerequisites:

- [AWS EC2 prerequisites](./prerequisites-aws.md)
- [Hetzner Cloud prerequisites](./prerequisites-hcloud.md)

### 3. Provider-Specific Prerequisites

Some prerequisites differ by provider. Refer to the corresponding documentation to complete the setup:

- [AWS EC2](./prerequisites-aws.md)
- [Hetzner Cloud](./prerequisites-hcloud.md)

Depending on the target system, choose the appropriate hostname from the table in the [README.md](../README.md).

## Create a Cloud VM

Create the server using the following command:

```shell
ansible-playbook playbooks/create-vm.yml --extra-vars "provider=hcloud"
```

The `provider` parameter can be one of

- `aws`
- `hcloud`

`profile` can be one of

- `basic` (default)
- `desktop`
- `windows`

> [!NOTE]
> Windows is only supported by `provider=aws`.

To pick a good combination, use the following guidelines:

- If you want to run Windows, choose `--extra-vars provider=aws --extra-vars profile=windows`
- If you want to run Linux, prefer `--extra-vars provider=hcloud` (default `profile=basic`)
- If there are no virtual machines available on `hcloud`, then try aws: `--extra-vars provider=aws`

After about 1 - 2 minutes, the new server is created. The SSH host key is
trusted automatically into a project-scoped `known_hosts` file (see
[ADR-003](../architecture/decisions/003-ssh-host-key-verification-policy.md)) — no manual confirmation is required.

After that, the setup will take another 10 - 15 minutes.

### Attention: Inventory Refresh Requires Sourced Configuration Script

If refreshing the inventory fails, then you might have forgotten to source the configuration script. Check the section on provider specific prerequisites above.

### Note: Windows requires manual setup

The Windows Server provides a clean installation with SSH, RDP access, and the Chocolatey package manager. However, unlike the Linux systems, **it does not include**:

- Pre-installed development applications and tools
- Automated backup/restore of user configurations
- Keyring restoration with saved passwords
- Ready-to-use development environment

**Expected setup time**: 1-2 hours to manually install and configure your development tools and applications.

**Recommendation**: Use Windows Server when you specifically need Windows-only applications. For general development work, prefer the Linux systems which provide a complete, instantly-ready development environment with automatic configuration restoration.

## Verify the Setup

```shell
# Show the inventory
ansible-inventory --graph
```

The inventory will show the host name for the provisioned instance. The host name is unique for each provider and platform combination. Have a look at the table in the [/README.md](../README.md) to see the possible combinations of provider, platform and host name.

Before executing the other commands in this section, load the configured key into your SSH agent:

```shell
ssh-add ~/.ssh/YOUR_KEY_FILE.pem
```

Then run the following commands to verify the setup:

```shell
# Check whether the server can be reached
# Linux variant:
ansible linux -m shell -a 'whoami' --extra-vars "ansible_user=galadriel"

# Windows variant using win_command
ansible windows -m win_command -a 'whoami' --extra-vars "ansible_user=Administrator"
```

>[!IMPORTANT]
> You might want to add additional SSH keys to the `authorized_keys` files on
> the server.

You can also SSH directly to the instance. Look up the IP address with:

```shell
ansible-inventory --host <hostname>
```

Load your SSH key, then connect using `ansible_host` from the output:

```shell
ssh-add ~/.ssh/id_ansible_ed25519

# On Linux, galadriel is the default desktop user
ssh galadriel@<ip>

# On Windows, only Administrator is configured as a user
ssh Administrator@<ip>
```

## Connect using RDP

Connect via an RDP compatible client. For Linux, use the `galadriel` user, on Windows connect as `Administrator`.

## Delete the VM

To delete the VM and all associated resources, back up your configuration
first — see [Backup and Restore](./backup-restore.md) — then destroy:

```shell
ansible-playbook playbooks/destroy-vm.yml --extra-vars provider=hcloud --extra-vars hostname=<hostname>
```

Use the same `provider` value used to create the VM, and the `hostname` shown
by `ansible-inventory --graph`.

> [!IMPORTANT]
> Always destroy AWS and Hetzner Cloud instances when no longer needed.
> Monitor the corresponding billing dashboards for unexpected charges.

--

Next: [Work with a Virtual Machine](./work-with-vm.md)
