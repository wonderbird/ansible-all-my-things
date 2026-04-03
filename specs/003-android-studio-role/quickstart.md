# Quickstart: android_studio role

## Prerequisites

- AMD64 Ubuntu VM reachable from the Ansible control machine
- The VM is already provisioned with `setup-users.yml` (user accounts exist)
- snapd is running on the target VM (standard Ubuntu)
- Outbound internet access on the VM (snap downloads from the Snap Store)

## Isolated role test (Constitution §III)

Edit `configure-linux-roles.yml` to include only the `android_studio` role:

```yaml
roles:
  - role: android_studio
    tags: not-supported-on-vagrant-arm64
```

Then run the playbook:

```bash
ansible-playbook configure-linux.yml --limit hobbiton
```

Verify on the target VM:

```bash
snap list android-studio
```

Expected: one row showing `android-studio` with a revision and channel.

## Idempotency test

Run the playbook a second time without changes. All `android_studio` tasks
must report `ok` or `skipped` — never `changed`.

## ARM64 skip test

Run with the skip tag active:

```bash
ansible-playbook configure-linux.yml \
  --limit hobbiton \
  --skip-tags not-supported-on-vagrant-arm64
```

All `android_studio` role tasks must be skipped; the playbook must complete
without errors.

## SDK validation test (SC-005)

On a freshly provisioned VM, launch Android Studio and step through the
Standard setup wizard. The wizard should complete within 30 seconds,
indicating no major downloads are pending.

## SDK idempotency test (US4-AC2)

Run the playbook a second time. All SDK pre-provisioning tasks must
report `ok` or `skipped` — never `changed`.

## SDK ARM64 skip test (US4-AC3)

Run with the skip tag active (same command as the ARM64 skip test
above). All SDK pre-provisioning tasks must also be skipped.

## Restore configure-linux-roles.yml

After testing, restore `configure-linux-roles.yml` to include all roles in
the correct order.
