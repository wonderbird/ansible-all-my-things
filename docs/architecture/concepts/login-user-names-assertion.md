<!-- SPDX-License-Identifier: MIT-0 -->

# Asserting the `login_user_names` input contract in roles

Many roles in this repository configure software per user by looping over
`login_user_names`. That variable is not role-owned: the calling playbook
derives it from the `login_users` inventory list, and a Molecule converge play
sets it directly in its `vars:` block. So every consuming role depends on a
value it neither defines nor controls.

This document is the authoritative source of truth for how such a role declares
that dependency.

## The rule

A role that loops over `login_user_names` MUST carry this block, byte-identical,
as its **first own task** — before any role-defaults validation, and before any
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

`login_user_names` MUST NOT be given a role default. An empty-list default turns
a missing required input into a silent no-op: every loop runs zero iterations,
the play reports success, and the host is left unconfigured.

**Never reorder the two conditions.** `assert` short-circuits on the first falsy
condition, so `is defined` has to come first. Reversed, an undefined variable
raises Ansible's generic undefined-variable error at the length check and
`fail_msg` is never printed — exactly the diagnostic loss the assertion exists
to prevent.

## The playbook-level complement

The preflight play of `playbooks/configure-profile.yml` additionally asserts
that `login_users` is defined and non-empty. It fires before any host is touched
and before role meta dependencies execute, which a role-level assertion cannot:
a role with meta dependencies runs those before its own first task, so a
role-level violation is reported only after some work has been done.

The playbook guard does not replace the role-level one. It reaches only the
orchestrated entrypoint — not a role applied directly by the role-runner script
or by a Molecule converge play, and not a role that no playbook applies at all.

## Why the block is duplicated rather than extracted

A role's declaration of its required inputs is interface, not logic — the
Ansible analogue of a function signature, which is necessarily restated per
function. Principle XI (DRY) targets restated *implementation* logic, so it is
not in tension here.

This kind of self-defending redundancy is already established in this
repository: Principle II mandates declaring a hard role dependency in
`meta/main.yml` *in addition to* explicit playbook ordering, precisely so a role
defends itself for any future consumer.

Keeping the copies byte-identical and greppable serves the goal — no silent
drift between copies — better than an abstraction would. A shared task file
would need a cross-role relative include, breaking role self-containment; an
`include_role` or `meta` dependency would add an edge and a mandatory Molecule
scenario for a six-line task.

## Adding a new role

The `role-creator` skill carries this block verbatim, at the point where a new
role's `tasks/main.yml` is authored. That is the surface a role author reads.

`role-template/` deliberately carries nothing for this convention. It ships no
`tasks/` directory at all (Principle XIII: no empty or stub files), and most new
roles do not loop over `login_user_names` — a block shipped by default would be
wrong for the majority of them, and removing an inapplicable block is a step
authors skip more often than adding a missing one.

Keeping every copy identical is therefore a review responsibility today.
Enforcing it automatically — checking that every role containing a
`login_user_names` loop carries the block, and that all copies hash identically
— is still open work.
