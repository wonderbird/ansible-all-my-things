# Roadmap: Create and Destroy VM Playbooks

## Why this document exists

The full vision in `prd.md` and `solution-design.md` is large: two unified
playbooks spanning four providers, two profiles, a new profile-group
configuration playbook, dynamic-inventory integration, a hostname pool that
encodes provider by LOTR region, and deletion of the superseded
`provision.yml` / `destroy.yml` / `provisioners/` artefacts.

Delivering that in one pass violates YAGNI and KISS and produces a slice too
large to demo or validate locally. This roadmap breaks the vision into
incremental phases, each delivering value on its own. `spec.md` tracks only the
**current phase**; this file preserves the deferred scope so nothing is lost.

## Guiding principles

- **Vertical slices**: every phase produces a working, demoable capability —
  not a horizontal layer.
- **YAGNI / KISS**: build only the confirmed need; no parameter, branch, or
  abstraction with a single live value.
- **Test locally before cloud** (Constitution III): local providers and local
  validation come before cloud providers.
- **No existing feature breaks**: old playbooks coexist with new ones until a
  provider is fully migrated; superseded artefacts are deleted only at the end.

## Decisions captured

Two contradictions in the source artefacts were resolved during scope
reduction:

- **Single pool vs. provider-encoded names.** `prd.md` specifies per-provider
  pools whose region encodes the provider; the spec's FR-004 specifies a
  **single shared sequential pool**. These are mutually exclusive: a single
  sequential pool hands the next free name to whoever asks next, so a `tart`
  VM can receive a name seeded for the `hcloud` region. The single shared pool
  wins (simpler); provider-encoding (US4) is therefore **not achievable** under
  it and is deferred/likely dropped — see Phase 6.
- **Configuration coupling.** `prd.md` puts changes to `configure-linux.yml`
  out of scope, yet the spec adds a new `configure.yml`. Creation and
  configuration are separated: `create-vm.yml` creates and registers a VM;
  configuration stays with the existing `configure-linux.yml` until a dedicated
  profile-group playbook earns its place — see Phase 5.

## Phases

### Phase 1 — Create / destroy a tart VM, basic profile (CURRENT)

Tracked in `spec.md`. The walking skeleton.

**In scope** for Phase 1:

- `create-vm.yml`: pick the next unused hostname from the shared pool, create a
  `tart` VM, append it to the static inventory under the `basic` group, print
  the hostname. Fail loud with zero infrastructure action when the pool is
  exhausted.
- `destroy-vm.yml hostname=X`: destroy the tart VM, remove its static-inventory
  entry; fail loud on an unknown hostname.
- `provider` defaults to `tart` and `profile` defaults to `basic`; both
  parameters exist but carry a single live value (no branching logic).
- Shared hostname pool (FR-015): ten ordered LOTR names, the existing hosts as
  the first entries. Selection = first name not already in inventory.

**Out of scope (deferred to later phases)**: every other provider, the
`desktop` profile, `configure.yml`, dynamic inventory, provider-encoded names,
and deletion of `provision.yml` / `destroy.yml` / `provisioners/`.

**Value**: an engineer creates and tears down a local tart VM through the new
unified commands, validated on a Mac per Constitution III.

### Phase 2 — Add the docker provider

Extend `create-vm.yml` / `destroy-vm.yml` with a `docker` task file. Docker is
the second **local** provider and the only one validatable on a Linux host
(and in CI), so it precedes the cloud providers.

**Value**: local Linux VM lifecycle through the same commands; unlocks
container-based validation of the create/destroy flow.

### Phase 3 — Add the hcloud provider (first cloud)

Add the `hcloud` task file and **dynamic-inventory integration** (FR-007):
`meta: refresh_inventory` after create; no static-file edits; destroy relies on
the plugin no longer returning the host.

**Value**: first cloud target; proves the dynamic-inventory path end to end.

### Phase 4 — Add the aws provider

Add the `aws` Linux task file, reusing the dynamic-inventory pattern from
Phase 3. Windows VM creation remains out of scope; the existing `moria`
AWS Windows host is untouched.

**Value**: full Linux provider coverage across all four targets.

### Phase 5 — desktop profile + `configure.yml`

Add the `desktop` profile (second inventory group + desktop roles) and the
profile-group configuration playbook (FR-012): `configure.yml` targets all
inventory hosts by default, supports `--limit`, and maps each profile group to
its roles. Reassess whether this supersedes `configure-linux.yml` or wraps it.

**Value**: completes the create → configure lifecycle; `profile` becomes a
meaningful choice rather than a fixed default.

### Phase 6 — Provider-encoded hostnames (reassess)

Revisit US4. Under the single shared pool it is not achievable without
reintroducing per-provider pools. Decide explicitly: either drop it, or accept
the added complexity of per-provider pools with a documented justification
(Constitution IV / Governance). Default expectation: **dropped.**

### Phase 7 — Retire superseded artefacts (migration)

Once all four providers are covered by the new playbooks and existing hosts are
migrated, delete `provision.yml`, `destroy.yml`, `provisioners/`, and the
superseded design docs listed in `solution-design.md`. Update
`docs/user-manual/create-vm.md`; remove all user-facing references to
`provision.yml` / `destroy.yml` (FR-013, FR-014).

**Value**: a single, consistent VM-lifecycle mechanism with no legacy
dispatch paths.

## Phase dependency order

```text
Phase 1 (tart)
   └─> Phase 2 (docker)
          └─> Phase 3 (hcloud, dynamic inventory)
                 └─> Phase 4 (aws)
                        └─> Phase 5 (desktop + configure.yml)
                               └─> Phase 7 (retire legacy)
Phase 6 (provider-encoded names) — independent; reassess any time, default drop
```

Provider ordering after Phase 1 is adjustable; the only hard constraint is that
Phase 7 (deletion) must not run until every provider that `provision.yml` /
`destroy.yml` currently serves has a working replacement.
