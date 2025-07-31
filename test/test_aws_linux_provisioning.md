# Test: AWS Ubuntu and Windows Provisioning

## Purpose

Provision an Ubuntu Linux VM and a Windows VM on AWS, verify they are reachable and configured, and then destroy them to avoid costs.

## Manual Test Instructions

### Prerequisite: Configure AWS Instance Size

- This test requires valid AWS credentials, a configured SSH key, and a populated vault file. See [/docs/prerequisites-aws.md](../docs/create-vm.md) for more details.
- For the **Linux** instance, select `t3.micro` as `aws_default_instance_type` in [/inventories/group_vars/aws_ec2_linux/vars.yml](../inventories/group_vars/aws_ec2_linux/vars.yml). This instance type is free tier eligible. However, this is subject to AWS account limits.
- For the **Windows** instance, select `t3.large` as `aws_default_instance_type` in [/inventories/group_vars/aws_ec2_windows/vars.yml](../inventories/group_vars/aws_ec2_windows/vars.yml).

### Step 1: Provision the Instance

Run the following commands from the project root:

```shell
# Start Linux instance "rivendell"
ansible-playbook --vault-password-file ansible-vault-password.txt ./provision.yml --extra-vars "provider=aws platform=linux"

# Wait until the security group has been configured

# Start Windows instance "moria"
ansible-playbook --vault-password-file ansible-vault-password.txt ./provision.yml --extra-vars "provider=aws platform=windows"

# It will take some minutes until the SSH host key is shown
```

- This will create instances for the different platforms on AWS.
- You may be prompted to add the SSH key to your `~/.ssh/known_hosts` file.
- Provisioning may take 10–15 minutes for each VM.

### Step 2: Verify the Instance

#### 1. Show the inventory:

```shell
ansible-inventory --graph
```

- You should see the new instances listed under the `linux` group and under the `windows` group, respectively.

#### 2. Load your SSH key into the agent:

```shell
ssh-add ~/.ssh/user@host.pem
```

Replace `user@host.pem` with your actual private key filename.

#### 3. Check connectivity and user:

```shell
source ./configure.sh rivendell
ansible rivendell -m shell -a 'whoami' --extra-vars "ansible_user=gandalf" --vault-password-file=ansible-vault-password.txt

source ./configure.sh moria
ansible moria -m win_command -a 'whoami' --extra-vars "ansible_user=Administrator" --vault-password-file ansible-vault-password.txt
```

The output should show `gandalf` for Linux and `administrator` for Windows as the user.

#### 4. (Optional) SSH and RDP directly to the instance:

```shell
# For the Linux instance
ssh -L 3389:localhost:3389 -L 8022:localhost:22 galadriel@$IPV4_ADDRESS

# Now you can connect to localhost using RDP and the credentials for galadriel

# For the Windows instance
ssh -L 3389:localhost:3389 -L 8022:localhost:22 Administrator@$IPV4_ADDRESS

# Now you can connect to localhost using RDP and the credentials for Administrator
```

Replace `galadriel` if your default user is different.

### Step 3: Destroy the Instance

To avoid AWS charges, destroy the instance after verification:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./destroy.yml
```

This will remove the VM and associated resources.
