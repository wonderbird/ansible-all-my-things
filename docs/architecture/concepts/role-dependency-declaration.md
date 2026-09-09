<!-- SPDX-License-Identifier: MIT-0 -->

# Role dependency declaration: `meta/main.yml` vs. explicit ordering

Most roles in this repository are authored with `dependencies: []` in
`meta/main.yml`; cross-role ordering is instead expressed explicitly, by
listing roles in the required order in a playbook's `roles:` list (or a
Molecule scenario's `converge.yml`). This document is the authoritative
source of truth for when that default should be overridden — i.e. when a
role's `meta/main.yml` MUST declare a real Ansible role dependency instead
of, or alongside, explicit ordering.

## The decision test

Ask one question about the role being authored or changed: **does one of
this role's own tasks unconditionally require an artefact (binary, file,
clone, config) that only another specific role provisions, such that
absence causes a hard failure for any consumer playbook that has not
already applied that other role first — whether via a bare task that fails
on its own, or an explicit `assert`/`fail` guard — with no `when:`-skip or
`failed_when: false` masking the failure?**

- **Yes** → this is a hard, role-intrinsic dependency. Declare it in
  `meta/main.yml`'s `dependencies:` list. The requirement is a property of
  the role itself, not of any one playbook's ordering choice, and must not
  rely on every future consumer independently rediscovering it by reading
  the role's tasks.
- **No** → the relationship is a project-specific orchestration choice
  (e.g. "these two roles happen to run well together in this pipeline"),
  not a functional requirement. Express it via explicit ordering only —
  do not add a `meta/main.yml` dependency for convenience-only sequencing.

## Worked examples from this repo

**`claude_code_config` → `rtk` (hard dependency).**
`claude_code_config/tasks/configure.yml` runs:

```yaml
- name: Initialize rtk globally for each desktop user
  ansible.builtin.command:
    cmd: rtk init -g
  become: true
  become_user: "{{ item }}"
  loop: "{{ login_user_names }}"
  changed_when: false
```

An unconditional `command` task, no existence check, no `failed_when:
false`. If the `rtk` binary is absent, this task fails outright. A
playbook that lists `claude_code_config` without having first applied `rtk`
will break at apply time — this is exactly the "hard-fails for any
consumer" signal.

**`claude_code_config` → `ai_agent_workspace` (hard dependency).** The
skills symlink task in `claude_code_config/tasks/install-addons.yml`
asserts `matched > 0` after searching the `ai_agent_workspace` clone's
`.claude/skills` directory — a deliberate, fail-loud (Constitution
Principle XII) guard for the same kind of cross-role artefact dependency.

**`claude_code_config` → `claude_code` (hard dependency).**
`claude_code_config/tasks/install-addons.yml` and `configure.yml` run
unguarded `claude plugin ...`/`claude mcp ...` shell calls against
`/home/{{ item }}/.local/bin/claude` — the binary `claude_code` installs.
No presence check precedes them; if the binary is absent, these tasks fail
outright. `claude_code_config/tasks/configure.yml`'s own jq merge also
assumes `~/.claude/settings.json` already exists with `claude_code`'s
baseline auto-update-disable keys — `claude_code/tasks/configure.yml`
creates `~/.claude` and writes that baseline first. `claude_code_config`
therefore declares `claude_code` as a hard `meta/main.yml` dependency, in
addition to explicit play ordering.

All three qualify under the decision test above, and all three are
declared — see "Current state" below.

**Counter-example: role co-location in a playbook.** Two roles that happen
to run in the same play purely because they configure the same host profile
(e.g. `nerd_font` and `google_chrome` both applying to the `desktop` group)
have no functional ordering requirement between them — no meta dependency
is warranted; the playbook's role list is the only ordering mechanism
needed, and none exists here today.

## Why declare the dependency even when explicit ordering already works

Ansible deduplicates role execution by role name and **identical role
parameters** — the args on the role invocation itself (e.g. `- role: rtk,
foo: bar`), compared before variable evaluation, not by the ambient
play/host/group variables a role happens to see at runtime. If a role is
both declared as a `meta/main.yml` dependency of another role **and**
listed explicitly in the same play with the same (in this repo's case,
absent) role parameters, it runs exactly once. Declaring a genuine hard
dependency therefore costs nothing at runtime when the calling playbook
already lists the roles in the correct order — it adds a second,
independent enforcement path:

- **Meta dependency**: makes the role self-defending. Any current or future
  consumer — a new playbook, a Molecule `converge.yml`, a role composed
  into another project — gets the correct ordering automatically, without
  having to read the role's task internals to discover the requirement.
