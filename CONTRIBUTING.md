# Easily adding and testing a new role

To test your new role:

1. Create a tart based VM: [/docs/create-vm.md](./docs/create-vm.md)
2. Create a `configure-<role-name>.yml` playbook in the repository root directory. Example:

    ```yaml
    ---
    - name: Configure <role-name> role
      hosts: linux
      become: true

      vars:
        ansible_user: "{{ my_ansible_user }}"
        desktop_user_names: "{{ desktop_users | map(attribute='name') | list }}"

      roles:
        - <role-name>
    ```

Then you can easily run only the new role as follows:

```shell
cd test/tart
ansible-playbook ../../configure-<role-name>.yml --skip-tags "not-supported-on-vagrant-arm64"
```
