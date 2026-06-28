# Hetzner Cloud Prerequisites

1. **Create cloud project:** You need a cloud project with
   [Hetzner](https://www.hetzner.com/).

2. **Register SSH key:** Your SSH key must be registered in the cloud
   project, so that new servers can use it. This will allow `root` login
   via SSH. It is recommended to set up an AWS account and use it to
   generate an SSH key pair. See [AWS](./prerequisites-aws.md)
   documentation.

3. **Configure server properties:** Server size and location defaults
   live in
   [/inventories/group_vars/hcloud/vars.yml](../../inventories/group_vars/hcloud/vars.yml);
   override per run with `--extra-vars hcloud_server_type=...` /
   `--extra-vars hcloud_server_location=...`. The SSH key is configured
   via `my_ssh_key_name` in your vault secrets (see step 5 below).

4. **Configure inventory:** Configure `hcloud` as the default inventory
   in [/ansible.cfg](../ansible.cfg)

5. **Configure secrets:** Finally, follow the instructions in section
   [Important concepts](./important-concepts.md) to update your secrets
   in `.envrc` and in
   [./inventories/group_vars/all/vars.yml](./inventories/group_vars/all/vars.yml).

6. **Publish HCLOUD_TOKEN to environment:** Next, publish your API token
   to the HCLOUD_TOKEN environment variable, which is used by default by
   the
   [hetzner.hcloud ansible modules](https://docs.ansible.com/ansible/latest/collections/hetzner/hcloud/).

```shell
read -s HCLOUD_TOKEN; export HCLOUD_TOKEN; echo $HCLOUD_TOKEN | wc -c | xargs echo "Number of characters in HCLOUD_TOKEN:"
```

---

Next: [Work with a Virtual Machine](./work-with-vm.md)
Up: [Create a Virtual Machine](./create-vm.md)
