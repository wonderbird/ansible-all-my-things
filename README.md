# My IT System

Automated setup and updates for my IT system.

- [./inventories/README.md](./inventories/README.md) describes the inventories
- [./playbooks/README.md](./playbooks/README.md) describes the playbooks
- [./test/README.md](./test/README.md) describes how to test the playbooks

## Add a developer vm with Hetzner

### Prerequisites

You need a cloud project with [Hetzner](https://www.hetzner.com/).

Your SSH key must be registered, so that new servers can use it. This will
allow root login via SSH.

### Create the VM

First, configure the `hcloud_` properties for server size and SSH key ID in
[./provisioners/hcloud.yml](./provisioners/hcloud.yml).

Next, publish your API token to the HCLOUD_TOKEN environment variable, which
is used by default by the
[hetzner.hcloud ansible modules](https://docs.ansible.com/ansible/latest/collections/hetzner/hcloud/).

```shell
echo -n "hcloud API token: "; read -s HCLOUD_TOKEN; export HCLOUD_TOKEN
```

Then create the server using the following command:

```shell
ansible-playbook ./provision.yml
```

To verify the setup, execute the `mob moo` command on the server:

```shell
# Source .bash_profile to load the environment variables
ansible dev -m shell -a '. $HOME/.bash_profile; mob moo'
```

## Delete the VM

Remove the SSH host keys from the known hosts file:

```shell
export IPV4_ADDRESS=$(hcloud server list -o json | jq '.[0].public_net.ipv4.ip' | tr -d '"'); echo "IPv4 address: \"$IPV4_ADDRESS\""
ssh-keygen -R $IPV4_ADDRESS
```

To delete the VM including its primary IPv4 address, use the following command:

```shell
hcloud server delete lorien
```

You can verify that the server is deleted in your [Hetzner console project](https://console.hetzner.cloud/projects/10607445/servers).

## References

[boos2025b] S. Boos, “wonderbird/ansible-for-devops: Exercises from the Book Jeff Geerling: ‘Ansible for DevOps’, 2nd Ed., Leanpub, 2023.” Accessed: May 03, 2025. [Online]. Available: [https://github.com/wonderbird/ansible-for-devops](https://github.com/wonderbird/ansible-for-devops)

[geerling2023] J. Geerling, _Ansible for DevOps_, 2nd ed. Leanpub, 2023. Accessed: Apr. 20, 2025. [Online]. Available: [https://www.ansiblefordevops.com/](https://www.ansiblefordevops.com/)

## Acknowledgements

This project uses code, documentation and ideas generated with the assistance of
large language models.
