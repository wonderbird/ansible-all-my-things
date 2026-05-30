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

Resolved by Step 0 spike (2026-05-30 — Branch A confirmed):

- [x] Auto-start concurrency (THE GATE) — RESOLVED: Branch A. 10/10
  concurrent writes from 2 sibling worktrees succeeded. beads resolves
  `.beads/` to git root; all worktrees share one embedded DB. No server
  needed. Entire server scaffold is YAGNI.
- [x] Auto-start controllability — RESOLVED: moot in Branch A. No server
  spawned; split-brain not possible in embedded mode.
- [x] `config.yaml`-only server mode on fresh clone — RESOLVED: moot in
  Branch A. Staying in embedded mode; no server-mode config needed.
- [x] Fresh-VM auto-import — RESOLVED: moot in Branch A. `bd` bundles
  Dolt statically; embedded mode works without a server or import step.
- [x] Migration semantics — RESOLVED: `bd backup sync` +
  `bd backup restore --force` (Dolt-native, user decision). Completed
  2026-05-30 after merge to main. Count stable: 128 pre = 128 post.
- [x] data-dir / Pinned version / Molecule — RESOLVED: all moot under
  Branch A (no server role built).

Still open (tracked):

- [ ] Fresh-VM re-confirmation — tracked as `ansible-all-my-things-888`
  (spike, P2). Must verify Branch A holds on cold start with no
  `metadata.json` before fully collapsing any server-mode role.
