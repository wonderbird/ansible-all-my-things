# Test: Vagrant Docker Ubuntu Provisioning

## Purpose
Provision a minimal Ubuntu Linux VM on Vagrant Docker, verify it is reachable and configured, and then destroy it.

## Manual Test Instructions

### Step 1: Provision the Instance
Run the following command from the project root:

```shell
cd test/docker
vagrant up
```

- This will create an Ubuntu instance using Vagrant and Docker.
- Provisioning may take some 2 minutes.

### Step 2: Verify the Instance

1. **Show the inventory:**
   ```shell
   ansible-inventory --graph
   ```
   - You should see the new instance listed under the `linux` group.
   - Note: The instance will always be present, because it is configured statically.

2. **Load your SSH key into the agent:**
   ```shell
   ssh-add ~/.ssh/user@host.pem
   ```
   - Replace `user@host.pem` with your actual private key filename.

3. **Check connectivity and user:**
   ```shell
   source ../../configure.sh dagorlad
   ansible linux -m shell -a 'whoami' --extra-vars "ansible_user=gandalf" --vault-password-file=../../ansible-vault-password.txt
   ```
   - The output should show `gandalf` as the user.

4. **(Optional) SSH directly to the instance:**
   ```shell
   ssh galadriel@$IPV4_ADDRESS -p 2223
   ```
   - Replace `galadriel` if your default user is different.

### Step 3: Destroy the Instance
Destroy the instance after verification:

```shell
vagrant destroy -f
```

- This will remove the VM.
