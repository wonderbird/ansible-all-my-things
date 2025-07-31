# Test: AWS Ubuntu Provisioning (t3.micro)

## Purpose

Provision a minimal Ubuntu Linux VM on AWS (t3.micro), verify it is reachable and configured, and then destroy it to avoid costs.

## Manual Test Instructions

### Prerequisite: Configure AWS Instance Size

- This test requires valid AWS credentials, a configured SSH key, and a populated vault file. See [/docs/prerequisites-aws.md](../docs/create-vm.md) for more details.
- In [/inventories/group_vars/aws_ec2_linux/vars.yml](../inventories/group_vars/aws_ec2_linux/vars.yml) assign the value `t3.micro` to the variable `aws_default_instance_type`. This instance type is free tier eligible. However, this is subject to AWS account limits.

### Step 1: Provision the Instance

Run the following command from the project root:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./provision.yml --extra-vars "provider=aws platform=linux"
```

- This will create a t3.micro Ubuntu instance on AWS.
- You may be prompted to add the SSH key to your `~/.ssh/known_hosts` file.
- Provisioning may take 10–15 minutes.

### Step 2: Verify the Instance

1. **Show the inventory:**

   ```shell
   ansible-inventory --graph
   ```

   - You should see the new instance listed under the `linux` group.

2. **Load your SSH key into the agent:**

   ```shell
   ssh-add ~/.ssh/user@host.pem
   ```

   - Replace `user@host.pem` with your actual private key filename.

3. **Check connectivity and user:**

   ```shell
   source ./configure.sh rivendell
   ansible linux -m shell -a 'whoami' --extra-vars "ansible_user=gandalf" --vault-password-file=ansible-vault-password.txt
   ```

   - The output should show `gandalf` as the user.

4. **(Optional) SSH directly to the instance:**

   ```shell
   ssh galadriel@$IPV4_ADDRESS
   ```

   - Replace `galadriel` if your default user is different.

### Step 3: Destroy the Instance

To avoid AWS charges, destroy the instance after verification:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./destroy.yml
```

- This will remove the VM and associated resources.
