# Concept: Documentation Updates

## Overview

This improvement aligned the user-facing documentation with the production state of the
infrastructure. The memory-bank reflected a mature multi-provider system — including Windows Server
2025, an enhanced inventory architecture, and streamlined dependency management — while the
published docs still described an earlier development state. Users following the docs hit broken
or outdated instructions.

## Rationale

Three areas of drift motivated the update:

1. **Instruction accuracy** — `docs/user-manual/create-vm.md` referenced manual
   `ansible-galaxy` commands and an older SSH-user name. Users who followed it verbatim
   could not complete a successful setup.
2. **Missing inventory context** — the enhanced unified inventory system (dual keyed groups,
   `platform:` tag semantics, four-tier variable precedence) was not described anywhere in
   user-facing docs.
3. **Production status** — the docs implied the infrastructure was in a development stage
   when three providers were already production-ready.

## Scope

The following updates were delivered as part of this improvement:

### `docs/user-manual/create-vm.md`

- **Streamlined dependencies** — replaced manual `ansible-galaxy` invocations with
  `pip3 install -r requirements.txt && ansible-galaxy collection install -r requirements.yml`.
- **Provider-selection guidance** — added clear guidance for choosing between AWS and Hetzner Cloud.
- **Consistent SSH user** — aligned all SSH-user references to `galadriel` throughout.
- **Instance-name context** — added a reference to the README table for hostname explanations
  (hobbiton, rivendell, moria).
- **Fixed verification commands** — corrected inventory and connectivity verification procedures.
- **Simplified environment setup** — consolidated environment variable configuration using
  `source ./configure.sh`.

### `README.md`

- Added a platform column to the infrastructure table for clearer
  provider / platform / hostname mapping.

### `docs/user-manual/next-steps.md`

- Updated to reflect current progress tracking.

## Acceptance

Users can complete the initial setup workflow by following `docs/user-manual/create-vm.md` alone,
without encountering broken or outdated instructions. The infrastructure overview in `README.md`
accurately communicates the production-ready status of the multi-provider system.

## Related Work

- **Remaining documentation work** — a subset of originally-planned updates was deferred and is
  tracked in `docs/feature-requests/improvement.documentation.updates/` (multi-provider comparison
  guide, cost-analysis doc, inventory-system doc, and updates to several user-manual pages).
- **Consistent provisioning style** — `docs/feature-requests/feat.consistent.provisioning.style/`
  tracks the unimplemented Vagrant Docker unification, which will require further doc updates when
  it ships.
- **Kiro IDE** — `docs/feature-requests/feat.kiro/` tracks unimplemented Kiro-related work.
