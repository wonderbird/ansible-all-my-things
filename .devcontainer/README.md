# Docker Container to Run Ansible Scripts

This devcontainer allows to run ansible scripts.

## Status

Work in progress:

- [ ] Configure a basic docker container that can run ansible commands.

## Container Configuration

At the moment the docker image is minimal. You'll need to configure and set up everything by hand.

### Configure and Run Basic Container Image

```shell
. ./scripts/configure-hcloud-token.sh

# Build the docker image
docker build --tag "custom-ansible" .

# Create and run a container, enter container using bash
# The environment variable HCLOUD
docker run --env HCLOUD_TOKEN="$HCLOUD_TOKEN" --name "custom-ansible" -it custom-ansible /bin/bash
```

### Install AWS CLI

Install the AWS CLI and set up AWS as described in [docs/prerequisistes-aws.md](../docs/prerequisistes-aws.md), which delegates the installation to https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html#getting-started-install-instructions

```shell
# Install some tools
apt-get update
apt-get install -y --no-install-recommends jq vim

# Install AWS CLI
export ARCH=aarch64
# export ARCH=x86_64

mkdir -p /tmp/awscli
cd /tmp/awscli
curl "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip" -o "awscliv2.zip"
gpg --import /root/awscliv2-public-key.asc
curl -o awscliv2.sig https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip.sig
gpg --verify awscliv2.sig awscliv2.zip
unzip awscliv2.zip
./aws/install
cd ..
rm -rf /tmp/awscli
aws --version
```

### Install hcloud CLI

```shell
# Install hcloud CLI
export ARCH=arm64
# export ARCH=amd64

mkdir -p /root/hcloud
cd /root/hcloud
wget https://github.com/hetznercloud/cli/releases/download/v1.60.0/hcloud-linux-$ARCH.tar.gz -O "hcloud.tar.gz"
tar -xzvf hcloud.tar.gz
rm hcloud.tar.gz
ln -s /root/hcloud/hcloud /usr/local/bin/hcloud 
cd ~
hcloud
```

### Configure SSH Key to Access Created VMs

```shell
# Copy the SSH private key to the container
cd ~
mkdir .ssh
```

In a shell outside the docker container, copy the SSH private key and the AWS signing key into the container:

```shell
docker cp ~/.ssh/YOUR_KEY_FILE.pem custom-ansible:/root/.ssh/
docker cp .devcontainer/aws* custom-ansible:/root/
```

Then back in the docker container, finish the configuration:

```shell
# Fix the access rights for the ssh key
cd ~
chown root:root .ssh/*pem
chmod 600 .ssh/*pem
ls -la .ssh
eval $(ssh-agent)
ssh-add ~/.ssh/YOUR_KEY_FILE.pem
```

### Configure ansible-all-my-things Repository

```shell
# If container is not used as the Dev Container for Visual Studio Code, then
# setup a working directory with the cloned ansible-all-my-things repository
# Usually the container user is root and we will work in /root.
git clone https://github.com/wonderbird/ansible-all-my-things
cd ~/ansible-all-my-things
```

Now set up the ansible secrets following the documentation in [docs/important-concepts.md](../docs/important-concepts.md).

Next, install the ansible tools and the dependencies by following the instructions in [docs/create-vm.md](../docs/create-vm.md):

```shell
cd ~/ansible-all-my-things
pip3 install --root-user-action=ignore -r requirements.txt
ansible-galaxy collection install -r requirements.yml
```

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
docker start custom-ansible
docker exec -it custom-ansible /bin/bash
```
