# Docker Container to Run Ansible Scripts

This devcontainer allows to run ansible scripts.

## Status

Work in progress:

- [x] Configure a basic docker container that can run ansible commands.
- [ ] aws environment variables need to be configured
- [ ] Move all documentation from here to Dockerfile and to scripts.

## Pull and Run Current Image

Once per week, a new version of the image defined by [Dockerfile](./Dockerfile) is built and published to the [GitHub Container Registry](https://github.com/wonderbird/ansible-all-my-things/pkgs/container/ansible-toolchain).

```shell
docker pull ghcr.io/wonderbird/ansible-toolchain
```

## Image configuration

The following environment variables are supported:

- `HCLOUD_TOKEN`: your Hetzner cloud API token
- `ANSIBLE_VAULT_PASSWORD`: password to encrypt the secrets in ansible vault
- `BACKUP_DIR` (optional): If this variable is not empty, then your backups are copied into that directory. For example, use  `/backup`

Furthermore the following bind mounts are supported:

- `/root/.ssh/YOUR_KEY_FILE.pem`: your private key registered with Hetzner cloud and aws. See [/docs/prerequisites-aws.md](../docs/prerequisites-aws.md).
- `/root/ansible-all-my-things/inventories/group_vars/all/vault.yml`: encrypted ansible configuration. See [docs/important-concepts.md](../docs/important-concepts.md).
- `/backup`: folder containing and receiving backups

## Create container

Once you have the sources of the bind mounts ready, you can run the container as follows:

```shell
read -p "Enter HCLOUD_TOKEN: " -s HCLOUD_TOKEN; export HCLOUD_TOKEN; echo; \
read -p "Enter ANSIBLE_VAULT_PASSWORD: " -s ANSIBLE_VAULT_PASSWORD; export ANSIBLE_VAULT_PASSWORD; echo

docker run --mount type=bind,source="/path/to/backup",target=/backup \
           --mount type=bind,source="/path/to/YOUR_KEY_FILE.pem",target=/root/.ssh/YOUR_KEY_FILE.pem \
           --mount type=bind,source="/path/to/vault.yml",target=/root/ansible-all-my-things/inventories/group_vars/all/vault.yml \
           --env HCLOUD_TOKEN="$HCLOUD_TOKEN" \
           --env ANSIBLE_VAULT_PASSWORD="$ANSIBLE_VAULT_PASSWORD" \
           --env BACKUP_DIR="/backup" \
           --name "ansible-toolchain" \
           -it ghcr.io/wonderbird/ansible-toolchain
```

## Create a VM on hcloud

```shell
# Ensure that the ssh-key is loaded into the agent
eval $(ssh-agent) \
  && ssh-add /root/.ssh/YOUR_KEY_FILE.pem; \
  ssh-add -l

ansible-playbook ./provision.yml --extra-vars "provider=hcloud platform=linux"

# Show the VM ip address
hcloud server list
```

More commands and procedure to delete the VM are described in [/docs/create-vm.md](../docs/create-vm.md).

## Re-start and Enter the Container

The next time you want to interact with the ansible playbooks, you only need to start the container and enter it:

```shell
docker start ansible-toolchain
docker exec -it ansible-toolchain bash
```