- **Explicit playbook/converge ordering**: keeps the full apply order
  human-auditable from one flat file, without recursively tracing
  `meta/main.yml` across every role in the chain — valuable in a
  security/audit-conscious repo (see Constitution Principle IX) where
  reviewers need to reconstruct exactly what runs, in what order, without
  spelunking through role metadata.

These are not competing choices for a genuine hard dependency: keep both.
The redundancy is intentional, not duplication to eliminate — it is the
same "log the accepted tradeoff" posture the Complexity Tracking practice
already applies to other deliberate small overlaps in this codebase.

## Presence-check conditionals are not a substitute

A third option exists beyond "declare a meta dependency" and "explicit
ordering": have the dependent role check whether the other role's artefact
is present and branch — e.g. `stat` the `rtk` binary, then
`when: rtk_stat.stat.exists` around `rtk init -g`. This does not solve the
same problem and MUST NOT be used as a substitute for either mechanism
above, for a hard dependency as defined by the decision test.

Constitution Principle XII (Fail Loud) already governs this, even though it
does not name presence-check conditionals explicitly: *"Silent skips,
empty-string fallbacks, and `None`/undefined variable fallthrough are
prohibited"*; *"`ignore_errors: true` MUST NOT suppress genuine failure
conditions."* Walk the branches:

- **Skip silently if absent** (`when: rtk_stat.stat.exists`, no `else`).
  This is exactly the prohibited pattern. `rtk init -g` never runs, the task
  reports skipped/ok, the playbook run looks green, but the desired
  end-state is never reached. This is a **regression** from the role's
  current behavior: today's unconditional `command: rtk init -g` already
  fails loud (no `failed_when: false` anywhere in that task) when the
  binary is missing. Adding a silent-skip guard would make a currently
  fail-loud task quietly swallow the same failure.
