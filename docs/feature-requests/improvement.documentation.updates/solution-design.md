# Solution Design: Documentation Updates (Remaining)

## Approach

Complete the remaining documentation work one document at a time, validating
each with the `review-documentation-here` skill before moving to the next.
Prefer updating existing files over creating new ones where the content fits
naturally.

## Dependencies

This feature-request is related to the beads-4fv refactor
(`docs/feature-requests/improvement.documentation.updates/`). That refactor
folds inventory-system content into `docs/techContext.md`. Before starting
step 3 below, verify whether `docs/techContext.md` already provides adequate
inventory-system coverage. If it does, step 3 reduces to a cross-link rather
than a new document.

The multi-provider comparison content (step 1) overlaps with content in
`docs/architecture/solution-strategy.md`. Read that file first to avoid
duplication.

## Steps

### Step 1: Multi-provider comparison guide

**Source of truth:** `docs/techContext.md` (provider-differences table, per-VM
specs), `docs/architecture/solution-strategy.md` (provider-strategy rationale).

**Deliverable:** A new file at `docs/user-manual/provider-comparison.md`
(or equivalent path) containing a three-column reference table (AWS Linux /
AWS Windows / Hetzner Linux) covering: connection method, default user,
package manager, instance type, storage, cost, authentication, provisioning
time, and inventory groups.

**Acceptance:** File exists; table is accurate against current infrastructure;
`review-documentation-here` skill passes; `docs/techContext.md` cross-links
to it.

### Step 2: Cost-analysis doc

**Source of truth:** Per-VM specs in `docs/techContext.md` (hobbiton: cx22
Helsinki ~$4/mo; rivendell: t3.micro/small eu-north-1 ~$8–10/mo; moria:
t3.large eu-north-1 ~$60/mo).

**Deliverable:** A new file at `docs/user-manual/cost-analysis.md` covering
per-VM monthly cost, always-on vs. on-demand billing models (Hetzner vs.
AWS), and guidance on stopping/terminating VMs to control cost.

**Acceptance:** File exists; per-VM entries present; billing-model trade-off
explained; `review-documentation-here` skill passes.

### Step 3: Inventory system doc

**Pre-check:** Verify that `docs/techContext.md` already covers unified
inventory (dual-keyed groups, `platform:` tag, 4-tier precedence, `@all`
group graph) after the beads-4fv rewrite.

- If covered adequately: add a cross-link from `docs/user-manual/important-concepts.md`
  to the relevant section of `docs/techContext.md`. No new file needed.
- If not covered adequately: create `docs/user-manual/inventory-system.md`
  containing the directory tree, `@all` group graph, `platform:` tag
  semantics, and 4-tier precedence rule.

**Acceptance:** Either a cross-link exists or a standalone doc exists; a new
operator can understand how hosts are grouped and how variables are resolved
without reading source code.

### Step 4: Update `docs/user-manual/prerequisites-aws.md`

**Source of truth:** Current file content + `docs/techContext.md` for the
`ansible-sg` shared security-group (port 22 + 3389, IP-restricted via
`{{ current_public_ip }}/32`, dynamic IP via ipinfo.io) and vault-based
credential model.

**Check:** Read the current file and identify any gaps against the current
infrastructure. Add or update sections for:

- `ansible-sg` shared security group (used by both Linux and Windows instances)
- Dynamic public-IP detection via ipinfo.io
- Vault-encrypted credential storage (`ANSIBLE_VAULT_PASSWORD_FILE`)

**Acceptance:** File updated; no outdated instructions; `review-documentation-here`
skill passes.

### Step 5: Update `docs/user-manual/important-concepts.md`

**Check:** Read the current file and identify whether unified inventory and
`platform:` tag are explained. Add a section or paragraph covering:

- The unified inventory model (single `inventories/` tree, provider-keyed
  dynamic sources)
- The `platform:` tag and why it exists (provider-agnostic group membership)
- Where to find the 4-tier precedence rule (cross-link to techContext or
  inventory-system doc)

**Acceptance:** File updated; `review-documentation-here` skill passes.

### Step 6: Update `docs/user-manual/work-with-vm.md`

**Check:** Read the current file and identify which VMs are covered. Add or
update sections for:

- Windows-specific workflow on `moria`: connect via RDP (port 3389,
  IP-restricted), run Ansible via SSH + PowerShell shell, package management
  via Chocolatey
- Confirm hobbiton and rivendell workflows are current (SSH user `galadriel`)

**Acceptance:** File covers all three production VMs; Windows workflow present;
`review-documentation-here` skill passes.

## Risks

- **Parallel rewrite of top-level docs (beads-4fv):** `docs/techContext.md`
  is being rewritten as part of this same refactor. Coordinate: complete steps
  3–6 after the beads-4fv rewrite of `docs/techContext.md` is committed, so
  the cross-links point to stable content.

- **Windows Server doc descoped:** The decision to deprioritise a full Windows
  Server user-manual (due to manual setup requirements) means step 6 adds
  only the operational workflow notes, not a full setup guide. Do not scope-
  creep into Windows provisioning instructions.

- **Duplicate content with solution-strategy.md:** The multi-provider
  comparison (step 1) overlaps with `docs/architecture/solution-strategy.md`.
  Check that file first; prefer extending it over creating a separate guide if
  the audience and purpose align.
