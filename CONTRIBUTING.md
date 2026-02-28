# Easily adding and testing a new role

To test your new role:

1. Create a tart based VM: [/docs/create-vm.md](./docs/create-vm.md)
2. Insert the new role in the `configure-linux-roles.yml` playbook
3. Comment out all other roles in the `configure-linux-roles.yml` playbook, except the new one.

Then you can easily run only the new role as follows:

```shell
cd test/tart
ansible-playbook ../../configure-linux-roles.yml --skip-tags "not-supported-on-vagrant-arm64"
```

> [!WARNING]
>
> When done, remember to uncomment the other roles in the `configure-linux-roles.yml` playbook.
