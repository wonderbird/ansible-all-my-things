# Hetzner Cloud Prerequisites

1. **Create cloud project:** You need a cloud project with [Hetzner](https://www.hetzner.com/).

2. **Register SSH key:** Your SSH key must be registered in the cloud project, so that new servers can use it. This will allow `root` login via SSH. It is recommended to set up an AWS account and use it to generate an SSH key pair. See [AWS](./prerequisites-aws.md) documentation.

3. **Configure server properties:** Now configure the `hcloud_` properties for **server size** and the **SSH key ID** in [/provisioners/hcloud.yml](../provisioners/hcloud.yml).

4. **Configure inventory:** Configure `hcloud` as the default inventory in [/ansible.cfg](../ansible.cfg)

5. **Configure secrets:** Finally, follow the instructions in section [Important concepts](./important-concepts.md) to update your secrets in `.envrc` and in [./inventories/group_vars/all/vars.yml](./inventories/group_vars/all/vars.yml).

6. **Publish HCLOUD_TOKEN to environment:** Next, publish your API token to the HCLOUD_TOKEN environment variable, which is used by default by the [hetzner.hcloud ansible modules](https://docs.ansible.com/ansible/latest/collections/hetzner/hcloud/).

```shell
echo -n "hcloud API token: "; read -s HCLOUD_TOKEN; export HCLOUD_TOKEN
```

---

Next: [Work with a Virtual Machine](./work-with-vm.md)
Up: [Create a Virtual Machine](./create-vm.md)
