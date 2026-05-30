# Plan: Persistent local Dolt SQL server for concurrent beads writes

## Context

Goal: let parallel AI agents (via `my-omc-parallel-work` skill) write to beads
concurrently without locking each other out — on **ephemeral VMs**. Each agent
session likely starts on a fresh VM with a fresh repo clone, and Dolt is NOT
pre-installed there. The whole setup MUST therefore be automated as an Ansible
role; manual steps will not survive VM churn (Constitution: Agent Environment).

**Investigation findings (system state verified, not assumed):**

| Fact | Value |
| --- | --- |
| Host arch (this machine) | `aarch64` (ARM64); fresh VMs may be any arch |
| Dolt installed (this machine) | yes — `/usr/local/bin/dolt`, v2.0.7 (newest 2.0.8) |
| Dolt on fresh VM | NOT pre-installed — role must download arch-correct binary |
| `bd` (beads) | v1.0.4, `/home/galadriel/.local/bin/bd` |
| Current dolt mode | `embedded` (in-process, no server) — per `bd dolt status` |
| Default server data dir | `.beads/dolt` (confirmed: `bd dolt --help` `data-dir` default) |
| Current embedded data | `.beads/embeddeddolt/ansible_all_my_things/` |
| Mode source file | `.beads/metadata.json` → `"dolt_mode": "embedded"` — **untracked on this machine** via local `.git/info/exclude` (see correction below); fresh-clone presence is a Step 0 open question |
| Git-tracked beads files | **ONLY `.beads/config.yaml`** (verified: `git ls-files .beads/` returns just `config.yaml`) |
| Per-project conn file | `.beads/.env` (gitignored, GH#2520) carries Dolt conn config |
| systemd (user) | running; lingering required for headless boot start |
| beads auto-start | `bd` auto-starts `dolt sql-server` transparently when needed |
| Issue count in `issues.jsonl` | **116** (verified `wc -l .beads/issues.jsonl`) |
| Pinned Dolt version | **2.0.8** (both `arm64` + `amd64` release assets confirmed to exist) |

**CORRECTION (prior-revision error).** An earlier version of this plan claimed
`.beads/metadata.json` is "git-tracked". That is **false**. `git ls-files
.beads/` returns only `.beads/config.yaml`. `metadata.json` is **untracked on
this machine**. The accurate mechanism behind that state is:

- `.git/info/exclude` (added by `bd init` as "fork protection") contains a
  blanket `.beads/` entry. This is a **local, per-clone** file that is **never
  cloned** — it does not travel with `git clone`.
- `config.yaml` is git-tracked **only because it was committed to HEAD BEFORE
  that exclude was added.** Already-tracked files bypass ignore rules, so the
  `.beads/` exclude does not untrack it.
- `metadata.json` was **never committed after the exclude existed**, so it stays
  **untracked on this machine**.
- **Key implication for fresh clones:** a fresh `git clone` will **NOT** inherit
  `.git/info/exclude`. Whether `metadata.json` exists on a fresh clone therefore
  depends on **beads' own init behavior** on the first `bd` invocation — **NOT**
  on this repo's local exclude, and **NOT** a property derivable from this
  machine's local state. **This is an open question to be settled empirically by
  Step 0**, not pre-decided here.
- **The operative conclusion is unchanged:** do **NOT** rely on `metadata.json`
  propagating via git (it won't on this machine); propagate server mode through
  the git-tracked `config.yaml` **only**.

Every claim that "fresh clones inherit server mode via metadata.json" is
therefore wrong and has been removed. This correction drives changes in the data
propagation design (below) and in Steps 0, 3, and 4.

**Critical reframing of the task.** The task description assumes beads uses an
embedded *library* that must be swapped for a server binary. That is not how
beads v1.0.4 works. Per `bd dolt --help`: *"Beads uses a dolt sql-server for all
database operations. The server is auto-started transparently when needed."*
Beads already has two modes:

- **embedded** (current): in-process Dolt engine, single writer — the lock
  problem the task describes.
- **server**: connect to a standalone `dolt sql-server` via host/port; multiple
  `bd` clients share one server = concurrent writers. Configured with
  `bd dolt set host <h>` / `bd dolt set port <N>`.

Because beads *already auto-starts a `dolt sql-server`*, the open empirical
question is whether that **auto-started server is already shared across
worktrees** — in which case concurrent writes may already work without ANY
systemd/linger/external-data-dir scaffold (the YAGNI hypothesis). **Step 0 (a
spike) resolves this before any role is built.** Do not assume the full Option A
is needed until the spike says so.

The core change, *if the spike confirms scaffolding is needed*, is:
**(1) stand up one persistent `dolt sql-server`, (2) point beads at the server,
and (3) make the server boot-persistent via user systemd.**

**What changed in this revision.** Both Architect and Critic returned ITERATE.
This revision (a) inserts a mandatory **Step 0 spike** to test whether beads'
own auto-start already supports concurrent cross-worktree writes (collapsing the
role if so); (b) **corrects the `metadata.json` git-tracking error**; (c) fixes
the data-dir rationale to **never** use `bd dolt set data-dir <absolute-path>`
(Principle X portability); (d) converts the auto-start split-brain note into a
**designed single-server mechanism** with a hard assertion; (e) resolves the
**Molecule/systemd feasibility** question by forcing a documented choice between
a systemd-capable container and a Vagrant/Tart VM; (f) adds a **Complexity
Tracking table** (Governance, `constitution.md:366-368`). It also pins Dolt
`2.0.8` and documents privilege/auth boundaries. Migration of existing beads data
uses **`bd backup sync` + `bd restore --force`** (user decision).

This is infra config in an Ansible repo. Constitution principles in scope:
Idempotency (I), Role-First + Molecule (II), Test-Locally-First (III),
Simplicity/YAGNI (IV), DRY (XI), Fail Loud (XII), No External/Ephemeral
References in Durable Artefacts (X — extended by analogy to machine-specific
absolute paths committed to durable artefacts).

## Work Objectives

0. **Spike (gate):** empirically determine whether beads' transparent auto-start
   already supports concurrent writes across sibling worktrees. The outcome
   decides whether the full role is needed or whether a minimal install+config
   role suffices.
1. (If the spike requires it) An Ansible role `roles/dolt-beads-server/` that, on
   a fresh VM, installs the arch-correct Dolt binary, creates a boot-persistent
   user systemd unit running a single local `dolt sql-server`, and enables
   lingering — fully idempotent. (If the spike shows auto-start suffices, the role
   collapses to: install arch-aware Dolt binary + commit host/port in
   `config.yaml`.)
2. Beads (`bd`) configured to use server mode against that local server, with the
   connection persisted **via git-tracked `config.yaml` only** so every
   agent/worktree connects to the same server. (`metadata.json` does NOT
   propagate; a fresh clone must derive server mode from `config.yaml`.)
3. Existing beads data migrated intact to the new server via **`bd backup sync`
   + `bd backup restore --force`** (Dolt-native, preserves full history). Applies
   to the current machine's embedded DB only; fresh VMs start with whatever beads
   initialises on first run (no migration needed there).
4. A validated test scenario for the role — **either** a Molecule scenario on a
   systemd-capable container **or** a Vagrant/Tart VM procedure — proving install
   + unit + linger + connectivity + single-server. The choice is decided and
   justified in "Molecule/systemd feasibility decision" below.
5. Concurrent writes from 2+ simultaneous `bd` clients succeed without lock
   errors — the acceptance proof for the whole task.

## Guardrails

**Must Have**

- **Step 0 spike runs first** and its branch decision is recorded in the plan/PR
  before any role is scaffolded.
- Role installs Dolt arch-aware: download the **v2.0.8** release asset matching
  `{{ ansible_architecture }}` (e.g. `arm64`/`amd64`); idempotent — skip if the
  pinned version is already installed (`creates:`/version-check guard).
- **data-dir is set ONLY via the systemd unit's `ExecStart --data-dir=...`
  flag.** NEVER run `bd dolt set data-dir <absolute-path>` — that writes a
  machine-specific absolute path into `metadata.json` (a per-clone artefact),
  breaking portability across clones/VMs (Principle X by analogy).
- User systemd unit `~/.config/systemd/user/dolt-beads.service` whose
  `ExecStart` invokes `dolt sql-server` directly (decoupled from `bd`), bound to
  `127.0.0.1` only, on a pinned port (role var, default `3309`),
  `Restart=on-failure`.
- **Single-server guarantee:** exactly ONE `dolt sql-server` bound to the pinned
  port, and beads' auto-start MUST NOT spawn a second server in its default
  `.beads/dolt/` location (designed mechanism + assertion in Step 3).
- `loginctl enable-linger` for the service user → boot persistence without an
  interactive login (required for headless agent VMs).
- Idempotent re-runs: re-running the role MUST NOT break a running server or lose
  data.
- Beads pointed at the server with the connection persisted in git-tracked
  `config.yaml` (host=127.0.0.1, port=pinned).
- Fail-loud behavior: required vars (`data-dir` path, port) validated with
  `assert`; if the server is down `bd` must error clearly, not silently fall back
  to a divergent embedded copy (Principle XII).
- Test scenario authored via the `molecule-testing` skill (Principle II — it is
  the authoritative source) **regardless** of whether the chosen path is a
  container or a VM.

**Must NOT Have**

- No `bd dolt set data-dir <absolute-path>` anywhere (Principle X portability).
- No claim that `metadata.json` propagates server mode through git (it does not).
- No `bd` in the systemd `ExecStart` — the unit runs `dolt sql-server` directly.
- No remote/cloud Dolt, no `dolt sql-server` exposed beyond loopback.
- No rewrite of beads internals or custom MySQL client — use `bd dolt set` only.
- No second `dolt sql-server` spawned by beads auto-start in `.beads/dolt/`.
- No `ignore_errors`-style silent skips, no `default('')`/`default(omit)` for
  required values (Principle XII).
- No duplicated port/path/version literals — single source via role vars
  (Principle XI).

## Data propagation — server mode through git (CORRECTED)

Only `.beads/config.yaml` is git-tracked (it predates the `.git/info/exclude`
`.beads/` entry; already-tracked files bypass ignore rules). `metadata.json` is
untracked **on this machine** because of that local, per-clone exclude — which is
**not cloned**. Whether `metadata.json` exists on a **fresh clone** depends on
beads' own first-run init behavior, **not** on this repo's local exclude, and is
a **Step 0 open question** (do not pre-decide it). So:

- For server mode, write host/port into `config.yaml` via
  `bd dolt set host 127.0.0.1 --update-config` and
  `bd dolt set port {{ dolt_beads_port }} --update-config` (these update
  `config.yaml`). **Do NOT** set data-dir via `bd` (Principle X).
- **Open verification (Step 0 / implementation):** on a fresh clone with NO
  `metadata.json`, does `bd` initialise in server mode from `config.yaml` alone,
  or does it regenerate `metadata.json` defaulting to `embedded`? If the latter,
  the role MUST add a task that forces server mode on first run (e.g. re-running
  `bd dolt set host/port` against the fresh clone, or whatever `bd` command
  re-derives mode from `config.yaml`). This must be settled empirically; a role
  task placeholder is included in Step 4 with a loud assertion that post-task
  `bd dolt status` reports `server`.

## Key Design Decision — server data-dir location

The systemd unit's `--data-dir` must resolve deterministically on every VM, but
VMs may clone the repo to different paths.

- **A. Hardcode repo path as a role var** — couples the unit to one clone path;
  brittle on churning VMs / multiple worktrees.
- **B. Env file resolving the repo path at provision time** — flexible but adds a
  second source of truth for the path.
- **C. Fixed absolute data-dir outside the repo** (`~/.local/share/dolt-beads/`)
  — server owns a stable, clone-independent data dir; `bd` reaches it via
  host/port over TCP (not by path). Survives repo moves and multiple worktrees.

**Decision: Option C (fixed absolute data-dir outside the repo).** In server
mode, `bd` clients connect by **host/port over TCP**, not by filesystem path — so
the server's data-dir need not live inside any clone. The data-dir path becomes a
role var (`dolt_beads_data_dir`, default `~/.local/share/dolt-beads`), **injected
ONLY into the systemd unit's `ExecStart --data-dir=` flag** — never via
`bd dolt set data-dir` (Principle X). Acknowledge explicitly: because `bd`'s own
transparent auto-start may use a *different* default data-dir (`.beads/dolt/`)
than the systemd unit, **split-brain (two servers, two data-dirs) is the key
safety risk** — handled by the designed single-server mechanism in Step 3.

## Molecule/systemd feasibility decision — DECIDE BEFORE SCAFFOLDING

The repo's existing Molecule scenarios use `ubuntu:24.04` + `pre_build_image:
true` with **no init system, no systemd, no cgroup mounts** (verified in
`roles/podman/molecule/default/molecule.yml`). Acceptance criteria asserting
`systemctl --user is-active`, `loginctl enable-linger`, and "restart brings the
server back" **cannot pass** in that topology.

**Two paths; exactly one must be chosen and justified before scaffolding:**

- **Path A — Systemd-capable container.** Use a systemd-as-PID-1 image (cgroup v2
  mounts + `--privileged` or specific mounts, dbus + `XDG_RUNTIME_DIR` for
  `--user` scope). A deliberate deviation from the repo's other scenarios. Honest
  caveat: `--user` systemd in a container is fragile and may not faithfully
  reproduce reboot-persistence (linger across an actual reboot cannot be tested
  in a container). Stays in the "containerized" column of Principle II.
- **Path B — Vagrant/Tart VM validation.** Declare this role **"cannot be
  containerized"** per Principle II/III/Technology-Stack (`constitution.md:286-287`
  explicitly lists Vagrant+Tart / Vagrant+Docker "for roles that cannot be
  containerized"). The role tests linger + reboot persistence, which containers
  cannot faithfully simulate. No `molecule/default/` scenario; route to the
  Vagrant-based VM procedure. Slower, but honest about what the topology proves.

**Recommended decision: Path B (Vagrant/Tart VM)** — because the *entire point*
of the systemd unit + linger is **reboot persistence**, which a container cannot
prove. Asserting `systemctl --user is-active` in a non-systemd container would be
a false-confidence test. Path B is the only one that validates the actual
guarantee (server survives reboot on a headless VM).

**Justification recorded:** Principle III (test-locally-first) requires the test
to actually exercise the behaviour. Reboot persistence is the load-bearing
behaviour; only a VM exercises it. The `molecule-testing` skill remains the
authoritative source for whichever harness is authored (Principle II), even when
the harness is the Vagrant procedure rather than a `molecule/` scenario.

> Note: if Step 0 collapses the role to "install binary + commit config" (no
> systemd/linger), the feasibility question is moot and a **plain Molecule
> container scenario suffices** (no init system needed). Re-evaluate this decision
> after Step 0.

## Complexity Tracking (Governance — `constitution.md:366-368`)

Principle IV (Simplicity/YAGNI) exceptions MUST be documented here before
implementation. The following components are introduced **only if the Step 0
spike confirms beads' auto-start does NOT already support concurrent
cross-worktree writes**. If the spike shows auto-start suffices, the systemd /
linger / external-data-dir rows are **removed** and only the Dolt-install row
remains.

| Component | Why needed | Simpler alternative rejected |
|-----------|-----------|------------------------------|
| User systemd unit (`dolt sql-server` direct) | Persistent single shared server decoupled from any `bd` invocation; survives the lifetime of any one agent/worktree | Rely on beads' transparent auto-start — rejected IF Step 0 shows auto-start spawns per-worktree servers / fails concurrent writes. If Step 0 shows it works, this row is deleted and the unit is not built. |
| `loginctl enable-linger` | Boot/reboot persistence on a headless VM with no interactive login | Start server on first `bd` call — rejected: not reboot-persistent; agent VM after reboot would have no server until a manual/auto trigger. |
| External fixed data-dir (`~/.local/share/dolt-beads`) | Clone-independent, shared by all worktrees over TCP; deterministic for the unit | In-repo `.beads/dolt/` — rejected: couples to one clone path, breaks on multiple worktrees / repo moves. `bd dolt set data-dir <abs>` — rejected per Principle X (commits machine-specific path to `metadata.json`). |
| Arch-aware Dolt binary install (v2.0.8) | Fresh VMs have no Dolt and may be arm64 or amd64; must fetch the correct asset | Assume Dolt pre-installed — rejected: false on fresh ephemeral VMs (verified). Single-arch download — rejected: VMs may be either arch. |

## Privilege boundary & auth (documented accepted risks)

- Installing Dolt to `/usr/local/bin/dolt` (system path) **requires `become:
  true`** (root/sudo). The user systemd unit, linger, and `bd` config tasks run
  **as the service user** (no `become`). Tasks MUST be split accordingly:
  install = privileged; unit/linger/config/bootstrap = unprivileged service user.
- **Dolt auth:** the server binds loopback (`127.0.0.1`) with `user=root`, **no
  password** by default. This is **accepted** as a local-only risk: the port is
  never exposed beyond loopback, consistent with the "local-only" principle. Note
  this explicitly in the role docs and `verify` (assert bind is loopback-only).

## Task Flow

```
[0 SPIKE: auto-start concurrency test] -gate->
  (A) auto-start suffices -> [collapse: install binary + commit config] -> [6 Test]
  (B) scaffold needed ->
    [1 Scaffold role + vars] -> [2 Install Dolt v2.0.8 (arch-aware, become)] ->
    [3 systemd user unit + linger + single-server assert] ->
    [4 Point beads at server via config.yaml] ->
    [5 Migrate existing data: bd backup sync -> bd backup restore --force] ->
    [6 Test (VM or systemd-container) + concurrency proof]
```

## Detailed TODOs

### Step 0 — SPIKE (gate): does beads auto-start already support concurrent writes?

- On the current machine, create **two sibling git worktrees** of this repo
  (`git worktree add`).
- From each worktree, run **interleaved/simultaneous** `bd create` / `bd update`
  writes (background loops in both worktrees at once).
- Observe and record:
  - Do **both** sets of writes succeed (no lock errors)?
  - Is a **single** shared `dolt sql-server` process used, or do **two** spawn?
    (`pgrep -af "dolt sql-server"`, inspect data-dirs / ports.)
  - Where does each worktree's server put its data-dir (`.beads/dolt/` per
    worktree, or one shared location)?
- Also verify the `config.yaml`-only propagation question: in a fresh clone with
  no `metadata.json`, does `bd` derive mode from `config.yaml`?
- **Branch on result:**
  - **(A) Concurrent writes succeed via auto-start + one shared server** →
    *candidate to collapse the role*: (a) install the arch-aware Dolt binary on
    fresh VMs, (b) commit host/port in `config.yaml`. **Drop**
    systemd/linger/external data-dir. Delete the corresponding Complexity Tracking
    rows. Document the simpler approach and skip Steps 3 and (most of) 4.
    - **Fresh-VM re-confirmation gate (MANDATORY before collapsing):** a green
      Branch-A result on the **dev machine** is **necessary but NOT sufficient**.
      Before dropping the role (systemd/linger/data-dir), the concurrent-write
      result **MUST be re-confirmed on one fresh VM** (cold start, no
      `metadata.json`, no warm beads server).
    - **Rationale:** the dev machine has a `metadata.json` and a warm,
      already-running beads server; a fresh VM has **neither**. The concurrent-write
      behavior on a cold start may differ from the warm dev machine, so the dev
      result alone cannot be trusted to generalize.
    - **Only after fresh-VM re-confirmation** is the Branch-A conclusion trusted
      and the complexity (systemd/linger/external data-dir) dropped. If the fresh
      VM does **not** reproduce the green result, fall through to Branch B (full
      Option A).
  - **(B) Concurrent writes fail (lock errors) or two servers spawn** → proceed
    with full Option A, Steps 1-6, with all fixes in this revision applied.
  - **(C) Auto-start always spawns its own server regardless of running config**
    → Option A's single-server premise is in doubt; document this as a blocker
    and re-open the options analysis before scaffolding.
- **Acceptance:** the spike's result and chosen branch are written into this plan
  (and the PR description). No role code is written before this gate is recorded.
  **For Branch A specifically:** the collapse is NOT accepted on the dev-machine
  result alone — it is accepted only after the **fresh-VM re-confirmation gate**
  (cold start, no `metadata.json`) reproduces the green concurrent-write result.
  A dev-machine green is necessary but not sufficient; record both the dev-machine
  and the fresh-VM outcomes before dropping systemd/linger/data-dir.

---

### SPIKE RESULT (recorded 2026-05-30): **Branch A — concurrent writes already work**

**Dev-machine findings:**

| Observation | Result |
|-------------|--------|
| Two sibling worktrees created | ✅ `/tmp/beads-spike-wt` (detached HEAD) + main worktree |
| Both worktrees share ONE database | ✅ Both resolve to `/home/galadriel/.../embeddeddolt` (git-root resolution) |
| 2 simultaneous writes | ✅ Both succeeded, exit 0, no lock errors |
| 10 simultaneous writes (5 from each worktree) | ✅ 10/10 succeeded, zero errors |
| Dolt server spawned mid-write | ❌ None — `pgrep dolt sql-server` = empty |
| `.beads/dolt/` created | ❌ Not created (no auto-start server) |
| Issues visible across worktrees | ✅ Both worktrees see all issues in the shared db |

**Additional finding (not in original plan):** `bd` binary is 123.7 MB, links only to
`libc.so.6` — Dolt is **statically embedded** in `bd`. System `/usr/local/bin/dolt`
is needed ONLY for server mode (`dolt sql-server`); embedded mode requires no system
Dolt binary. This eliminates the "install Dolt on fresh VMs" step for embedded mode.

**Mechanism:** beads resolves `.beads/` by walking to the git root, not the current
working directory. All worktrees of the same repo share the same git root and therefore
the same `.beads/embeddeddolt/` database path. Concurrent writes are serialized
internally by Dolt's WAL; all writes succeed.

**Branch A0 scope (what this means for the role):**
- System Dolt binary install: **NOT needed** (bd bundles Dolt)
- User systemd unit + linger: **NOT needed** (YAGNI — embedded mode handles concurrency)
- External data-dir: **NOT needed** (shared via git root, not TCP)
- config.yaml host/port: **NOT needed** for embedded mode (no server to point at)
- Complexity Tracking rows (systemd, linger, data-dir, arch-aware install): **all removed**

**Fresh-VM re-confirmation status:** NOT yet completed (no fresh VM available).
The plan requires this before fully collapsing the role. Until then, the Branch A0
finding is provisional. If fresh-VM test contradicts, fall back to Branch B.

**Practical consequence:** Task 1l6's original goal (concurrent writes across parallel
agents) is **already achieved** by beads v1.0.4's embedded mode + git-root resolution.
The Dolt SQL server setup (the original deliverable) is YAGNI on the current machine.
The remaining work is: (1) document this finding + PR, (2) migration (US-009).

---

### Step 1 — Scaffold the role and its vars (Branch B only)

- Create `roles/dolt-beads-server/` with `defaults/main.yml`, `tasks/main.yml`,
  `meta/main.yml`, `templates/`, matching existing role layout (e.g.
  `roles/podman/`). The test harness directory depends on the
  Molecule/systemd-feasibility decision (Path A = `molecule/default/`; Path B =
  Vagrant procedure, no `molecule/`).
- Define role vars in `defaults/main.yml`: `dolt_beads_version` (**`2.0.8`**),
  `dolt_beads_port` (default `3309`), `dolt_beads_data_dir`
  (`~/.local/share/dolt-beads`), `dolt_beads_user`, `dolt_beads_bind`
  (`127.0.0.1`).
- Add an `assert` task validating required vars are defined and non-empty
  (Principle XII).
- **Acceptance:** role directory matches conventions; `assert` fails loudly if a
  required var is missing; no literals duplicated outside defaults.

### Step 2 — Install the Dolt binary (arch-aware, idempotent, privileged)

- Map `{{ ansible_architecture }}` → Dolt asset (`aarch64`→`arm64`,
  `x86_64`→`amd64`); **fail loud** on an unmapped arch.
- Check installed version (`dolt version`); skip download if it already equals
  `dolt_beads_version` (**2.0.8**) (idempotency guard).
- Download the matching **v2.0.8** release tarball, extract `dolt` to
  `/usr/local/bin/dolt` **with `become: true`** (system path needs root); verify
  the binary runs.
- **Acceptance:** on a fresh target `dolt version` reports `2.0.8`; re-running the
  role reports `ok` (not `changed`) for install tasks.

### Step 3 — Create the user systemd unit + linger + single-server mechanism (Branch B only)

- Template `~/.config/systemd/user/dolt-beads.service` (as the service user, no
  `become`):
  `ExecStart=/usr/local/bin/dolt sql-server --host=127.0.0.1
  --port={{ dolt_beads_port }} --data-dir={{ dolt_beads_data_dir }}`,
  `Restart=on-failure`, `WantedBy=default.target`. **data-dir lives ONLY here.**
- Ensure `dolt_beads_data_dir` exists (owned by the service user).
- `loginctl enable-linger {{ dolt_beads_user }}` (idempotent — check current
  linger state first).
- Enable + start the unit via `ansible.builtin.systemd_service` with
  `scope: user`.
- **Designed single-server mechanism (replaces the old vague "note"):**
  - The unit starts `dolt sql-server` on the pinned port at the fixed data-dir.
  - `bd` is configured (git-tracked `config.yaml`: host=127.0.0.1,
    port=`{{ dolt_beads_port }}`) so that when beads would auto-start a server it
    instead **connects to the already-bound port**.
  - **Assertion (must pass):** exactly ONE `dolt sql-server` bound to the pinned
    port — `pgrep -af "sql-server.*{{ dolt_beads_port }}" | wc -l == 1` — **and**
    `.beads/dolt/` was **never created** (confirming auto-start did not spawn a
    second server in its default location).
  - **Spike-within-step:** if beads' auto-start cannot be controlled by config
    alone (it always spawns its own server regardless of a running one), Option A
    is undermined — STOP and document; reconsider the approach (link back to Step
    0 branch C).
- **Acceptance:** `systemctl --user is-active dolt-beads` = active; port bound on
  loopback only (`ss -tlnp`); **single-server assertion passes**; `.beads/dolt/`
  absent; after `systemctl --user restart` the server returns unattended;
  re-running the role is idempotent.

### Step 4 — Point beads at the local server (persisted via config.yaml)

- `bd dolt set host 127.0.0.1 --update-config` and
  `bd dolt set port {{ dolt_beads_port }} --update-config` so **`config.yaml`**
  (the only git-tracked beads file) carries the worktree-wide default. **Do NOT
  set data-dir via `bd`** (Principle X).
- **Fresh-clone server-mode task:** whether `metadata.json` is present or absent
  on the fresh clone (this is settled by Step 0, not pre-decided — a fresh clone
  does NOT inherit this machine's local `.git/info/exclude`), ensure `bd` comes
  up in server mode from `config.yaml`. Run the mode-deriving command (verified
  in Step 0) and **assert** `bd dolt status` = `server`. If `bd` creates or keeps
  `metadata.json` defaulting to embedded, this task forces server mode loudly
  (Principle XII).
- Auto-commit policy: default `on` for durability (Fail Loud); not `batch`.
- **config.yaml tracking guard (run after `bd dolt set ... --update-config`):**
  the `--update-config` writes must land in a *git-tracked* `config.yaml`, not be
  silently swallowed by the blanket `.beads/` entry in `.git/info/exclude`.
  Assert both:
  1. `git ls-files .beads/config.yaml` returns **non-empty** — proves
     `config.yaml` is still tracked (already-tracked files bypass the exclude).
  2. `git status --short .beads/config.yaml` **reflects the change** — proves the
     write is visible to git and will actually be committed.
  - **If either fails loud:** the `.beads/` exclude is silently ignoring
    `config.yaml`; fix by explicitly forcing it with
    `git add --force .beads/config.yaml` and **document the need** in the role
    (Principle XII — no silent loss of the server-mode config).
- **Acceptance:** `bd dolt show`/`status` reports server mode + host/port; a fresh
  shell (no env vars) connects to the same server; **`config.yaml` carries
  host/port** (no reliance on `metadata.json`); **the config.yaml tracking guard
  above passes** (`git ls-files` non-empty AND `git status --short` reflects the
  change).

### Step 5 — Migrate existing data to the server (current machine only)

- **Scope:** migration applies only to the current machine's embedded DB. Fresh
  VMs start with whatever beads initialises on first `bd` invocation — no
  migration step needed there.
- **Pre-migration snapshot:** record `bd list | wc -l` and `bd stats` as baseline
  before touching the DB.
- **Back up the embedded DB:** confirm a backup destination is configured
  (`bd backup status`); if not, initialise one (`bd backup init ~/.beads-backup`
  or equivalent). Run `bd backup sync` while still in embedded mode to push the
  full Dolt DB (history included) to the backup.
- **Switch to server mode:** Steps 3+4 must already be complete (server running,
  `config.yaml` updated). Now restore into the server-backed DB:
  `bd backup restore --force` (overwrites the server's current empty DB with the
  backed-up embedded data, preserving full Dolt history).
- **Verify:** `bd list | wc -l` matches the pre-migration baseline; spot-check 3
  issues by title/status/deps; `bd dolt status` = server; `bd doctor` clean.
- **Note:** `bd restore --force` is NOT the correct command — it restores a
  compacted issue from Dolt history (read-only). The correct migration command is
  `bd backup restore --force` (restores the entire DB from a Dolt backup).
- **Acceptance:** issue count matches baseline; spot-check passes; server mode
  confirmed; `bd doctor` clean; embedded data dir archived (not deleted until
  proof passes).

### Step 6 — Test scenario + concurrency proof (per the feasibility decision)

- **Invoke the `molecule-testing` skill** (Principle II — authoritative) for
  whichever harness the feasibility decision selected:
  - **Path A (systemd container):** author `molecule/default/` (systemd image +
    cgroup mounts) covering create → prepare → converge → idempotence → verify →
    destroy.
  - **Path B (Vagrant/Tart VM, recommended):** author the VM-based validation
    procedure; assert reboot persistence (provision → reboot → server still
    active).
- **Verify** asserts: Dolt binary at **2.0.8**; unit active; port bound on
  `127.0.0.1` only; linger enabled; **single-server assertion** (one process,
  `.beads/dolt/` absent); `bd dolt status` = server.
- **Concurrency proof:** launch 2+ concurrent `bd update`/`bd create` writes
  (background loops / separate worktrees); confirm all succeed with zero lock
  errors and all writes land. Run `bd doctor` clean.
- Run the test (Principle III) — must pass including idempotence (Path A) or
  reboot-persistence (Path B).
- **Acceptance:** test green end-to-end; concurrent writers all commit with no
  lock errors; single-server assertion holds; `bd doctor` clean.

## Success Criteria

- **Step 0 spike result recorded** and the chosen branch (collapse vs full Option
  A) documented before any role code.
- `roles/dolt-beads-server/` exists, is idempotent, and passes its chosen test
  harness (Molecule systemd-container **or** Vagrant/Tart VM procedure).
- On a fresh VM the role installs the arch-correct **Dolt 2.0.8** binary
  (privileged install), and — if Branch B — stands up a boot-persistent loopback
  `dolt sql-server` user unit with linger and **exactly one** server (no
  `.beads/dolt/` second server).
- `bd dolt status` reports server mode against localhost; a fresh shell connects
  with no manual start; **server mode derives from git-tracked `config.yaml`**
  (not `metadata.json`).
- Existing data migrated via `bd backup sync` + `bd backup restore --force`:
  post-migration issue count matches pre-migration baseline; spot-check passes;
  `bd doctor` clean.
- 2+ concurrent `bd` writers succeed with no lock errors (primary proof).
- Server bound to `127.0.0.1` only, `user=root` no-password local-only (accepted
  risk documented); no remote exposure.

---

## RALPLAN-DR Summary

**Mode:** SHORT (reversible, additive infra config; gated by a spike and by local
test-first). Risk bounded by the Step 0 spike, the chosen test harness, and the
git-tracked `issues.jsonl` as the source of truth for issue data.

### Principles (decision filter)

1. **Role-First + Molecule (Constitution II).** Reproducibility on ephemeral VMs
   requires a role with an authoritative `molecule-testing`-authored harness;
   manual steps do not survive churn.
2. **Idempotency (Constitution I).** Install guarded by version check; unit and
   linger declarative; bootstrap import guarded against duplication.
3. **Simplicity / YAGNI (Constitution IV).** A spike (Step 0) tests whether beads'
   auto-start already solves concurrency before any systemd/linger/data-dir
   scaffold is built; the Complexity Tracking table justifies anything that
   survives the spike.
4. **Fail Loud (Constitution XII).** `assert` required vars; arch-map failure
   loud; single-server assertion; server-down errors clearly; no silent
   fallbacks.
5. **No Machine-Specific Paths in Durable Artefacts (Constitution X, by
   analogy).** Never commit an absolute data-dir to `metadata.json` via
   `bd dolt set data-dir`; data-dir lives only in the systemd `ExecStart` flag.

### Decision Drivers (top 3)

1. **Reproducibility on ephemeral VMs** — fresh VM has no Dolt, no server, no data
   dir, no `metadata.json`; everything must come from a role run.
2. **Concurrent write support** — embedded = single writer; the spike decides
   whether server mode (or auto-start) already gives many writers.
3. **Boot persistence without interactive login** — headless agent VMs need the
   server up after reboot via user systemd + linger (only a VM, not a container,
   can prove this).

### Required gate — Step 0 spike

The full Option A (systemd/linger/external data-dir) is **NOT** adopted until the
Step 0 spike confirms beads' transparent auto-start does **not** already support
concurrent cross-worktree writes via a single shared server. If it does, the role
collapses to "install Dolt 2.0.8 + commit host/port in `config.yaml`" and the
systemd/linger/data-dir Complexity Tracking rows are removed.

### Corrected propagation mechanism

Server mode propagates through git via **`config.yaml` ONLY**. `metadata.json` is
**not** git-tracked and is absent on fresh clones; no design may rely on it. A
fresh-clone task forces server mode from `config.yaml` and asserts
`bd dolt status` = server.

### Molecule/systemd feasibility decision

Existing scenarios use a non-systemd `ubuntu:24.04` container, so
`systemctl --user`/linger/reboot assertions cannot pass there. **Recommended:
Path B — Vagrant/Tart VM** (per `constitution.md:286-287`, for roles that "cannot
be containerized"), because reboot persistence is the load-bearing guarantee and
only a VM proves it. Path A (systemd-capable container) is the documented
alternative if a VM harness is infeasible. The `molecule-testing` skill authors
whichever harness is chosen. *(If Step 0 collapses the role, a plain Molecule
container scenario suffices — re-evaluate.)*

### Complexity Tracking

The Complexity Tracking table (above) documents the user systemd unit, linger,
external data-dir, and arch-aware Dolt install as Principle IV exceptions —
conditional on the Step 0 spike confirming they are necessary. If the spike shows
auto-start suffices, only the Dolt-install row remains.

### Viable Options

**Option A — Beads server mode + Ansible role `dolt-beads-server` (RECOMMENDED,
gated by Step 0)**

Arch-aware Dolt 2.0.8 install + user systemd unit (running `dolt sql-server`
directly) + `enable-linger` + `config.yaml` server config + single-server
assertion + data migration via `bd backup sync` / `bd backup restore --force`,
validated by the chosen test harness.

- Pros: only option reproducible on a fresh VM (Driver 1); uses beads' first-class
  server path; fixed external data-dir is clone-independent (TCP shared);
  test-gated per Principle II/III; idempotent (Principle I).
- Cons: more upfront work than auto-start; requires the single-server mechanism +
  assertion to defeat split-brain; depends on the Step 0 spike result.

**Option A0 — Collapsed role (install binary + commit config only)** — *adopted
only if Step 0 branch A holds.*

- Pros: minimal surface (Principle IV); no systemd/linger/data-dir complexity;
  relies on beads' supported auto-start.
- Cons: depends entirely on the spike confirming auto-start shares one server and
  supports concurrent writes; no reboot-persistence guarantee beyond beads'
  on-demand start.

**Option B — Hand-rolled `dolt sql-server` + manual MySQL DSN**

- Pros: total control over server flags.
- Cons: duplicates `bd dolt set` (DRY XI / YAGNI IV); higher split-brain risk;
  more surface; still needs a role to be VM-reproducible. **Invalidated as
  default** — only if Option A's auto-start reconciliation proves unworkable
  (Step 0 branch C).

**Option C — Beads `--global` shared-server (`beads_global`) mode**

- Pros: built-in global shared server for multi-project sharing.
- Cons: changes DB identity/scope (global vs this project); broader blast radius
  than the single-repo need; migration semantics unverified. **Invalidated for
  now** (YAGNI) — revisit only if agents must share beads across multiple repos.

### Rationale for chosen option

Option A is the minimum solution satisfying all three drivers using beads' own
supported mechanism, packaged as a role to survive VM churn — **but only after**
the Step 0 spike confirms the scaffold is actually needed (else Option A0). The
`config.yaml`-only propagation, the single-server assertion, and the data-dir-in-unit
constraint (Principle X) close the specific gaps Architect and Critic flagged. Options B and C add scope or bespoke
surface that Principles IV/XI rule out absent a concrete failure of A (Step 0
branch C).

---

## Open Questions (also appended to .omc/plans/open-questions.md)

Resolved by the user (defaults accepted):

1. **Auto-commit policy** — `on` (durable, Fail Loud). RESOLVED.
2. **Data dir location** — RESOLVED: Option C, fixed `~/.local/share/dolt-beads`
   outside the repo, injected ONLY via the systemd `ExecStart --data-dir` flag
   (never `bd dolt set data-dir`).
3. **Reproduce as an Ansible role?** — RESOLVED: YES, required (pending the Step 0
   spike, which may collapse it to install+config).
4. **Pinned port value** — RESOLVED: default `3309` (role var).
5. **Pinned Dolt version** — RESOLVED: `2.0.8` (arm64 + amd64 assets confirmed).

Still open — to verify during the Step 0 spike / implementation:

6. **Auto-start concurrency (THE GATE)** — does beads' transparent auto-start
   already support concurrent cross-worktree writes via one shared server? Decides
   collapse vs full Option A. Why it matters: if yes, the entire systemd/linger/
   data-dir scaffold is YAGNI.
7. **`config.yaml`-only server mode on fresh clone** — first, **does
   `metadata.json` even exist on a fresh clone?** This machine's `metadata.json`
   is untracked only because of a local, never-cloned `.git/info/exclude`; a
   fresh clone does NOT inherit that exclude, so its presence depends on beads'
   own first-run init, which **Step 0 must settle empirically** (not pre-decided).
   Then: whether `metadata.json` is present or absent, does `bd` derive server
   mode from `config.yaml`, or regenerate/keep `metadata.json` defaulting to
   embedded (requiring a forced-mode task)? Why it matters: server mode must
   survive a clone regardless of how beads init treats `metadata.json`.
8. **Auto-start controllability** — can config alone stop beads from spawning a
   second server in `.beads/dolt/`? If not, Option A's single-server premise
   fails. Why it matters: split-brain (two servers/data-dirs) would silently
   diverge issue data.