- **Fail with a custom message if absent** (`stat` + `assert`/`fail` before
  the guarded task). Whether this is redundant or required depends on what
  the guarded task does when the artefact is missing:
  - If the task already hard-fails on its own (the `rtk init -g` case — a
    bare `command` with no fallback), an explicit presence-check-then-fail
    is redundant with the failure that already happens; it buys a
    friendlier diagnostic string, nothing else.
  - If the task would otherwise **silently no-op** — the `ai_agent_workspace`
    case is exactly this: without its `assert matched > 0` guard, a missing
    clone makes the `find` return zero matches (not an error), and the
    downstream symlink loop iterates zero times — no failure, no symlinks,
    a green run. Here the presence-check-then-fail **is** the Fail-Loud
    mechanism (Constitution Principle XII), not diagnostic sugar; removing
    it would silently break the role's contract.
  - Either way, presence-check-then-fail does not by itself establish
    correct *ordering* — it only decides how loudly a wrong order is
    reported. It does not replace declaring the dependency or ordering the
    playbook; it is sometimes required alongside them (when the guarded
    task's own failure mode would otherwise be silent) and merely a nicer
    error message alongside them otherwise.
  - It is also the **only available mechanism** when the prerequisite is
    not a role you can declare a dependency on at all — provisioned by a
    different playbook run, a manual/bootstrap step, or anything not
    modeled as an Ansible role in this repo. In that case, skip the
    dependency-declaration question entirely and go straight to a
    fail-loud presence check.
  - It also serves as a **last line of defense** for a role meant to be
    reused by consumers outside this repo's own playbooks: a meta
    dependency is still the right primary tool there, but a consumer who
    invokes the role via `include_role` (see the caveat below) won't get
    it enforced — a presence-check guard inside the role catches that case
    loudly instead of letting it no-op or fail obscurely.
- **Install the dependency inline if absent.** Duplicates the other role's
  actual installation logic into the dependent role. A one-line idempotent
  apt task is cheap enough to justify duplicating across a couple of roles;
  reimplementing another role's non-trivial core logic conditionally,
  though, duplicates the role itself, a straight Principle II/XI
  violation.
- **Warn and continue if absent.** Same defect as silent-skip with a log
  line attached. A warning inside a long playbook run against many hosts
  gets missed; it does not meet "an explicit, actionable error."

The test that decides whether any `when:`-branch on another role's artefact
is legitimate: **is "artefact absent" ever a genuinely supported system
state here, or is it always a bug that happens not to crash immediately?**
Legitimate Ansible branching looks like OS-family conditionals (`when:
ansible_os_family == "Debian"` — both branches are valid depending on real
environment) or feature flags (`when: enable_x | default(false)` — "off" is
a supported configuration) — cases where neither branch is a degraded
fallback for a missing precondition. Contrast with a role's own idempotency
guard on its **own** target artefact (e.g. `rtk`'s `rtk_pre_install_stat`,
skip reinstalling if already present) — that is ordinary Principle I
idempotency, not a cross-role dependency question, and is unaffected by any
of this. For `rtk` inside `claude_code_config`: every production playbook
that runs `claude_code_config` also runs `rtk` first; "absent" only ever
means the ordering broke. Branching on it can only mask a real defect,
never serve a real "sometimes it's fine" case — the tell that
presence-checking is the wrong tool here.

One more reason a partial presence-check workaround would not produce a
coherent system, even though it is not itself an apply-time failure:
`configure.yml`'s settings.json merge, in the same file, unconditionally
writes the literal string `"rtk hook claude"` into a Claude Code
PreToolUse hook via `jq` — it does not execute `rtk` and does not fail if
`rtk` is absent, but it does assume `rtk` will be present later, at
*runtime*, whenever Claude Code triggers that hook. `rtk` is a hard,
load-bearing dependency of `claude_code_config` as a whole — one apply-time
task (`rtk init -g`) and one runtime assumption (the hook) — not of one
isolated task; a conditional around only the init task would leave the
runtime assumption unaddressed either way.

## Current state

`claude_code_config/meta/main.yml` declares `dependencies: [rtk, nodejs,
ai_agent_workspace, claude_code]` — all four are hard, role-intrinsic
dependencies per the decision test above (`rtk` and `ai_agent_workspace`
for the reasons in the worked examples above; `nodejs` because
`install-omc-cli.yml` unconditionally invokes `npm`; `claude_code` because
this role's `claude plugin`/`claude mcp` shell calls unconditionally
require the binary it installs).

`beads_go`, `beads_rust`, `ai_agent_workspace`, `specify_cli`, `tmux`, and
`skill_manager` (which also needs `nodejs`) declare `dependencies: [git]` —
each unconditionally invokes the `git` binary via `ansible.builtin.git` or,
for `specify_cli`, `pipx install git+...`.

`claude_code/meta/main.yml` declares `dependencies: []` — it installs the
binary plus its own minimal version-pin config and has no task that
unconditionally requires `git` or any other role's artefact; the `git`
role is still listed ahead of it in `configure-profile-roles.yml` and its
Molecule `converge.yml`; purely orchestration-convenience ordering (git is
useful to have on any host running the Claude Code CLI), not a meta
dependency, per the decision test above.

The `git` role itself declares `dependencies: []` — it has no
dependency of its own.

`win_ai_agent/meta/main.yml` declares `dependencies: [windows_foundation]`
for the same kind of reason (Windows-specific, out of scope for this
document's Linux worked examples). Every other role in this repository is
authored with `dependencies: []`, relying solely on explicit ordering,
since none of them have a hard, role-intrinsic dependency by the test
above.

## Caveats when declaring a dependency

- **`meta/main.yml` dependencies are reliably honored via the `roles:` play
  keyword** (and transitively, when a dependency role itself has
  dependencies). Their handling under `import_role`/`include_role` has
  varied across Ansible versions and is documented inconsistently upstream
  — do not rely on either honoring them. This repo currently only uses the
  `roles:` keyword and `import_role` on the paths this document covers (a
  couple of unrelated roles elsewhere use `include_role` for other
  purposes), so nothing here breaks today — but if this repo moves toward
  conditional, task-based role inclusion for a role covered by this
  document, treat a `meta/main.yml` dependency on it as unenforced and
  re-express the ordering explicitly (and add a presence-check guard per
  the section above, since you can no longer rely on the dependency
  mechanism at all).
- **Keep dependency chains shallow.** Ansible resolves nested dependencies
  breadth-first in a way that becomes hard to reason about more than one
  level deep. This repo's roles are flat and single-purpose (Constitution
  Principle II), so dependency chains here should stay one level (a role
  depends directly on the role(s) it hard-needs, not on a chain of
  dependencies-of-dependencies).
- **Ansible's role-execution dedup is keyed on role name plus role
  parameters** (the args on the role invocation, e.g. `- role: rtk, foo:
  bar`), compared before variable evaluation — not on ambient play/host/
  group variables. `meta/main.yml` can pass parameters per dependency if a
  role genuinely needs different ones than its sibling explicit invocation,
  but prefer invoking with no parameters (or identical ones) on both paths
  in this repo, so Ansible's dedup actually collapses them to a single run.
