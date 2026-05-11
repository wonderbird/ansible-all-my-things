# PRD: Documentation Updates (Remaining)

## Problem

The documentation-update improvement shipped the first batch of user-manual
updates (create-vm.md, README.md platform column, next-steps.md). Several
documents that should reflect the current production state of the
infrastructure are still missing or incomplete.

## Goal

Finish bringing user-facing documentation in line with the production-ready
multi-provider system, covering the specific pages and guides that were not
addressed in the first batch.

## Scope

### Documents to create

1. **Multi-provider comparison guide** — a concise reference explaining the
   differences between Hetzner Cloud and AWS (Linux and Windows), covering
   connection method, default user, package manager, instance type, storage,
   cost, authentication, and provisioning time. Intended audience: a developer
   choosing which provider to use for a new VM.

2. **Cost-analysis doc** — a reference documenting the approximate monthly
   cost per VM (hobbiton ~$4/mo, rivendell ~$8–10/mo, moria ~$60/mo) and the
   trade-offs between always-on (Hetzner) and on-demand (AWS) billing models.

3. **Inventory system doc** — an explanation of the unified inventory
   architecture: dual-keyed groups, the `platform:` tag, the 4-tier variable
   precedence rule (all → platform → provider → provider_platform), and the
   `@all` group graph. Helps operators understand how hosts are grouped and
   how variables are resolved.

### Documents to update

4. **`docs/user-manual/prerequisites-aws.md`** — review and update to reflect
   the current AWS environment (VPC, security-group `ansible-sg` shared
   between Linux and Windows, dynamic IP detection via ipinfo.io, vault-based
   credential storage).

5. **`docs/user-manual/important-concepts.md`** — review and update to include
   the unified inventory model and the `platform:` tag concept, so readers
   understand the abstraction before they run playbooks.

6. **`docs/user-manual/work-with-vm.md`** — review and update to cover
   day-to-day operations with all three production VMs (hobbiton, rivendell,
   moria) including Windows-specific workflows (RDP, Chocolatey).

## Out of scope

- **Windows Server full user-manual** — descoped. The Windows Server setup
  requires significant manual steps that make a comprehensive automated guide
  impractical at this time. Covered by the `moria` VM entry in cost-analysis
  and prerequisites, not a standalone guide.

- **Content already absorbed by this refactor** — inventory-system
  documentation that has been folded into `docs/techContext.md` as part of
  beads-4fv does not need a separate standalone doc if it is already
  adequately covered there. Executor must verify before creating.

## Acceptance Criteria

1. Multi-provider comparison guide exists at a stable path under
   `docs/user-manual/` or `docs/architecture/`; passes `review-documentation-here`
   skill; cross-links from `docs/techContext.md`.

2. Cost-analysis doc exists; contains per-VM cost entries for hobbiton,
   rivendell, and moria; passes `review-documentation-here` skill.

3. Inventory-system doc exists (or its content is verifiably present in
   `docs/techContext.md`); covers dual-keyed groups, `platform:` tag,
   4-tier precedence, `@all` group graph.

4. `docs/user-manual/prerequisites-aws.md` reflects the current
   `ansible-sg` shared security-group and vault-based credential model.

5. `docs/user-manual/important-concepts.md` mentions the unified inventory
   and `platform:` tag.

6. `docs/user-manual/work-with-vm.md` covers all three production VMs
   including Windows-specific notes.

7. No status tags (`✅`, `⏳`, `❌`, `COMPLETED`, `IN PROGRESS`) in any
   of the above documents.

8. All documents use SSH user `galadriel` (not `gandalf`).
