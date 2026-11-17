<!-- SPDX-License-Identifier: MIT-0 -->
# swapfile — Design

Non-obvious decisions for the `swapfile` role.

## Opt-In by Group Membership

A host gets a swap file by joining the cross-cutting `swapfile` inventory
group, which also carries its `swapfile_size_gb`. This follows ADR-005
(`docs/architecture/decisions/005-install-only-profile.md`): opting in is
structural, so a host that should have swap but lacks it is visible in the
inventory, not hidden behind a skipped `when:`.

The size is per host because hosts on the same provider need different sizes,
e.g. 2 GB on a 4 GB OpenClaw VM and 16 GB elsewhere. The role has no default
size: a forgotten size fails instead of silently filling a small disk, such as
the default root volume of an AWS VM.

Alternatives rejected: a per-provider default in `group_vars` (one size per
provider, unsafe on small disks), a hand-kept static group (hostnames are
reused from a pool, so the list goes stale), and cloud-init `user_data`
(reaches neither existing VMs nor local test VMs, and sits outside a role).

## Fail Loud Instead of Resizing

An existing swap file of another size stops the role with instructions.
Resizing needs `swapoff`, which moves every swapped page back into memory; on a
host under memory pressure that can trigger the OOM killer. That decision stays
with the operator.

## Idempotency and Adoption

Each step checks the state it would produce: `stat` for the file, `blkid -p`
for the swap signature, `swapon --show` (whole-line match) for activation,
`lineinfile` for the `fstab` line and `ansible.posix.sysctl` for the sysctl
file. The `fstab` line and the `vm.swappiness=10` line match what the operator
used to write by hand, so a hand-configured host reports no changes.

## Recovery from Interrupted Runs

- A failed `fallocate` can leave an empty file. The rescue removes it, so the
  next run does not mistake it for a wrong-size swap file. `creates:` ensures
  the rescue never removes a file that existed before the run.
- A run stopped between allocation and `mkswap` leaves a file without a
  signature. `blkid` reports none and the next run formats it. Any other
  signature, e.g. a filesystem image, stops the role instead of being
  overwritten.

## Free-Space Guard

Before allocating, the role reads the free bytes of the filesystem holding the
swap file with `df` and requires the swap size plus 1 GiB. The margin keeps the
filesystem writable for apt and logs afterwards.

## No Molecule Scenario

Constitution Principle II allows a role that cannot be exercised in a
container to be validated on a VM instead. A rootless Podman container running
`ubuntu:24.04` can `fallocate` and `mkswap`, but `swapon` fails with
`swapon: /swapfile: swapon failed: Operation not permitted`. A partial scenario
would need a test-only switch that skips activation, which is the silent skip
this role avoids, and would leave its core behaviour untested.

## Container Guard

The role gathers its own virtualization facts and refuses a host whose
`virtualization_type` is `docker`, `podman`, `container` or `lxc`. Without the
guard, a container in the group fails late at `swapon` with
`Operation not permitted`, after the file was created; with it, the role stops
before touching the disk. Run against a Podman container, the guard stops with
`virtualization_type 'podman'`. Container types outside the list, such as
`systemd-nspawn` or `openvz`, are not caught; no host here runs them.
