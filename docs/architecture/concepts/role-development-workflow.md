# Role development workflow

## Testing a role with Molecule (preferred)

Roles that can be exercised in a container are tested with Molecule. Activate
the Python virtual environment first.

From the role directory:

```shell
cd roles/<role-name>
molecule test
```

From the project root:

```shell
./scripts/test-molecule-all.sh
```

Both forms run the full lifecycle: create → prepare → converge → idempotence →
verify → destroy. All phases MUST pass before committing.

## Running a single role on a live host

```shell
./scripts/run-role.sh <host> <role>
```

`<host>` must match an inventory entry. The script uses `my_ansible_user` and
`desktop_users` variables from inventory, so those must be defined.

## Testing a role with Vagrant (fallback for full-VM roles)

Roles that require a full VM (e.g., desktop environment, display managers,
hardware drivers) are tested against a local Vagrant/Tart VM:

1. Create a Tart-based VM: [/docs/create-vm.md](./docs/create-vm.md)
2. Insert the new role in the `configure-linux-roles.yml` playbook.
3. Comment out all other roles in `configure-linux-roles.yml`, except the
   new one.

```shell
cd test/tart
ansible-playbook ../../configure-linux-roles.yml --skip-tags "not-supported-on-vagrant-arm64"
```

> [!WARNING]
>
> When done, remember to uncomment the other roles in the
> `configure-linux-roles.yml` playbook.
