# ADR-005: Opinionated Claude Config as a Cross-Cutting Group

Date: 2026-08-24
Status: Accepted
Deciders: Stefan (Product Owner)

## Context and Problem Statement

The repository provisions hosts by *profile*. Profiles are inventory groups
that are children of a `base` supergroup (`inventories/base.yml`): `basic` and
`desktop`. `playbooks/configure-profile-roles.yml` applies a shared role list
to `hosts: base` (so every profile inherits it) and a GUI-only extension to
`hosts: desktop`.

The shared base role list installs the full developer stack and the AI agent
tooling, via two roles with distinct, present-day responsibilities:

- `claude_code` — installs the Claude Code binary and its runtime dependencies
  (`jq`, `git`); no per-user configuration.
- `claude_code_config` — writes global per-user opinionated agent
  configuration: `~/.claude/settings.json` opinions, the oh-my-claudecode
  (OMC) CLI, plugins, MCP servers, a `.bashrc` agent block, and symlinks the
  shared skill library into `~/.claude/skills`.

The profile model conflates two independent axes:

- **System axis** — console (`basic`) vs desktop packages (`desktop`).
- **Config axis** — the opinionated `claude_code_config` output present vs
  absent.

Binding the config axis to profile identity leaves one cell of the resulting
2x2 matrix unreachable: **desktop without the opinionated config**. Two
independent, confirmed needs require it:

- An **OpenClaw desktop VM** whose several single-user agents each have a
  distinct purpose (conversation partner, personal assistant, coding
  assistants for apps needing desktop packages) must not receive the
  opinionated global Claude config.
- An **OpenCode + Oh My OpenAgent (OMO) work context** whose setup collides
  with the opinionated Claude Code configuration, so that host must run
  without the opinions regardless of its system profile.

Decision: **how should the topology let any host independently choose its
system profile and whether it carries the opinionated Claude config, without
regressing the existing `basic`/`desktop` behavior?**

## Decision Drivers

- **Orthogonality.** The system axis and the config axis must be
  independently selectable; every combination of the two must be reachable.
- **Idempotency (Constitution I).** Existing `basic`/`desktop` hosts that
  already carry the opinionated config must remain byte-identical: a re-run of
  `configure-profile.yml` must report zero changed tasks.
- **Fail loud (Constitution XII).** Opting out of the config must be
  structural (group membership), not a silently-skipped `when:` guard whose
  miss looks like success.
- **Simplicity / YAGNI (Constitution IV).** No longer weighs against a second
  inventory group: the desktop-without-opinions and console-without-opinions
  cells are confirmed needs, not speculative structure.

## Considered Options

1. **Cross-cutting `claude_opinionated` group (chosen).** Introduce a group
   orthogonal to the system-profile groups: a host belongs to its
   `basic`/`desktop` group and, independently, may opt into
   `claude_opinionated`. `claude_code_config` is applied by a play targeting
   `hosts: claude_opinionated` instead of a profile-based host list.
   `create-vm.yml` gains a `claude_opinionated` boolean variable, default
   `false` (pure opt-in); a host joins the group only when the flag is passed.
2. **`basic:desktop` union play with a third flat profile (rejected,
   superseded).** Add a third profile as a child of `base` but not of `basic`
   or `desktop`, excluded from a `claude_code_config` play targeting
   `hosts: basic:desktop`. This reaches "console without opinions" but ties
   the config axis to profile identity: reaching "desktop without opinions"
   would need a second, duplicate desktop-shaped profile, and the union-token
   syntax (`basic:desktop`) is non-obvious enough that a reviewer read it as
   desktop-only. Binding an orthogonal axis to profile identity does not scale
   past the first no-opinions cell.
3. **Per-host `when:` toggle (rejected).** Keep `claude_code_config` in the
   base play and guard it with a per-host variable. Rejected under Fail Loud:
   a silent per-task skip is exactly the surface Constitution XII warns
   against — a mistyped condition skips config on hosts that need it and still
   reports success, and the skip is hard to assert on a VM.

## Decision

Adopt Option 1, the cross-cutting `claude_opinionated` group.

- `claude_opinionated` is **not** a child of `base`; it is populated per host,
  independently of the host's `basic`/`desktop` system-profile membership.
- `claude_code_config` is applied by a dedicated play `hosts: claude_opinionated`,
  carrying the same `become: true` and `vars:` block as the base play. The
  desktop play is unchanged.
- `create-vm.yml`'s per-provider create tasks (`playbooks/tasks/create/*.yml`)
  add the new host to `claude_opinionated` only when
  `claude_opinionated | default(false) | bool` is true, following the same
  `combine(..., recursive=true)` pattern already used to add the host to its
  profile group.
- The `claude_code_config` role is **not renamed**: a group names a host-set
  intent, a role names a capability; the `claude_code` (binary) /
  `claude_code_config` (its config) pairing stays readable.

## Consequences

- **Config flips from default-on to opt-in.** A host only carries the
  opinionated config when `claude_opinionated=true` is passed to
  `create-vm.yml`. This migration hazard is accepted because these VMs are
  ephemeral and rebuilt regularly.
- **All four cells of the 2x2 are reachable**: console or desktop, each with
  or without the opinionated config.
- **The prior third flat profile is removed.** Only `basic`, `desktop`, and
  `windows` remain as system profiles; "console without opinions" is now
  expressed as `profile=basic` without `claude_opinionated`, not as a distinct
  profile name.
- **`claude_code_config` role retained, unrenamed** — see Decision above.

## Follow-ups

- **Dead `curl` dependency.** `roles/claude_code/tasks/install-deps.yml` had
  historically installed `jq`, `git`, and `curl`. `curl` was dead weight —
  `claude_code` downloads its binary via `ansible.builtin.get_url`, not `curl`,
  and no other role relied on `claude_code` installing it. `curl` is dropped;
  `jq` (used by `claude_code`'s own `settings.json` merge) and `git` (used by
  `ai_agent_workspace`'s clone) stay. (Tracked in `ansible-all-my-things-7quu`.)
- **Meta-dependency test gap.** A role's Molecule `converge.yml` lists roles
  explicitly and in order, so it cannot detect an accidentally broken
  `meta/main.yml` `dependencies:` list — the scenario would still pass. This is
  an inherent Molecule convention, not a defect of this change; it is mitigated
  by a documented manual meta-dependency review step in the `molecule-testing`
  skill. (Tracked in `ansible-all-my-things-vjib`.)
