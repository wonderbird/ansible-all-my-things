# Developer Setup

## Prerequisites: Spec-Kit

[GitHub Spec Kit](https://github.com/github/spec-kit) and [Claude Code](https://claude.ai)
can be used to extend this application. Consider installing the corresponding
tools as described in the [Spec Kit Getting Started Guide](https://github.com/github/spec-kit).

## Testing a role with Molecule (preferred)

Roles that can be exercised in a container are tested with Molecule. Activate
the Python virtual environment first, then run from the role directory:

```shell
cd roles/<role-name>
molecule test
```

This runs the full lifecycle: create → prepare → converge → idempotence →
verify → destroy. All phases MUST pass before committing.

## Testing a role with Vagrant (fallback for full-VM roles)

Roles that require a full VM (e.g., desktop environment, display managers,
hardware drivers) are tested against a local Vagrant/Tart VM:

1. Create a Tart-based VM: [/docs/create-vm.md](./docs/create-vm.md)
2. Insert the new role in the `configure-linux-roles.yml` playbook.
3. Comment out all other roles in `configure-linux-roles.yml`, except the
   new one.

Then run only the new role:

```shell
cd test/tart
ansible-playbook ../../configure-linux-roles.yml --skip-tags "not-supported-on-vagrant-arm64"
```

> [!WARNING]
>
> When done, remember to uncomment the other roles in the
> `configure-linux-roles.yml` playbook.
