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
