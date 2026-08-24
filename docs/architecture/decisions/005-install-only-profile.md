# ADR-005: Install-Only AI Agent Profile via a `basic:desktop` Union Play

Date: 2026-08-24
Status: Accepted
Deciders: Stefan (Product Owner)

## Context and Problem Statement

The repository provisions hosts by *profile*. Profiles are inventory groups
that are children of a `base` supergroup (`inventories/base.yml`): `basic` and
`desktop`. `playbooks/configure-profile-roles.yml` applies a shared role list to
`hosts: base` (so every profile inherits it) and a GUI-only extension to
`hosts: desktop`.

The shared base role list installs the full developer stack *and* the AI agent
tooling, including two roles produced by the `claude_code` split (ot00.1):

- `claude_code` — installs the Claude Code binary and its runtime dependencies
  (`jq`, `git`); no per-user configuration.
- `claude_code_config` — writes global per-user agent configuration:
  `~/.claude/settings.json` opinions, the oh-my-claudecode (OMC) CLI, plugins,
  MCP servers, a `.bashrc` agent block, and symlinks the shared skill library
  into `~/.claude/skills`.

A new need: a host that installs the AI CLIs but carries **zero** global
per-user agent configuration, for an operator who configures agents per project
themselves. Concretely, such a host must have the `claude`, `opencode`,
`specify`, and `rtk` binaries working, the `ai-agent-workspace` skill library
cloned (but **not** symlinked into `~/.claude/skills`), and no `~/.claude`
opinions, plugins, MCP config, or `.bashrc` agent block.

The single knob distinguishing this profile from `basic` is the omission of the
`claude_code_config` role. `claude_code` (with `jq`) must stay, because
`ai-agent-workspace` cloning needs `git` and `claude_code`'s own
`tasks/configure.yml` pipes `~/.claude/settings.json` through `jq`.

Decision: **how should the topology express a profile that receives every base
role except `claude_code_config`, without regressing `basic` or `desktop`?**

## Decision Drivers

- **Simplicity / YAGNI (Constitution IV).** The difference is a single role for
  a two-member "gets the config" set. Prefer the smallest structure that
  expresses it.
- **Idempotency (Constitution I).** `basic` and `desktop` must remain
  byte-identical to today: a re-run of `configure-profile.yml` must report zero
  changed tasks.
- **Fail loud (Constitution XII).** The exclusion must be structural, not a
  silently-skipped `when:` guard whose miss looks like success.
- **Avoid duplication / DRY (Constitution XI).** Weighed against the above; the
  chosen option accepts a small, contained duplication.

## Considered Options

1. **Union play (chosen).** Add `install_only` as a third flat child of `base`.
   Move `claude_code_config` out of the `hosts: base` role list into a new play
   `hosts: basic:desktop` that applies only `claude_code_config` and replicates
   `become: true` plus the full `vars:` block (`ansible_user`,
   `login_user_names`). `install_only` — a child of `base` but not of `basic`
   or `desktop` — inherits every base role yet is excluded from the config play
   by the group union pattern.
2. **Intermediate `agent_configured` group (rejected).** Introduce a group
   between `base` and `{basic, desktop}` that holds the config-bearing profiles,
   and target `claude_code_config` at it. Rejected under YAGNI: it adds a layer
   of inventory nesting to express membership of a two-element set, speculative
   structure for a single-operator repository.
3. **Per-host `when:` toggle (rejected).** Keep `claude_code_config` in the base
   play and guard it with `when: profile != 'install_only'` (or a per-host
   variable). Rejected under Fail Loud: a silent per-task skip is exactly the
   surface Constitution XII warns against — a mistyped condition skips config on
   hosts that need it and still reports success, and the skip is hard to assert
   on a VM.

## Decision

Adopt Option 1, the `basic:desktop` union play.

- `inventories/base.yml` children are flat: `basic`, `desktop`, `install_only`.
- `claude_code_config` is applied by a dedicated play `hosts: basic:desktop`,
  carrying the same `become: true` and `vars:` block as the base play. The
  desktop play is unchanged.
- The literal string `install_only` is byte-identical across the `base.yml`
  child, the profile allowlist in
  `playbooks/tasks/assert-provider-profile.yml`, and the `profile` value passed
  to `create-vm.yml`. A Docker host provisioned with `profile=install_only`
  lands in the `install_only` group because `create-vm.yml`'s Docker task
  combines the `profile` variable as a literal inventory group key.

## Consequences

- **Byte-identical `basic`/`desktop`.** Ansible deduplicates a role only within
  a single play; running `claude_code_config` in a separate play re-invokes its
  meta-dependencies. This is safe precisely because those dependencies are
  idempotent: the cross-play re-run makes no changes on a host that already has
  the config. This is proven by the zero-changed regression converge on a
  `basic` host — not assumed from role dedup, which does not span plays.
- **Small duplication.** The `vars:` block (`ansible_user`,
  `login_user_names`) and `become: true` are repeated in the new play. This is
  the accepted cost of Option 1 over Option 2's extra group layer; it is
  contained to one adjacent play and visible in one file.
- **`install_only` purity.** The profile gets `claude_code` (binary + `jq` +
  `git`) and `ai_agent_workspace` (clone-only), but no `~/.claude` global
  config, plugins, MCP, skill symlinks, or `.bashrc` agent block.

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
