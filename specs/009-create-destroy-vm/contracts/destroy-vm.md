# Contract: destroy-vm.yml

## Invocation

```bash
ansible-playbook playbooks/destroy-vm.yml -e hostname=vulcan
```

## Parameters

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `hostname` | Yes | — | Name of the VM to destroy; must match an entry in `inventories/vagrant_tart.yml` |

## Preconditions

- `hostname` is present in `inventories/vagrant_tart.yml` under `all.hosts`
  (otherwise fails immediately before any action)
- Vagrant is installed on the control node

## Postconditions (on success)

- The Tart VM is stopped and deleted
- All references to `hostname` are removed from `inventories/vagrant_tart.yml`
  (groups `all`, `linux`, `vagrant_tart`)

## Failure modes

| Condition | Behaviour |
|-----------|-----------|
| `hostname` not in inventory | Fails immediately with actionable error; no VM or infra action taken |
| VM absent from platform but present in inventory | Attempts Vagrant destroy; if VM already gone, logs a warning and removes stale inventory entry |
| `hostname` not provided | Ansible variable undefined error at task evaluation |

## Idempotency

Partially idempotent: running destroy twice for the same hostname fails on the
second run (hostname no longer in inventory) rather than silently succeeding.
This is intentional — a missing hostname is always an error (FR-010).
