<!-- SPDX-License-Identifier: MIT-0 -->

# shellcheck role — Design Notes

## Distribution Package, Unpinned

The role installs the `shellcheck` apt package unpinned (`state: present`),
following the `vim` role's precedent.

The alternative is the upstream static binary from the ShellCheck GitHub
releases, pinned in `defaults/main.yml` with a per-architecture SHA-256 and
registered with the version-update mechanism. It was rejected for now:

- The distribution package is signed by the Ubuntu archive, receives security
  updates through the normal apt upgrade path, and needs no checksum pins.
- Nothing in this repository requires a specific ShellCheck version or a check
  only newer releases ship, so YAGNI (Principle IV) favours the simpler
  install.

The cost is that the installed version follows the Ubuntu release and lags
upstream. Switch to the pinned upstream binary when a newer check, or
agreement with a ShellCheck version pinned elsewhere (for example in CI),
becomes a requirement.

## No Version-Update Wiring

The version-update mechanism under `playbooks/update-versions/` refreshes pins
in `defaults/main.yml`. The role pins nothing, so there is nothing to register.
