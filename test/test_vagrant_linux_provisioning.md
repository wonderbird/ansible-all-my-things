# Test: Vagrant Docker Ubuntu Provisioning

## Purpose

Provision a minimal Ubuntu Linux VM using Vagrant, verify it is reachable and configured, and then destroy it.

Depending on whether you want to test the Docker provider or the Tart provider, use the corresponding subdirectory `test/docker` or `test/tart` in the following. The instructions are written for the `test/docker` configuration.

## Manual Test Instructions

### Step 1: Provision the Instance

Provision either a Docker or Tart VM following the corresponding README file:

- [docker/README.md](./docker/README.md)
- [tart/README.md](./tart/README.md)

- This will create an Ubuntu instance using Vagrant or Docker.
- Provisioning may take some 2 minutes.

### Step 2: Verify the Instance

1. **Show the inventory:**

   ```shell
   ansible-inventory --graph
   ```

   - You should see the new instance listed under the `linux` group and under the `vagrant_docker` or `vagrant_tart` group.
   - Note: The instance will always be present, because it is configured statically.

2. **Load your SSH key into the agent:**

   ```shell
   ssh-add ~/.ssh/user@host.pem
   ```

   - Replace `user@host.pem` with your actual private key filename.

3. **Check connectivity and user:**

   ```shell
   # Change to the repository root
   cd ../..

   # Replace HOSTNAME by dagorlad when using Docker or by lorien when using Tart
   source ./configure.sh HOSTNAME

   ansible linux -m shell -a 'whoami' --extra-vars "ansible_user=gandalf" --vault-password-file ansible-vault-password.txt
   ```

   - The output should show `gandalf` as the user.

4. **(Optional) SSH directly to the instance:**

   ```shell
   # For the Tart provider:
   ssh galadriel@$IPV4_ADDRESS
   
   # For the Docker provider:
   ssh galadriel@$IPV4_ADDRESS -p 2223
   ```

   - Replace `galadriel` if your default user is different.

### Step 3: Destroy the Instance

Destroy the instance after verification:

```shell
# Change to the corresponding directory in the test folder:
cd test/docker

# or
cd test/tart

vagrant destroy -f
```

- This will remove the VM.
