# Findings: Desktop Profile Unification Strategy (Phase 5a)

## Context

`roadmap.md` Phase 5/6 was rewritten to describe a "step 0" unification
strategy for the `desktop` profile: instead of extracting roles from the
legacy desktop stack first, fold the legacy `configure-linux-roles.yml`
role list and the three legacy desktop playbooks
(`setup-desktop.yml`, `setup-keyring.yml`, `setup-desktop-apps.yml`)
**verbatim** into `configure-profile-roles.yml` / `configure-profile.yml`
under a new `profile=desktop` branch. This is an explicit, accepted
exception to Constitution Principle II (Role-First Organisation), taken to
unblock unifying the VM provisioning path (one `create-vm.yml` per provider,
no parallel `provision.yml` path) before doing the larger role-extraction
work.

Before any of Phase 5a is implemented, an architect review (Opus,
`oh-my-claudecode:architect`) was run against the new roadmap text. It found
the direction sound but surfaced gaps that the roadmap text does not yet
account for. This file records those gaps so a developer picking up Phase 5a
understands *why* they exist and what they need to think through before
writing code — it does not prescribe the final fix.

## Findings

### 1. [Critical] The Principle II exception has no `plan.md` home yet

Constitution Governance (`constitution.md:397-399`) requires that any
exception to a principle be logged in the **Complexity Tracking table of the
relevant `plan.md`, before implementation begins**. Right now the exception
for Phase 5a exists only as prose in `roadmap.md` — there is no `plan.md`
for the desktop-profile phase (`specs/010-configure-basic-profile/`
covers only the `basic` profile that already shipped).

**Why this matters**: writing the exception into a roadmap satisfies
nobody's process gate. If a developer starts implementing Phase 5a without
first creating a spec/plan for it (e.g. a new `specs/014-.../plan.md`) and
recording the exception in its Complexity Tracking table, the work is
non-compliant with Governance from the first commit.

**Think about**: does this phase need its own spec via the usual spec-kit
flow before implementation starts, purely to give the exception a proper
home? Or is there a lighter-weight place this project already accepts for
recording exceptions that wasn't considered here?

### 2. [Critical] No profile scoping: both target `hosts: linux`

`configure-profile-roles.yml:3` (today's `basic`-only play) and the legacy
`configure-linux-roles.yml:3` both declare `hosts: linux`. The three legacy
desktop playbooks are `hosts: linux` / `hosts: all`. The roadmap describes a
"`profile: desktop` branch" and "a second inventory group", but never
specifies the actual binding between a profile's role list and the
inventory group that should receive it.

A concrete symptom of the same gap: legacy `configure-linux-roles.yml:9`
sets the play var `tmux_install_iconic_font: true`, while the `tmux` role's
own default is `false`. The `basic` profile deliberately does not include
`tmux` at all. If the desktop branch imports the legacy play (carrying its
vars) without strict group separation from `basic`, there is no guarantee
the two profiles stay isolated when both kinds of hosts exist side by side
in the same inventory.

This isn't a hypothetical: `specs/010-configure-basic-profile/research.md:54`
already recorded the principle "two unrelated profiles must not share one
mutable role list" when the `basic` profile was designed. Phase 5a's
verbatim-import plan, as currently worded, risks breaking that principle
again for `desktop`.

**Think about**: should the desktop branch's role play target the new
`desktop` inventory group explicitly (not `hosts: linux`), and should
`basic`'s play be tightened the same way, so the two profiles can never
apply to the same host even if both groups exist in one inventory file?

### 3. [Worth fixing] The planned AWS RDP rule is additive, not conditional

The roadmap says the missing `3389` (RDP) security-group rule should be
added for the desktop case, relying on `purge_rules: false` in
`tasks/create/aws.yml:93-99` to add it without disturbing the existing `22`
rule. But `tasks/create/aws.yml` uses one shared `ansible-sg` security group
for every AWS VM the new playbooks create — `basic` and `desktop` alike.
Adding `3389` "additively" opens RDP on **every** AWS VM, not just the
desktop ones, which is a wider exposure than intended and cuts against
least-privilege thinking (Constitution Principle IX's spirit, applied here
to network exposure rather than CI credentials).

**Think about**: does the `3389` rule need to be conditioned on
`profile == desktop` (e.g. only added/present when a desktop VM exists), or
does the desktop profile need its own security group separate from
`ansible-sg`?

### 4. [Worth fixing] `restore.yml` parity proven too late

The roadmap defers porting `restore.yml` (personal backup/settings restore:
home-folder files, keyring, chromium/Chrome/VS Code/Claude settings) to
"right before Phase 6 deletes the legacy stack." That ordering means the new
restore path is least proven at the exact moment the only fallback
(the legacy stack) is removed. If the ported `restore.yml` has a bug that
only surfaces in practice, there is no way back once Phase 6 has run.

**Think about**: should Phase 6 require an explicit, demonstrated
backup → destroy → create → restore round-trip on the *new* playbooks as an
entry gate, stated as a checklist item in the roadmap — not just "ported,"
but "ported and proven" — before the legacy stack is deleted?

### 5. [Minor] Dependency graph doesn't show the two-pronged Phase 6 dependency

The ASCII graph in `roadmap.md` (Phase dependency order section) still draws
a single linear spine. The prose correctly says Phase 6 depends on **both**
provider-creation parity and desktop-profile parity, but the diagram only
shows one chain. Cosmetic — fix when next touching that section.

## References

- `docs/feature-requests/feat.create-destroy-vm/roadmap.md` — Phase 5/6 text
  this file is reacting to
- `.specify/memory/constitution.md:397-399` — Governance clause on logging
  complexity exceptions
- `playbooks/configure-profile-roles.yml:3` and `configure-linux-roles.yml:3`
  — both `hosts: linux`, no profile scoping
- `configure-linux-roles.yml:9` and `roles/tmux/defaults/main.yml` —
  `tmux_install_iconic_font` play-var vs. role-default conflict
- `specs/010-configure-basic-profile/research.md:54` — recorded principle
  that profiles must not share one mutable role list
- `playbooks/tasks/create/aws.yml:93-99` — shared `ansible-sg`,
  `purge_rules: false`
- `restore.yml` — personal-data restore scope deferred to immediately
  before Phase 6 deletion
- `specs/009-create-destroy-vm/plan.md` — existing Complexity Tracking
  table, precedent for where a Phase 5a exception entry would belong
