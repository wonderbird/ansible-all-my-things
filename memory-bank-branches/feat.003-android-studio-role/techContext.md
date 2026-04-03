# Tech Context

- **Stack**: YAML, Ansible 2.19+, `community.general`
  collection (already in `requirements.yml`)
- **Target**: Ubuntu Linux, AMD64 only; snapd pre-installed
- **Testing**: Manual on Hetzner Cloud VM `hobbiton` (AMD64);
  Vagrant VMs in this project are ARM64 and skip this role.
  See `specs/003-android-studio-role/quickstart.md`
- **Lint**: markdownlint on all spec artefacts and memory bank

## SDK automation — key technical facts

Details in plan.md SDK Design and research.md Decisions 4–6.
Only non-obvious facts listed here:

- Snap-bundled JBR provides Java 17+ at
  `/snap/android-studio/current/jbr`
- Snap does NOT expose `sdkmanager`; cmdline-tools must be
  bootstrapped separately
- cmdline-tools ZIP has a top-level `cmdline-tools/` dir —
  extract + rename needed (see plan.md)
- `community.general.android_sdk` requires explicit package
  versions — no symbolic `latest` token; detect via
  `sdkmanager --list` at runtime
