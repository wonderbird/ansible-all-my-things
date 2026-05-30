# Open Questions Tracker

## nkb — Refine docker-publish.yml: build → test → push order — 2026-05-15

- [ ] Per-arch cosign signing vs manifest-list fan-in — Confirm
  signing each per-arch tag independently is acceptable, or whether
  nkb should also introduce a manifest-list fan-in step (currently
  out of scope). Matters because consumers verifying via
  `latest` (no arch suffix) need a manifest list to exist.
- [ ] `workflow_dispatch` from forks — Confirm whether
  `workflow_dispatch` triggered from a fork should be allowed to
  reach the push job. GitHub Actions defaults disallow this for
  fork-owned runs, so no extra guard is added; flag if explicit
  belt-and-braces gating is desired.
- [ ] `concurrency:` block on `main` — Decide whether to add a
  workflow-level `concurrency:` group keyed on `main` in a separate
  change. Out of scope for nkb; would prevent two rapid commits from
  racing on unqualified tags. Matters if push cadence ever increases.
- [ ] Manifest-list fan-in follow-up — File
  `ansible-all-my-things-nkb-followup-manifest` to add
  `docker buildx imagetools create` for a proper multi-arch `:latest`
  manifest. nkb intentionally leaves `:latest` as amd64-only to
  eliminate the matrix-leg race deterministically; this is a known
  Principle VIII tracked debt item, not a silent compromise.

## Persistent local Dolt SQL server for concurrent beads writes — 2026-05-30

Resolved by user (defaults accepted / role confirmed):

- [x] Dolt auto-commit policy — RESOLVED: `on` (durable per write, Fail
  Loud default).
- [x] Server data-dir location — RESOLVED: fixed absolute path
  `~/.local/share/dolt-beads` outside the repo. Server mode connects
  over TCP (host/port), so clients are decoupled from clone path; one
  server shared by all worktrees.
- [x] Reproduce as an Ansible role? — RESOLVED: YES, required. VMs are
  ephemeral (fresh VM per session, no pre-installed Dolt); manual steps
  do not survive churn. Role `dolt-beads-server` + Molecule scenario is
  the core deliverable (Constitution II/III).
- [x] Pinned port value — RESOLVED: pin a fixed port, default `3309`
  (role var `dolt_beads_port`).

Still open — verify during the Step 0 spike / implementation (revised after
Architect + Critic ITERATE):

- [ ] Auto-start concurrency (THE GATE — Step 0 spike) — does beads'
  transparent auto-start already support concurrent cross-worktree writes
  via one shared server? Decides collapse (install+config only) vs full
  Option A (systemd/linger/external data-dir). Matters because if yes, the
  entire scaffold is YAGNI.
- [ ] `config.yaml`-only server mode on fresh clone — with no
  `metadata.json` (NOT git-tracked; absent on fresh clones), does `bd`
  derive server mode from `config.yaml`, or regenerate `metadata.json`
  defaulting to embedded (requiring a forced-mode task)? Matters because
  fresh VMs have no `metadata.json`; server mode must survive a clone.
- [ ] Auto-start controllability — can config alone stop beads from
  spawning a second server in `.beads/dolt/`? If not, Option A's
  single-server premise fails. Matters because split-brain (two
  servers/data-dirs) would silently diverge issue data.
- [ ] Fresh-VM auto-import — does beads auto-import `.beads/issues.jsonl`
  on first connect to an empty server, or is `bd import` required? Step 5
  includes an idempotent import; executor must verify and trim if
  redundant (Principle IV). Matters because a fresh clone must
  self-bootstrap its 116 issues or every new VM starts with an empty
  tracker.

Decisions recorded in this revision (resolving Architect/Critic findings):

- [x] Migration semantics — RESOLVED: JSONL bootstrap (export-then-import),
  not raw Dolt DB move. Pre-cutover `bd export --all -o .beads/issues.jsonl`
  is mandatory; uncommitted embedded state is dropped unless exported first.
- [x] data-dir setting method — RESOLVED: ONLY via systemd `ExecStart
  --data-dir` flag; NEVER `bd dolt set data-dir <abs>` (Principle X — no
  machine-specific path in `metadata.json`).
- [x] Pinned Dolt version — RESOLVED: `2.0.8` (arm64 + amd64 assets confirmed).
- [x] Molecule/systemd feasibility — RESOLVED (recommended): Path B
  Vagrant/Tart VM (reboot persistence cannot be proven in the existing
  non-systemd container topology); Path A systemd-container is the documented
  alternative. `molecule-testing` skill authors either harness.
