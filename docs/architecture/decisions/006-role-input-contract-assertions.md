# ADR-006: Role Input Contract Assertions for `login_user_names`

Date: 2026-09-09
Status: Accepted
Deciders: Stefan (Product Owner)

## Context and Problem Statement

Fourteen roles configure software per user by looping over
`login_user_names`. None of them checked the variable before use.

`login_user_names` is not a role-owned value. It is derived by the calling
playbook from the `login_users` inventory list, whose own documentation states
that there should be at least one user. So every consuming role depends on a
value it does not define and did not validate.

That produced two failure modes, and the second is the serious one:

- **Undefined.** Ansible raises a generic error at whichever loop expands
  first. It names the variable, but the message points at an arbitrary task
  rather than at the missing input, and only after earlier tasks in the role
  have already changed the host.
- **Empty list.** Every loop runs zero iterations and the play reports
  success. Nothing fails, nothing is logged, and the host is left
  unconfigured. The `podman` role shipped `login_user_names: []` as a role
  default and its README described the resulting skip as intended behaviour,
  so a caller supplying no users got a system-wide Podman install with every
  per-user step silently omitted.

Principle XII (Fail Loud) prohibits exactly this: silent skips, empty-string
fallbacks, and undefined fallthrough for a required value. It binds by its own
text to "any task, playbook, **or role**".

## Decision Drivers

1. **A required value must fail at the gap, not at a downstream symptom.** The
   error must name the variable and say what a correct value looks like,
   before any host mutation.
2. **Roles are applied outside the orchestrating playbook.** The role-runner
   script and every Molecule converge play apply a role directly. A guard that
   lives only in a playbook does not protect those paths.
3. **Three consuming roles are applied by no playbook at all.** For them, ad
   hoc application is the only invocation path, so a role-level contract is the
   only guard they can ever have.
4. **Proportionality.** The repository is maintained by one person. Any fix
   must not introduce a new abstraction, a new role, or new test scaffolding.

## Considered Options

1. Assert the contract in every consuming role.
2. Document the contract at playbook level and add no assertions.
3. Extract one shared assertion into a common task file or helper role.
4. Assert once in the orchestrating playbook instead of in the roles.
5. Consolidate the derivation into inventory group variables and assert there.

## Decision

**Option 1 and Option 4 together, plus the documentation half of Option 2.**

Every role consuming `login_user_names` carries this block, byte-identical, as
its first own task — before any role-defaults validation and before any
`import_tasks`:

```yaml
- name: Assert login_user_names is provided
  ansible.builtin.assert:
    that:
      - login_user_names is defined
      - login_user_names | length > 0
    fail_msg: >-
      Variable validation failed: login_user_names must be defined and
      contain at least one username. It is derived from login_users as
      `login_users | map(attribute='name') | list`; a Molecule converge
      play sets it directly in its `vars:` block.
```

The preflight play of `playbooks/configure-profile.yml` additionally asserts
that `login_users` is defined and non-empty, before any host is touched.

`login_user_names` is never given a role default. The `podman` role's
`login_user_names: []` is removed.

### Why the options were rejected

**Option 2 — documentation only.** Documentation cannot make an empty list
fail. It leaves both the standalone and Molecule paths unguarded and does not
touch the `podman` default. Its documentation half is adopted alongside the
assertions, not instead of them.

**Option 3 — shared task file or helper role.** A cross-role relative include
breaks role self-containment and has no precedent here. An `include_role` or
`meta` dependency instead adds an edge to every consuming role plus a mandatory
Molecule scenario for a six-line task, and Principle II prohibits declaring a
role dependency that exists only for orchestration convenience. The abstraction
costs more than the duplication it removes.

**Option 4 alone — playbook guard as a replacement.** It reaches no role
applied outside the orchestrated entrypoint, and its coverage holds only while
that entrypoint remains the sole one, a property that can change with no diff
and no test failure. Adopted as a complement instead: it fires before role
meta-dependencies execute, which a role-level assertion cannot.

