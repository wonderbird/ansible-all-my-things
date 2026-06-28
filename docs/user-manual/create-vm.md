# Create a Virtual Machine

## Virtual Machines on localhost

Local VMs running Ubuntu are created directly via `create-vm.yml` with
`--extra-vars provider=tart` (macOS ARM64) or
`--extra-vars provider=docker` (any Docker host).
See [Testing concepts](../architecture/concepts/testing.md)
for the role-isolation and local VM testing procedure.

## Virtual Machines on Cloud Providers

Currently the following virtual machines can be created:

- Windows Server 2025 on Amazon AWS EC2,
- Ubuntu 24.04 LTS on Amazon AWS EC2 or on Hetzner Cloud.

> [!IMPORTANT]
> For AWS, the security group is configured to allow SSH access only from
> your current public IP address. If your IP changes, you may need to
> update the security group rules in the AWS console.

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

#### Step 0 — Generate a key (all providers)

```shell
ssh-keygen -t ed25519 -f ~/.ssh/id_ansible_ed25519 -C "$(whoami)@$(hostname)"
```

The `-f` flag sets a dedicated filename; the public key
(`~/.ssh/id_ansible_ed25519.pub`) is generated automatically alongside it.
Using a dedicated name keeps the Ansible key separate from other keys.

> [!NOTE]
> AWS Windows instances only support RSA and ECDSA keys. If you plan to
> use Windows on AWS, generate an RSA key instead and reuse it for
> Hetzner Cloud.

#### Step 1 — Local providers (Tart, Docker)

No registration step is needed. The generated key is already referenced
in `group_vars/tart/` and `group_vars/docker/`. Update
`ansible_ssh_private_key_file` there if you used a different filename.

#### Step 2 — AWS EC2

Register the SSH key with AWS EC2:

1. Go to EC2 → Key Pairs in your [AWS console][aws-console-ec2]
2. Either create a new key pair or import your existing public key
3. Configure the key pair name in
   [/inventories/group_vars/all/vars.yml](../../inventories/group_vars/all/vars.yml)
   (see Ansible Vault Setup below)
4. Ensure you have the corresponding private key file (`.pem` format) in
   `~/.ssh/` with permissions restricted to 600:
   `chmod 600 ~/.ssh/*pem`
5. Set a password for the key file:
   `ssh-keygen -p -f ~/.ssh/YOUR_KEY_FILE.pem`

> [!IMPORTANT]
> **Windows AMI Limitation**: AWS does not support ED25519 key pairs for
> Windows AMIs. If you plan to use Windows Server instances, you must use
> RSA (minimum 2048-bit) or ECDSA key pairs. For Linux AMIs, all key
> types including ED25519 are supported.

#### Step 3 — Hetzner Cloud

Register your SSH key in the Hetzner Cloud project:

