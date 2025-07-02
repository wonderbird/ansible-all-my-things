# Create a developer VM with Hetzner

## Prerequisites

1. **Create cloud project:** You need a cloud project with [Hetzner](https://www.hetzner.com/).

2. **Register SSH key:** Your SSH key must be registered in the cloud project, so that new servers can use it. This will allow `root` login via SSH.

3. **Configure server properties:** Now configure the `hcloud_` properties for **server size** and the **SSH key ID** in [/provisioners/hcloud.yml](../provisioners/hcloud.yml).

4. **Configure inventory:** Configure `hcloud` as the default inventory in [/ansible.cfg](../ansible.cfg)

5. **Configure secrets:** Finally, follow the instructions in section [Important concepts](./important-concepts.md) to update your secrets in [./ansible-vault-password.txt](./ansible-vault-password.txt) and in [./playbooks/vars-secrets.yml](./playbooks/vars-secrets.yml).

6. **Publish HCLOUD_TOKEN to environment:** Next, publish your API token to the HCLOUD_TOKEN environment variable, which is used by default by the [hetzner.hcloud ansible modules](https://docs.ansible.com/ansible/latest/collections/hetzner/hcloud/).

```shell
echo -n "hcloud API token: "; read -s HCLOUD_TOKEN; export HCLOUD_TOKEN
```

## Create the VM

Create the server using the following command:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt ./provision.yml
```

You will be asked to add the SSH key of the new server to your local
`~/.ssh/known_hosts` file.

After that, the setup will take some 10 - 15 minutes.

## Verify the setup

```shell
# Show the inventory
ansible-inventory --graph
```

Before executing the other commands in this section, load the configured key into your SSH agent:

```shell
# Check whether the server can be reached
ansible dev -m shell -a 'whoami' --extra-vars "ansible_user=gandalf"

# Source .bash_profile to load the environment variables
ansible dev -m shell -a '. $HOME/.bash_profile; mob moo' --extra-vars "ansible_user=gandalf"
```

>[!IMPORTANT]
> You might want to add additional SSH keys to the `authorized_keys` files on
> the server.

## Delete the VM

To delete the VM, use the following command:

```shell
# Backup your configuration
ansible-playbook --vault-password-file ansible-vault-password.txt ./backup.yml

# Destroy
ansible-playbook ./destroy.yml
```

You can verify that the server is deleted in your [Hetzner console project](https://console.hetzner.cloud/projects/10607445/servers) or using the `hcloud` CLI:

```shell
hcloud server list
```