**Option 5 — consolidate the derivation into inventory.** A group-variable
value is a lazily evaluated expression: an undefined `login_users` still
surfaces as a generic error at an arbitrary loop-expansion site, and an empty
one still yields an empty list that fails nothing. It is a worthwhile
duplication fix with a materially different blast radius — variable precedence
and host-group scoping across every play — and is tracked separately. Its open
question: the derivation appears at eight sites, one of them a shell here-doc
in the role-runner script, and one play composes a second variable on top of
it; which inventory group file is correct depends on whether every consuming
play's hosts belong to the Linux group, which is set during host creation.

### Why duplication is accepted over extraction

Principle XI targets restated implementation logic. A role's declaration of its
required inputs is interface, not logic — the Ansible analogue of a function
signature, necessarily restated per function. The repository already requires
this kind of self-defending redundancy: Principle II mandates declaring a hard
dependency in `meta/main.yml` *in addition to* explicit playbook ordering,
precisely so a role defends itself for any future consumer.

Where extraction costs more than the repetition, the goal Principle XI serves —
no silent drift between copies — is better served by keeping the copies
byte-identical and greppable than by building the abstraction.

## Complexity Tracking

| Complexity | Principle in tension | Why accepted | Simpler alternative rejected because |
| --- | --- | --- | --- |
| Fourteen byte-identical assert blocks rather than a two-file fix | IV (YAGNI) vs XII (Fail Loud) | XII binds roles individually by its own text, with no reachability exception; three of the fourteen roles are applied by no playbook, so the playbook guard can never reach them | A two-file fix — removing the role default and adding the preflight guard — leaves fourteen roles individually non-compliant with XII and cannot reach the three uncalled roles |
| Duplication retained instead of extracted | XI (DRY) | Interface declarations, not restated implementation; extraction costs more than the duplication it removes | A shared assert task file requires either a cross-role relative include, breaking role self-containment, or a role dependency declared purely for orchestration convenience, which Principle II prohibits |

## Consequences

- **Fourteen identical six-line blocks exist by design** and must stay
  byte-identical; divergence is a defect.
- **Adding a role that loops over the variable requires adding the block.**
  The `role-creator` skill documents this; automating it in CI remains open.
- **The two conditions are order-sensitive.** `assert` short-circuits on the
  first falsy condition, so the definedness check must precede the length
  check. Reversing them degrades the error to a generic undefined-variable
  trace and suppresses `fail_msg` entirely. The failing condition is echoed in
  the output as `assertion`.
- **Roles with meta dependencies run those before their own first task**, so a
  role-level violation is reported after some work has been done. The preflight
  guard removes this for the orchestrated path; it remains on standalone role
  application.
- **The `podman` change corrects drift against that role's own specification**,
  which already declared the default as "(none — caller must supply)" while the
  role shipped an empty list. The specification outranks the README, so this is
  closer to a defect fix than a capability removal — though a caller relying on
  the documented skip loses it.
- **Playbooks invoked directly rather than through the profile playbook are not
  covered by the preflight guard.** One such playbook is imported by no
  entrypoint at all, and a merged feature specification forbids wiring it in.
- **If the derivation is later consolidated into inventory**, the definedness
  branch becomes near-unreachable and the length check becomes the only live
  one. The assertion must not then be weakened to a definedness check alone.

## Follow-ups

- **Automate the invariant in CI.** Every role containing a `login_user_names`
  loop must carry the block, and all copies must hash identically. Until then
  this is a review responsibility. (Tracked in `ansible-all-my-things-j771`.)
- **Consolidate the eight-site derivation** into inventory group variables,
  after determining which group every consuming play's hosts belong to.
  (Tracked in `ansible-all-my-things-khcl`.)
- **Extend the guard to directly invocable playbooks** —
  `setup-desktop.yml`, `setup-keyring.yml`, and `setup-desktop-apps.yml` are
  covered on the orchestrated path but not when run on their own. (Tracked in
  `ansible-all-my-things-tlvb`.)
- **Decide wire-or-delete for the three roles no playbook applies.** (Tracked
  in `ansible-all-my-things-i7xs`.)
- **Remove the dead scenario variable** in the `rtk` role's Molecule converge
  play, which sets `login_user_names` although the role never reads it.
