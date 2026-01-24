# Docker Container to Run Ansible Scripts

This devcontainer allows to run ansible scripts.

## Status

Work in progress:

- [x] Configure a basic docker container that can run ansible commands.
- [ ] aws environment variables need to be configured
- [ ] Move all documentation from here to Dockerfile and to scripts.

## Container Configuration

At the moment the docker image is minimal. You'll need to configure and set up everything by hand.

### Pulling Current Image from GitHub Container Registry

Once per week, a new version of the image defined by [Dockerfile](./Dockerfile) is built and published to the [GitHub Container Registry](https://github.com/wonderbird/ansible-all-my-things/pkgs/container/ansible-toolchain).

To pull and run that image:

```shell
# Create and run a container, enter container using bash
read -s HCLOUD_TOKEN
docker run --env HCLOUD_TOKEN="$HCLOUD_TOKEN" --name "ansible-toolchain" -it ghcr.io/wonderbird/ansible-toolchain
```

### Build and Run Basic Container Image Locally

The default architecture is Apple Silicon (`arm64`). If you want to build the image for an x86_x64 machine, then specify the build argument `--build-arg ARCH=amd64`.

```shell
# Build the docker image
docker build --tag "ansible-toolchain" .

# Create and run a container, enter container using bash
# Note: This command also works from a shell on a Synology NAS which runs with root privileges
read -s HCLOUD_TOKEN
docker run --env HCLOUD_TOKEN="$HCLOUD_TOKEN" --name "ansible-toolchain" -it ansible-toolchain
```

### Configure SSH Key to Access Created VMs

```shell
# Copy the SSH private key to the container
cd /root
mkdir .ssh
```

If you can use the `docker cp` command to copy files into the container, then from a shell outside the docker container, copy the SSH private key and the AWS signing key into the container:

```shell
docker cp ~/.ssh/YOUR_KEY_FILE.pem ansible-toolchain:/root/.ssh/
docker cp .devcontainer/aws* ansible-toolchain:/root/
```

As an alternative, you can copy-paste the file contents. Inside the docker container, create the files and copy-paste the contents from your local configuration:

```shell
# Your SSH key can be downloaded from AWS as described in /docs/prerequisites-aws.md
vi /root/.ssh/YOUR_KEY_FILE.pem

# The signing key used by the AWS team is located in /.devcontainer
vi /root/awscliv2-public-key.asc
gpg --import /root/awscliv2-public-key.asc
```

In the docker container, finish the configuration:

```shell
# Fix the access rights for the ssh key
chown root:root /root/.ssh/*pem
chmod 600 /root/.ssh/*pem
ls -la /root/.ssh
eval $(ssh-agent)
ssh-add /root/.ssh/YOUR_KEY_FILE.pem
```

### Configure ansible-all-my-things Repository

```shell
# If container is not used as the Dev Container for Visual Studio Code, then
# setup a working directory with the cloned ansible-all-my-things repository
# Usually the container user is root and we will work in /root.
git clone https://github.com/wonderbird/ansible-all-my-things

# Install the ansible tools and dependencies by following the instructions in
# ../docs/create-vm.md
cd /root/ansible-all-my-things
pip3 install --root-user-action=ignore -r requirements.txt
ansible-galaxy collection install -r requirements.yml
```

## Configure Secrets

Now set up the ansible secrets following the documentation in [docs/important-concepts.md](../docs/important-concepts.md).

## Create a VM on hcloud

```shell
ansible-playbook ./provision.yml --extra-vars "provider=hcloud platform=linux"

# Show the VM ip address
hcloud server list
```

More commands and procedure to delete the VM are described in [/docs/create-vm.md](../docs/create-vm.md).

## Leave the Container

Leave the container, but keep the custom configuration for the next use:

```shell
exit
```

## Re-start and Enter the Container

The next time you want to interact with the ansible playbooks, you only need to start the container and enter it:

```shell
docker start ansible-toolchain
docker exec -it ansible-toolchain bash
```
