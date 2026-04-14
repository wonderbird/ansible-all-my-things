# Review Findings: branch `006-podman-rootless-role`

Reviewed by: technical-coach skill (Claude Code)
Date: 2026-04-12
Scope: diff of `006-podman-rootless-role` vs. `main`

## MEDIUM

### M1 — `roles/podman/` has no Molecule scenario, with no documented exemption

Constitution Principle II (v1.2.0, amended on this branch) mandates a
Molecule test scenario for every role that can be exercised in a container.
The podman role has no `molecule/` directory.

A legitimate reason exists — installing `podman` inside a Molecule-managed
Podman container is the "podman-in-podman" problem requiring privileged mode
not enabled by the driver — but this reason is not recorded anywhere. The
`lineinfile` and `apt` tasks are testable in a container even if
`podman system migrate` must be skipped or mocked.

The acceptance test (T020) was also run on the cloud VM `hobbiton` rather
than a local VM, which brushes against Principle III ("validate locally before
cloud").

**Action**: Document the exemption in `roles/podman/DESIGN.md` (or add a
partial Molecule scenario that covers the `apt` and `lineinfile` tasks with
`podman system migrate` skipped via a variable guard).

### M2 — `prepare.yml` `apt-get update -qq` diverges from rule 340 template

Rule `340-molecule-testing.mdc` (created on this branch) shows the canonical
bootstrap as `apt-get update` (no flags). The actual `prepare.yml` uses
`apt-get update -qq`. `techContext.md` documents `apt-get update -qq` (flag
after subcommand) as potentially failing on Ubuntu 24.04 apt 2.7.x.

T023 passed despite this, so the container image may be more lenient. However,
the canonical template — the thing future role authors will copy — should be
safe and self-consistent.

**Action**: Align the template in rule 340 with the implementation (`-qq`), or
align the implementation with the template (remove `-qq`). The template is the
safer reference; prefer removing the flag from `prepare.yml`.

## LOW

### L1 — `podman/meta/main.yml` missing `namespace` and `role_name`

The java role required `namespace: wonderbird` and `role_name: java` after
Molecule prerun failed with a Galaxy naming error. The podman role's
`meta/main.yml` was written without these fields.

The error does not surface today because the podman role has no Molecule
scenario, but the moment one is added the prerun will fail for the same reason.

**Action**: Add `namespace: wonderbird` and `role_name: podman` to
`roles/podman/meta/main.yml`.

### L2 — SDKMAN installer left in `/tmp/` indefinitely with no integrity check

The `Remove sdkman installer` task was correctly removed to fix idempotence.
However, `/tmp/sdkman-install.sh` (mode `0755`, downloaded from the internet)
now persists on disk across all subsequent runs, and the `ansible.builtin.get_url`
task carries no `checksum:` parameter.

**Action**: Register the result of the sdkman install task and conditionally
delete the script only when install actually ran (`when: install_result is
changed`). This restores cleanup without breaking idempotence.

## INFO

### I1 — `update_cache` implicit vs. explicit in podman apt task

The podman `apt` task omits `update_cache` (defaults to `no`). The java role's
new prerequisites task explicitly declares `update_cache: false`. Both behave
identically; the explicit form is more readable and consistent with the
emerging project pattern.

**Action**: Add `update_cache: false` to the podman `apt` task.

### I2 — Play-level `become` interplay in `prepare.yml` lacks a comment

`become: true` is declared at play level; the two `raw` tasks override it with
`become: false` because sudo is not yet installed. The logic is sound but
subtle — a future reader may "fix" the `become: false` as an apparent mistake.

**Action**: Add a short inline comment to the raw tasks, e.g.:
`# sudo not yet installed — must not use become`.

## What Is Well Done

- `lineinfile` idempotency strategy for `/etc/subuid`/`/etc/subgid` is correct
  and well-documented in `DESIGN.md`.
- `changed_when: false` on `podman system migrate` is the right guard.
- `requirements.txt` change from `ansible>=4.0.0` to `ansible-core>=2.19.0`
  is precise; `community.general` is safely covered by `requirements.yml`.
- The java role Molecule scenario correctly separates `raw` bootstrap tasks
  and uses `ansible_facts['env']` rather than the removed `ansible_env`.
- Constitution amendment and rule 340 creation are coherent with each other
  and with the project's direction.
- `configure-linux-roles.yml` ordering (`podman` first) is correct for a
  dependency-providing role.