1. Log into the [Hetzner Cloud Console](https://console.hetzner.cloud/)
   and open your project.
2. Go to **Security** → **SSH Keys** → **Add SSH Key**.
3. Paste the contents of your public key file
   (e.g. `~/.ssh/id_ansible_ed25519.pub`).
4. Set the name to match the `my_ssh_key_name` value you will configure
   in your vault (see Hetzner Cloud Setup below).

### 3. AWS EC2 Setup

#### Install AWS CLI

Follow the instructions for your operating system to install the latest
supported AWS CLI: [Installing or updating the AWS CLI][aws-cli-install]

#### AWS Credentials Setup

If you don't have an AWS account yet, follow these steps:

##### 1. Create AWS Account

- Go to [aws.amazon.com][aws-account] and click "Create an AWS Account"
- Provide email, password, and account name
- Enter payment information (required even for free tier)
- Verify phone number and identity

##### 2. Create IAM User for Programmatic Access

- Log into AWS Console → Go to IAM service
- Click "Users" → "Create user"
- Username: `ansible-automation` (or similar)
- Select "Programmatic access" (API access)

##### 3. Set Permissions

**For quick setup (broader permissions):**

Attach existing policy: `AmazonEC2FullAccess`

**For minimal permissions:**

Create custom policy with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances", "ec2:TerminateInstances",
        "ec2:DescribeInstances", "ec2:DescribeImages",
        "ec2:DescribeKeyPairs", "ec2:DescribeSecurityGroups",
        "ec2:CreateSecurityGroup", "ec2:DeleteSecurityGroup",
        "ec2:AuthorizeSecurityGroupIngress", "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

##### 4. Get Access Keys

- After user creation, **immediately download** the CSV file with:
  - Access Key ID
  - Secret Access Key
- Store these securely — you cannot retrieve the secret key again

##### 5. Configure Credentials and Default Region

> [!IMPORTANT]
> **Region Selection**: The `AWS_DEFAULT_REGION` environment variable
> determines which AWS region is used for:
>
> - Instance provisioning
> - Inventory queries (critical for performance)
> - Resource management
>
> **Performance Impact**: Setting `AWS_DEFAULT_REGION` to match your
> instance locations is essential for fast inventory operations
> (~1 second vs 16+ seconds). If not set, defaults to `eu-north-1`.

###### Option 1: Environment Variables (Recommended)

```shell
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="eu-north-1"  # or your preferred region
```

###### Option 2: AWS CLI Configuration

```shell
aws configure
```

> [!NOTE]
> When using `aws configure`, the region you specify is saved in your
> AWS configuration. Transfer it to the environment variable:

```shell
# Extract region from AWS CLI config and set as environment variable
export AWS_DEFAULT_REGION=$(aws configure get region)

# Verify the region is set correctly
echo "Using AWS region: $AWS_DEFAULT_REGION"
```

#### Ansible Vault Setup

Follow the instructions in [Important concepts](./important-concepts.md)
to update your secrets in `.envrc` and in
[./inventories/group_vars/all/vars.yml](./inventories/group_vars/all/vars.yml).

#### AWS Instance Type Guidelines

**t3.micro** is the default choice for all AWS tests:

- Free tier eligible (subject to account limits)
- Sufficient for most testing scenarios
- Minimum costs if free tier limit exceeded

> [!IMPORTANT]
> Always destroy AWS and Hetzner Cloud instances after testing. Monitor
> the corresponding billing dashboards for unexpected charges.

### 4. Hetzner Cloud Setup

1. **Create cloud project:** You need a cloud project with
   [Hetzner](https://www.hetzner.com/).

2. **Configure server properties:** Server size and location defaults
   live in
   [/inventories/group_vars/hcloud/vars.yml](../../inventories/group_vars/hcloud/vars.yml);
   override per run with `--extra-vars hcloud_server_type=...` /
   `--extra-vars hcloud_server_location=...`. The SSH key is configured
   via `my_ssh_key_name` in your vault secrets (see step 4 below).

3. **Configure inventory:** Configure `hcloud` as the default inventory
   in [/ansible.cfg](../ansible.cfg)

4. **Configure secrets:** Follow the instructions in
   [Important concepts](./important-concepts.md) to update your secrets
   in `.envrc` and in
   [./inventories/group_vars/all/vars.yml](./inventories/group_vars/all/vars.yml).

5. **Publish HCLOUD_TOKEN to environment:** Publish your API token to the
   `HCLOUD_TOKEN` environment variable, used by the
   [hetzner.hcloud ansible modules][hcloud-modules].

```shell
read -s HCLOUD_TOKEN; export HCLOUD_TOKEN; echo $HCLOUD_TOKEN | wc -c | xargs echo "Number of characters in HCLOUD_TOKEN:"
```

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

- If you want to run Windows, choose
  `--extra-vars provider=aws --extra-vars profile=windows`
- If you want to run Linux, prefer `--extra-vars provider=hcloud`
  (default `profile=basic`)
- If there are no virtual machines available on `hcloud`, then try aws:
  `--extra-vars provider=aws`

After about 1 - 2 minutes, the new server is created. The SSH host key
is trusted automatically into a project-scoped `known_hosts` file (see
[ADR-003](../architecture/decisions/003-ssh-host-key-verification-policy.md))
— no manual confirmation is required.

After that, the setup will take another 10 - 15 minutes.

### Note: Windows requires manual setup

The Windows Server provides a clean installation with SSH, RDP access,
and the Chocolatey package manager. However, unlike the Linux systems,
**it does not include**:

- Pre-installed development applications and tools
- Automated backup/restore of user configurations
- Keyring restoration with saved passwords
- Ready-to-use development environment

**Expected setup time**: 1-2 hours to manually install and configure
your development tools and applications.

**Recommendation**: Use Windows Server when you specifically need
Windows-only applications. For general development work, prefer the
Linux systems which provide a complete, instantly-ready development
environment with automatic configuration restoration.

## Verify the Setup

```shell
# Show the inventory
ansible-inventory --graph
```

The inventory will show the host name for the provisioned instance. The
host name is unique for each provider and platform combination. Have a
look at the table in the [/README.md](../README.md) to see the possible
combinations of provider, platform and host name.

Before executing the other commands in this section, load the configured
key into your SSH agent. The key file depends on how you created it:

- **AWS — key pair created in the console** (downloaded as `.pem`):
  `ssh-add ~/.ssh/YOUR_KEY_FILE.pem`
- **AWS — locally-generated key imported to EC2** or **Hetzner Cloud**
  (Ed25519 or ECDSA key generated with `ssh-keygen`):
  `ssh-add ~/.ssh/id_ansible_ed25519`

Then run the following commands to verify the setup:

```shell
# Check whether the server can be reached
# Linux variant:
ansible linux -m shell -a 'whoami' --extra-vars "ansible_user=galadriel"

# Windows variant using win_command
ansible windows -m win_command -a 'whoami' --extra-vars "ansible_user=Administrator"
```

> [!IMPORTANT]
> You might want to add additional SSH keys to the `authorized_keys`
> files on the server.

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

Connect via an RDP compatible client. For Linux, use the `galadriel`
user, on Windows connect as `Administrator`.

## Delete the VM

To delete the VM and all associated resources, back up your
configuration first — see [Backup and Restore](./backup-restore.md) —
then destroy:

```shell
ansible-playbook playbooks/destroy-vm.yml --extra-vars provider=hcloud --extra-vars hostname=<hostname>
```

Use the same `provider` value used to create the VM, and the `hostname`
shown by `ansible-inventory --graph`.

> [!IMPORTANT]
> Always destroy AWS and Hetzner Cloud instances when no longer needed.
> Monitor the corresponding billing dashboards for unexpected charges.

--

Next: [Work with a Virtual Machine](./work-with-vm.md)

[aws-account]: https://aws.amazon.com
[aws-cli-install]: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
[aws-console-ec2]: https://console.aws.amazon.com/ec2
[hcloud-modules]: https://docs.ansible.com/ansible/latest/collections/hetzner/hcloud/
