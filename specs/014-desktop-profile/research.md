# Phase 0 Research: Desktop Profile for Create and Destroy VM Playbooks

All Technical Context fields in [plan.md](plan.md) were resolved directly
from existing repository precedent and a fresh read of the current codebase
(several roadmap.md claims about today's state turned out to be stale — see
the Correction note at the end). No `NEEDS CLARIFICATION` markers remain.

## Decision: `profile` is a brand-new mechanism, not an extension

**Decision**: Treat `profile` as a net-new extra-var on `create-vm.yml` and a
net-new `basic`/`desktop` inventory-group pair, not as "adding a second
branch" to something that already exists.

**Rationale**: Direct inspection of `playbooks/create-vm.yml`,
`playbooks/destroy-vm.yml`, `playbooks/configure-profile-roles.yml`, and a
repo-wide `grep -rn profile` found zero references to a `profile` extra-var
and zero `basic` inventory group. `configure-profile-roles.yml` targets
`hosts: linux` unconditionally — the same `linux` group every provider's
create task file already writes every host into, regardless of intended
profile. roadmap.md's Phase 1 and Phase 5 sections both described this as
already done ("`profile` defaults to `basic`; both parameters exist"; "...
configures the `basic` inventory group"); both claims were inaccurate
against the current codebase and have been corrected in roadmap.md directly
as part of this planning session.

**Alternatives considered**: None — this is a factual finding, not a design
choice. The only question it resolves is scope: this feature must build the
`profile` mechanism, not just extend it.

## Decision: One extra dict key per provider task file for group membership

**Decision**: Each `tasks/create/<provider>.yml` adds the new host under a
`basic` or `desktop` group key (selected by the `profile` var) in its
existing `updated_inventory` `combine()` call, alongside the existing `all`/
`linux`/`<provider>` keys. Each `tasks/destroy/<provider>.yml` removes the
host from that same key in its existing `cleaned_inventory` construction.

**Rationale**: Every provider's create/destroy task file already hardcodes
its own group key (`tart`, `docker`, `hcloud`, `aws`) using the identical
`combine()`/`dict2items | selectattr` pattern. Adding one more key of the
same shape is the smallest possible change that gives `configure-profile-roles.yml`
something real to target with `hosts: basic` / `hosts: desktop`, and it
requires no new abstraction — just one more literal key, mirroring a pattern
already proven idempotent four times over.

**Alternatives considered**:

- *A `group_by` task keyed on a host fact*: rejected — would require setting
  a custom fact on every host first, more moving parts than writing one more
  literal key into a dict that is already being constructed by hand.
- *A single shared "register profile group" task file, included by all four
  providers*: rejected as premature abstraction (Principle IV) — the four
  provider task files already duplicate the `all`/`linux`/`<provider>`
  pattern independently with no shared helper; a new shared helper introduced
  only for this one additional key would be inconsistent with the
  established (if duplicative) per-provider style, and the duplication here
  is 4 nearly-identical one-line dict entries, not complex logic.

## Decision: Reject docker+desktop via a new assert-provider-profile.yml task

**Decision**: Add a new task to the existing `assert-provider-profile.yml` that
fails loudly when `provider == 'docker' and profile == 'desktop'`, run in
`create-vm.yml`'s `pre_tasks`, before `tasks/create/{{ provider }}.yml` is
included.

**Rationale**: `assert-provider-profile.yml` already establishes the "fail
before any infrastructure action" pattern for an invalid `provider` value
(`tasks/assert-provider-profile.yml`). The desktop/docker incompatibility is the
same shape of pre-condition — a value combination that must never reach the
provider-specific task file — and reuses the existing `pre_tasks` slot.

**Alternatives considered**:

- *Check inside `tasks/create/docker.yml` itself*: rejected — by the time
  that task file runs, `pre_tasks` has already completed; an in-task-file
  check would be a less prominent, later failure point than extending the
  existing up-front assertion, and would scatter the docker/desktop rule
  away from the other provider-validity rule it logically belongs beside.

## Decision: profile-roles.yml gets two plays; profile.yml gets one branch

**Decision**: `configure-profile-roles.yml` keeps its existing `basic` play
(re-scoped from `hosts: linux` to `hosts: basic`, role list unchanged) and
gains a second play, `hosts: desktop`, that imports
`configure-linux-roles.yml`'s role list verbatim. `configure-profile.yml`
gains a `desktop`-scoped `import_playbook` chain
(`setup-desktop.yml`/`setup-keyring.yml`/`setup-desktop-apps.yml`) alongside
its existing `basic`-only chain.

**Rationale**: Mirrors the structure `configure-linux.yml` already uses for
the legacy stack (a flat sequence of `import_playbook` statements, each
already internally scoped to its own `hosts:`), and mirrors
`specs/010-configure-basic-profile`'s precedent of "one playbook hosting
multiple host-scoped plays" rather than introducing a new file per profile.
Two plays in one file, each independently host-scoped, is exactly how
multiple inventory groups receive different role sets without conditional
logic inside a single play (Principle IV — no `when:` gymnastics needed; the
inventory group itself is the switch).

**Alternatives considered**:

- *Separate `configure-profile-roles-desktop.yml` file*: rejected as
  unnecessary file proliferation — nothing about Ansible's
  `import_playbook` mechanism requires a separate file per host group, and
  `configure-linux.yml`'s own precedent already composes multiple
  independently-scoped plays without splitting files per concern.
- *One play with `hosts: basic:desktop` and tag-based role skipping*:
  rejected — directly reintroduces the shared-mutable-role-list problem
  `specs/010-configure-basic-profile/research.md` already rejected once
  (two profiles must not share one mutable role list); tags would couple
  `basic` and `desktop` together exactly as the roadmap's step 3 exists to
  prevent.

## Decision: AWS RDP rule via conditional rule list, not a new security group

**Decision**: `tasks/create/aws.yml`'s `amazon.aws.ec2_security_group` task
adds the TCP 3389 rule to the existing shared `ansible-sg` group only when
`profile == 'desktop'`, using a `rules` list built conditionally (e.g. a
`set_fact` that appends the 3389 rule entry only for the desktop case, or two
task variants gated by `when:`). The group itself remains the single shared
`ansible-sg`.

**Rationale**: The roadmap explicitly considered "give the desktop profile
its own security group" and left the choice open; reusing one shared group
with a profile-conditional rule is simpler (Principle IV) and requires no
new default variable, no new task-file branching beyond what FR-006/FR-007
already require for the group-key plumbing. `purge_rules: false` (already
set) makes the conditional-rule approach safe: a `basic`-profile create run
never removes the 3389 rule a desktop VM's create run may have already
added, and a `desktop`-profile create run never removes the 22 rule.

**Alternatives considered**:

- *Dedicated `ansible-sg-desktop` security group*: rejected for this
  increment — correct in isolation, but adds a second security group to
  manage/clean up for no behavioral difference over a conditional rule on
  the shared group, given `purge_rules: false` already makes the additive
  approach safe. Revisit only if a future requirement needs per-profile
  network isolation beyond port exposure.

## Correction note: roadmap.md factual drift discovered during this research pass

Two roadmap.md claims were found inaccurate against the current codebase and
corrected directly in that file (not left as a separate tracked finding,
since fixing a durable artefact's factual claim is the artefact's own
maintenance, not new work the codebase must satisfy):

1. Phase 1's description that `profile` already existed as a `create-vm.yml`
   extra-var defaulting to `basic` — it does not exist at all today.
2. Phase 5's description that `configure-profile.yml`/
   `configure-profile-roles.yml` already "configure the `basic` inventory
   group" — they target `hosts: linux` today; no `basic` group exists.

A related, pre-existing minor drift was also noticed but left untouched as
out of scope for this feature: `specs/010-configure-basic-profile/research.md`
describes `configure-profile-roles.yml` as scoped to `hosts: tart` with a
five-role list (no `tmux`); the current file targets `hosts: linux` and
includes six roles (`podman`, `tmux`, `ruby`, `python`, `dolt_sql_server`,
`claude_code`). `tmux` IS present in the file as it stands today — bd issue
`ansible-all-my-things-t2vb` ("Add tmux role to basic profile") describes it
as absent, which no longer matches; that issue appears already resolved by a
later merge and may just need closing. Neither the `specs/010` drift nor
`t2vb`'s stale premise is corrected here — unrelated to this feature's scope.
