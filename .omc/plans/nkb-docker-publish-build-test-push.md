# nkb — Refine docker-publish.yml: build → test → push order

## Context

File: `.github/workflows/docker-publish.yml`

Today the workflow has two jobs (`build` → `test`). On non-PR events
(`push` to `main`, semver tags, schedule, `workflow_dispatch`) the
`build` job pushes the image to GHCR *before* the `test` job runs, then
signs with cosign. The `test` job pulls the already-pushed image and
runs `container-structure-test`. A failing test does not prevent the
image from existing in the registry.

The PR path is already correct (build → tarball artifact → load in test
job → no push). nkb generalises that pattern so non-PR builds are also
gated by tests.

Constitution constraints relevant here:

- `.specify/memory/constitution.md` Principle VIII (No Untracked
  Technical Debt) — every workaround must be logged or removed.
- AGENTS.md “Test environment host architecture” — never assume host
  arch; we already use a native per-arch matrix.

bd issue: `ansible-all-my-things-nkb` (P1, depends on ngu, blocks ru3).

## Work Objectives

1. Pipeline order is **build → test → push** on every event, including
   non-PR.
2. GHCR receives an image only after both arch test jobs pass.
3. Cosign signing remains intact and signs the digest of the image that
   was actually tested.
4. The PR path keeps its current shape and runtime profile (build →
   tarball → test, no push, no registry login on builder).
5. The fork-safe property from ngu is preserved (PRs from forks do not
   need `packages: write` or registry login).
6. Unqualified tags (`:latest`, semver `vX.Y.Z`, `vX.Y`, `vX`) are
   emitted by exactly one arch leg to eliminate the last-writer-wins
   race between matrix legs (Principle VIII compliance — known
   limitation logged as follow-up rather than ignored).

## Guardrails

### Must Have

- Three jobs: `build`, `test`, `push` (`push` skipped on PRs).
- Per-arch matrix on both `build` and `test` (amd64 on `ubuntu-24.04`,
  arm64 on `ubuntu-24.04-arm`).
- Test job loads the *same* artifact for PR and non-PR paths — single
  code path, no `if: pull_request` branching inside test steps.
- `push` job uses `needs: [build, test]` and `if: github.event_name !=
  'pull_request'`.
- Cosign signs the digest produced by the push job’s `docker push`
  step (read back from `docker inspect ... RepoDigests`), so signature
  matches the image that GHCR actually serves.
- Tags are computed deterministically in the `push` job via
  `docker/metadata-action`. The `build` job uses a **labels-only**
  `docker/metadata-action` call (no `tags:` input) — solely to bake OCI
  provenance labels into the tarball (see Step 1).
- Unqualified tags (`latest`, `vX.Y.Z`, `vX.Y`, `vX`) are arch-gated to
  `matrix.arch == 'amd64'`. Arch-qualified tags (`latest-amd64`,
  `latest-arm64`) are emitted per matrix leg as today.
- `permissions: packages: write` and `id-token: write` are scoped to the
  `push` job only. `build` and `test` only need `contents: read`.
- Workflow concurrency / artifact retention semantics unchanged
  (`retention-days: 1`).
- `RepoDigests` extraction filters by `IMAGE_NAME` so unrelated repo
  digests (from cache layers etc.) cannot leak into cosign input.

### Must NOT Have

- No `docker push` from the `build` job on any event.
- No registry login in `build` or `test` on any event.
- No second image build in the `push` job (rebuild would double CI cost
  and risk digest drift versus the tested artifact).
- No multi-arch manifest creation step in this change — per-arch tags
  (`latest-amd64`, `latest-arm64`) are preserved. Manifest fan-in
  (`docker buildx imagetools create`) is logged as a follow-up issue.
- No reliance on `pull_request` event metadata inside the `push` job
  (it never runs for PRs).
- No `--force` on cosign (matches current behaviour for public repo).
- No time-based tag patterns (`type=schedule`, timestamp-based) in
  `metadata-action` — those would diverge between `build` and `push` if
  both jobs ever invoked the action (see Step 4 comment requirement).
- No `concurrency:` block added in this change. Concurrent pushes to
  `main` are an acknowledged edge case and out of scope (see Risks).

## Task Flow

```
build (matrix: amd64, arm64)
  └── tarball artifact image-<arch>.tar.gz
        │
        ▼
test (matrix: amd64, arm64) — needs: build
  └── download artifact → docker load → container-structure-test
        │
        ▼  (only if github.event_name != 'pull_request')
push (matrix: amd64, arm64) — needs: [build, test]
  └── download artifact → docker load → metadata-action → docker push → cosign sign
```

## Detailed TODOs

### Step 1 — Restructure `build` job: always export tarball, never push, drop metadata-action

**Edit** `.github/workflows/docker-publish.yml`:

- **Replace the full `docker/metadata-action` call (with `tags:`) in the
  build job with the labels-only call described below.** The build job
  only needs OCI labels and a stable local image name; it does not need
  tag computation. Set `docker/build-push-action`’s `tags:` input
  directly to `test-image:${{ matrix.arch }}`.
- Add a **labels-only** `docker/metadata-action` step in the build job
  to preserve OCI provenance labels on the published image:

  ```yaml
  - id: meta
    uses: docker/metadata-action@030e881283bb7a6894de51c315a6bfe6a94e05cf # v6.0.0
    with:
      images: ${{ env.IMAGE_NAME }}
  ```

  No `tags:` input — this call is solely for `steps.meta.outputs.labels`.

- Replace `docker/build-push-action` inputs with:
  - `load: true`
  - `push: false`
  - `tags: test-image:${{ matrix.arch }}`
  - `labels: ${{ steps.meta.outputs.labels }}` — preserves
    `org.opencontainers.image.source`, `.revision`, `.created`, etc. in
    the tarball image so the push job publishes a fully-labelled image.
    `docker tag` / `docker push` alone cannot inject labels; they must be
    baked in at build time.
- Remove the non-PR-only login and cosign install steps from this job.
- Remove `permissions: packages: write` and `id-token: write` from the
  `build` job (only `contents: read` remains).
- Always run the “Save image tarball” + “Upload image artifact” steps
  (remove `if: github.event_name == 'pull_request'`). The tarball is
  the single source of truth handed downstream. The save step becomes:

  ```yaml
  - name: Save image tarball
    run: docker save test-image:${{ matrix.arch }} | gzip > image-${{ matrix.arch }}.tar.gz
  ```

  (No more `docker tag` from `steps.meta.outputs.tags | head -1` —
  `test-image:${{ matrix.arch }}` is already the canonical local name.)
- Keep `cache-from` / `cache-to` GHA cache scoped per arch.

**Acceptance criteria**

- `build` job runs identically on PR and non-PR events.
- `build` job has **no** `docker/metadata-action` step that emits tags
  (only the labels-only call described above is present).
- After `build`, two artifacts exist: `image-amd64`, `image-arm64`.
- No registry login, no `docker push`, no cosign step in `build`.
- `permissions` block in `build` contains only `contents: read`.
- `docker/build-push-action` `tags:` input is the literal
  `test-image:${{ matrix.arch }}`.

### Step 2 — Simplify `test` job: single artifact path

**Edit** the `test` job:

- Remove the non-PR branch entirely: delete the registry login step,
  the `docker pull` step, and the `if: pull_request` guards on
  download/load.
- Always download `image-${{ matrix.arch }}`, always `docker load`, always
  test `test-image:${{ matrix.arch }}`.
- Drop the `Set test image reference` shell step; hard-code
  `--image test-image:${{ matrix.arch }}` directly in the
  `container-structure-test` invocation.
- Keep matrix and `container-structure-test` installation as-is.
- Keep `permissions: contents: read` (or omit; default is read).

**Acceptance criteria**

- `test` job has no `if: github.event_name == ...` guards.
- Test steps execute identically on PR and non-PR.
- `needs: build` retained.

### Step 3 — Add `push` job: load artifact, push, sign

**Append** a new job `push` after `test`:

```yaml
push:
  needs: [build, test]
  if: github.event_name != 'pull_request'
  runs-on: ${{ matrix.runner }}
  permissions:
    contents: read
    packages: write
    id-token: write
  strategy:
    matrix:
      include:
        - runner: ubuntu-24.04
          arch: amd64
        - runner: ubuntu-24.04-arm
          arch: arm64
  steps:
    - uses: actions/checkout@v6
    - run: echo "IMAGE_NAME=${{ env.REGISTRY }}/${{ github.repository_owner }}/ansible-toolchain" >> $GITHUB_ENV
    - uses: sigstore/cosign-installer@cad07c2e89fa2edd6e2d7bab4c1aa38e53f76003 # v4.1.1
      with:
        cosign-release: 'v2.2.4'
    - uses: docker/setup-buildx-action@4d04d5d9486b7bd6fa91e7baf45bbb4f8b9deedd # v4.0.0
    - uses: docker/login-action@b45d80f862d83dbcd57f89517bcf500b2ab88fb2 # v4.0.0
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    # Tags are arch-gated to prevent matrix legs from racing on
    # unqualified tags (:latest, semver). amd64 emits both unqualified
    # and arch-qualified; arm64 emits only arch-qualified.
    # DO NOT add time-based tag patterns (type=schedule, timestamp)
    # here without piping tags between jobs — metadata-action is only
    # invoked in this job and must remain event-deterministic.
    - id: meta
      uses: docker/metadata-action@030e881283bb7a6894de51c315a6bfe6a94e05cf # v6.0.0
      with:
        images: ${{ env.IMAGE_NAME }}
        tags: |
          type=raw,value=latest,enable=${{ github.ref == format('refs/heads/{0}', github.event.repository.default_branch) && matrix.arch == 'amd64' }}
          type=raw,value=latest-${{ matrix.arch }},enable={{is_default_branch}}
          type=ref,event=pr
          type=semver,pattern={{version}},enable=${{ matrix.arch == 'amd64' }}
          type=semver,pattern={{major}}.{{minor}},enable=${{ matrix.arch == 'amd64' }}
          type=semver,pattern={{major}},enable=${{ matrix.arch == 'amd64' }}
    - uses: actions/download-artifact@v4
      with:
        name: image-${{ matrix.arch }}
    - name: Load image from artifact
      run: docker load < image-${{ matrix.arch }}.tar.gz
    - name: Tag image with metadata tags
      env:
        TAGS: ${{ steps.meta.outputs.tags }}
      run: |
        echo "$TAGS" | while IFS= read -r tag; do
          [ -z "$tag" ] && continue
          docker tag "test-image:${{ matrix.arch }}" "$tag"
        done
    - name: Push image
      id: push
      env:
        TAGS: ${{ steps.meta.outputs.tags }}
      run: |
        DIGEST=""
        while IFS= read -r tag; do
          [ -z "$tag" ] && continue
          docker push "$tag"
          if [ -z "$DIGEST" ]; then
            # Filter RepoDigests by IMAGE_NAME so unrelated digests
            # (cache layers, sibling images) cannot leak in.
            DIGEST=$(docker inspect --format='{{range .RepoDigests}}{{println .}}{{end}}' "$tag" \
              | grep "^${IMAGE_NAME}@" \
              | head -1 \
              | cut -d@ -f2)
          fi
        done <<< "$TAGS"
        echo "digest=$DIGEST" >> "$GITHUB_OUTPUT"
    - name: Sign the published Docker image
      env:
        TAGS: ${{ steps.meta.outputs.tags }}
        DIGEST: ${{ steps.push.outputs.digest }}
      run: echo "${TAGS}" | xargs -I {} cosign sign --yes {}@${DIGEST}
```

**Acceptance criteria**

- `push` job runs only on non-PR events.
- `push` job depends on `[build, test]`; if either fails, no push.
- Per-arch matrix matches `build`/`test`.
- The exact tarball tested in `test` is what gets pushed (load → tag →
  push of `test-image:${{ matrix.arch }}`).
- Unqualified tags (`:latest`, semver) appear in `meta.outputs.tags`
  **only** when `matrix.arch == 'amd64'`. Inspect a non-PR run log on
  the arm64 leg and confirm only `latest-arm64` is emitted.
- `RepoDigests` extraction is filtered by `IMAGE_NAME` (grep step in
  the push script).
- Digest used by cosign is read back from the pushed image via
  `docker inspect ... RepoDigests` after `docker push`. Cosign signs
  every tag at `{tag}@{digest}`.
- `id-token: write` and `packages: write` exist only on this job.

### Step 4 — Confirm metadata-action tag computation lives only in the `push` job

`docker/metadata-action` with `tags:` is invoked **only** in the `push`
job. The `build` job has a labels-only `metadata-action` call (no `tags:`
input) — this does not participate in tag computation and creates no
cross-job determinism concern. There is therefore no cross-job tag
plumbing required.

**Acceptance criteria**

- A comment near the top of the workflow documents:
  - tag computation via `metadata-action` runs only in the push job;
  - the build job's `metadata-action` is labels-only (no `tags:` input);
  - no cross-job tag plumbing is needed;
  - **do not add time-based tag patterns (`type=schedule`,
    timestamp-based) to `metadata-action` without piping tags between
    jobs** — adding them would re-introduce the determinism question
    this design avoids.
- No `outputs:` block added to `build` for tag passing.
- `build` job contains no `docker/metadata-action` step that emits tags
  (cross-check with Step 1 acceptance).

### Step 5 — Update pipeline overview comment

Replace the top-of-file comment block (lines 3–7) with the new
build → test → push description, and update the “PR path / non-PR path”
sentences to reflect the unified artifact flow. Include the
metadata-action placement note from Step 4.

**Acceptance criteria**

- Comment accurately describes 3 jobs and the artifact handoff.
- Comment states that unqualified tags are amd64-only by design.
- No stale references to “push in build job”.

### Step 6 — Lint, full two-path verification, and upstream PR

**Local lint / sanity check:**

```
yamllint .github/workflows/docker-publish.yml
# fallback if yamllint absent:
python -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" \
  .github/workflows/docker-publish.yml
```

---

**Stage A — PR path (feature → fork/main):**

Open a PR from `feature/fork-safe-docker-ci` to `eudicy/ansible-all-my-things`
`main`. CI runs on the fork. Expected: `build` (×2) + `test` (×2) pass,
`push` job absent (PR event).

```
gh run watch   # monitor via CLI
```

---

**Stage B — Non-PR path: DAG-only pre-check (optional, before merge):**

Trigger `workflow_dispatch` on the feature branch to verify job ordering
and permissions without touching the registry:

```
gh workflow run docker-publish.yml --ref feature/fork-safe-docker-ci
gh run watch
```

All three jobs (`build`, `test`, `push`) must appear and succeed.
`$TAGS` is empty on a non-default branch so the push loop is a no-op —
this validates **DAG order and permissions only**, not actual push or
cosign.

---

**Stage C — Non-PR path: full push + cosign (merge to fork/main):**

Merge the PR from Stage A. The merge push to fork `main` triggers the
non-PR path: build → test → push to `ghcr.io/eudicy/ansible-toolchain`.

Monitor:

```
gh run watch
gh run view <run-id> --log   # stream full logs
```

If the push job fails mid-run:

```
# Identify pushed versions
gh api /user/packages/container/ansible-toolchain/versions

# Delete bad version
gh api --method DELETE \
  /user/packages/container/ansible-toolchain/versions/<version-id>

# Revert commit if needed
git revert HEAD && git push
```

Cosign verification after successful run:

```
cosign verify \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp 'github.com/eudicy/ansible-all-my-things' \
  ghcr.io/eudicy/ansible-toolchain@<digest>
```

Run for at least one amd64-only tag (`:latest`) and one arch-qualified
tag (`:latest-arm64`).

---

**Stage D — Upstream PR:**

After Stage C passes, open a PR from `eudicy/ansible-all-my-things`
`main` to `wonderbird/ansible-all-my-things` `main`:

```
gh pr create \
  --repo wonderbird/ansible-all-my-things \
  --head eudicy:main \
  --base main
```

Upstream CI sees a PR event → exercises PR path only (already verified
in Stage A).

---

**Debugging failed runs:**

```
gh run list --workflow=docker-publish.yml   # find run ID
gh run view <run-id> --log-failed           # failed steps only
gh run view <run-id> --log                  # full logs
```

GitHub MCP tools useful during debug:
- `mcp__github__pull_request_read` — PR check status
- `mcp__github__get_commit` — confirm SHA that triggered the run
- `mcp__github__get_file_contents` — verify workflow YAML on branch

---

**Acceptance criteria**

- Stage A: PR CI shows build (×2) + test (×2) pass, push absent.
- Stage B: `workflow_dispatch` shows build → test → push (all succeed,
  push loop is no-op — DAG and permissions confirmed).
- Stage C: fork `main` run shows build → test → push; push job emits
  `latest-amd64`, `latest-arm64`, `latest` (amd64 only) to
  `ghcr.io/eudicy/ansible-toolchain`; cosign verifies cleanly.
- Stage D: upstream PR opens without error; upstream CI passes.

## Success Criteria

- Workflow file has three jobs in the order build, test, push.
- Push job carries the only `packages: write` and `id-token: write`
  permissions and only runs when `github.event_name != 'pull_request'`.
- No image is ever pushed to GHCR without both arch test jobs passing.
- Cosign continues to sign every published tag, using the digest of the
  pushed (and tested) image.
- Unqualified tags (`:latest`, `vX.Y.Z`, `vX.Y`, `vX`) are emitted only
  by the amd64 matrix leg — last-writer race eliminated.
- `RepoDigests` extraction is filtered by `IMAGE_NAME`.
- PR path latency is essentially unchanged (no extra registry round
  trip).
- bd issue `nkb` closed with link to merged PR.
- Follow-up issue filed for multi-arch manifest-list fan-in (see Risks).

## Files Touched

- `.github/workflows/docker-publish.yml` (single file, full rewrite of
  structure but reusing all existing actions/SHAs).

## Risks & Mitigations

- **Last-writer race on unqualified tags.** Both matrix legs (amd64,
  arm64) running in parallel previously pushed to the same unqualified
  tags (`:latest`, semver), making the final image arch-dependent on
  scheduling. Mitigation: arch-gate every unqualified tag to
  `matrix.arch == 'amd64'` so only amd64 publishes them. arm64 still
  publishes its arch-qualified tag (`:latest-arm64`).
- **Known limitation: `:latest` is amd64-only, not a proper multi-arch
  manifest list.** This is deterministic but means arm64 consumers must
  pull `:latest-arm64` explicitly. Per Principle VIII, a follow-up
  issue MUST be filed for `docker buildx imagetools create`-based
  manifest-list fan-in. Logged as `ansible-all-my-things-nkb-followup-manifest`.
- **Concurrent pushes to `main`.** Two rapid commits could trigger
  overlapping workflow runs; without a `concurrency:` block the second
  run could push older tested content over newer. Out of scope for nkb
  (low-frequency project, solo dev). Logged as follow-up. Mitigation if
  it ever fires: cancel the older run manually via `gh run cancel`.
- **Digest mismatch between local tarball and pushed image.** Because
  `docker load` preserves image ID and `docker push` of the same image
  yields the same content digest, this is safe; we still read the
  digest back from `docker inspect ... RepoDigests` (filtered by
  `IMAGE_NAME`) *after* push, which is what GHCR actually serves.
- **`docker tag` step naming.** The build job tags the loaded image
  as `test-image:${{ matrix.arch }}`; the push job re-tags that same
  image to every metadata tag before pushing.
- **Schedule / workflow_dispatch events.** Both are non-PR, so they hit
  the push job. Behaviour matches current intent (cron rebuilds
  `latest`, amd64-only by the new gating rule).
- **Cosign on multi-arch.** Each arch job signs its own per-arch tag.
  amd64 additionally signs the unqualified tags it owns. Manifest-level
  signing is out of scope (linked to the manifest-list follow-up).

---

## RALPLAN-DR Summary

### Principles

1. **GHCR is downstream of test.** Nothing reaches the registry without
   a green test job.
2. **Single artifact, single image.** What is tested is exactly what is
   pushed — no rebuilds, no “equivalent” second build.
3. **Least privilege per job.** Only the `push` job carries
   `packages: write` / `id-token: write`.
4. **Deterministic, race-free tagging.** Unqualified tags are owned by
   exactly one matrix leg (amd64). `docker/metadata-action` runs only
   in the push job, eliminating cross-job determinism questions.
5. **Symmetry between PR and non-PR.** `build` and `test` are identical
   across events; only `push` is gated. This symmetry is also why
   staging-tag promotion (Option D) is rejected — forks cannot push
   staging tags.

### Decision Drivers (top 3)

1. **Correctness of gating** — push must not happen on test failure on
   any event; and concurrent matrix legs must not race on shared tags.
2. **Minimal CI cost / latency** — avoid rebuilding the image twice;
   reuse the tarball artifact already produced by ngu.
3. **Signature integrity** — cosign must sign the digest of the image
   that GHCR actually serves, not a hypothetical rebuild.

### Viable Options

#### Option A — 3-job split with artifact handoff, arch-gated unqualified tags (CHOSEN)

build → test → push, push job downloads the tarball produced by build,
loads, pushes, signs. Unqualified tags (`:latest`, semver) are gated to
the amd64 matrix leg only.

Pros:
- Strictly enforces build → test → push on all events.
- Single image is built, tested, and pushed — no digest drift.
- Push permissions cleanly isolated to one job.
- Reuses the artifact pipeline already shipped by ngu.
- Arch gating eliminates the last-writer race deterministically.

Cons:
- One extra job in the graph (more YAML, one extra runner spin-up per
  arch).
- Tarball upload + download adds ~tens of seconds per arch on non-PR
  runs.
- `:latest` resolves to amd64 only — not a proper multi-arch manifest
  list. Logged as follow-up.

#### Option B — Keep 2 jobs, gate push inside build job on test status

Same two jobs as today, but `build` would split into two stages: first
stage builds & saves, second stage waits for `test` then pushes.

Pros:
- Fewer job definitions.
- No artifact upload on non-PR if the same runner does both stages.

Cons / why **invalidated**:
- GitHub Actions cannot have a job wait on a later job; `needs:` is
  one-directional. Splitting `build` into two jobs collapses to Option
  A. Polling for test job status from within build is fragile, racy,
  and violates the GHA execution model.
- Permissions cannot be reduced for the “build” half; `packages: write`
  would still leak to the build phase.

#### Option C — 3-job split but rebuild image in push job (no artifact reuse)

push job re-runs `docker/build-push-action` with `push: true` after
`test` passes.

Pros:
- No artifact upload/download in push job.
- Uses `docker/build-push-action`’s built-in digest output for cosign.

Cons / why **invalidated**:
- Violates Principle 2: the pushed image is a *different build* than
  the tested image (BuildKit non-determinism, cache misses, base image
  drift between minutes). Defeats the purpose of testing.
- Doubles build cost on non-PR runs.
- GHA cache mitigates but does not eliminate the rebuild risk.

#### Option D — Staging-tag promotion (no artifact)

build job pushes to `:staging-{sha}` in GHCR → test job pulls from the
registry (no artifact upload) → a promote job retags staging to real
tags via `docker buildx imagetools create`, optionally fanning in a
multi-arch manifest list.

Pros:
- No artifact upload cost (~tens of seconds saved per arch on non-PR).
- Registry is single source of truth for the tested digest.
- `imagetools create` can produce a proper multi-arch manifest list,
  fixing the `:latest` arch-gating limitation directly.

Cons / why **invalidated**:
- **Forks cannot push staging tags from PRs.** `GITHUB_TOKEN` on
  fork-originated PRs has no `packages: write` for the upstream
  registry — the PR path would either break entirely or have to fall
  back to the artifact mechanism. That re-introduces the dual-path
  branching this plan exists to eliminate, breaking Principle 5
  (symmetry between PR and non-PR).
- Staging tags pollute the GHCR namespace and require TTL-based
  cleanup (extra workflow or external sweeper).
- `imagetools create` produces a **new manifest digest** that may
  differ from the per-arch digests that were actually tested when
  multiple semver tags point to different underlying objects, weakening
  the “sign exactly what was tested” property cosign relies on.
- Outcome: **rejected on symmetry grounds.** Manifest-list fan-in is
  pursued as a follow-up issue using a different mechanism that does
  not require PR-time registry writes.

### Chosen Option

**Option A — 3-job split with artifact handoff, arch-gated unqualified
tags.** Maximises gating correctness, race safety, and signature
integrity. Modest artifact overhead is acceptable for non-PR runs and
matches the path PRs already take.

### Answers to the four design questions

1. **3-job split vs 2-job with guards** → 3-job split. GHA `needs:` is
   one-way; “gate push on test inside build” is not expressible
   cleanly.
2. **How to pass image to push job** → **Tarball artifact**, same as
   PR path. Rebuild in push job rejected (Option C). Staging tag in
   GHCR rejected (Option D, fork symmetry).
3. **Digest for cosign** → `docker inspect --format='{{range
   .RepoDigests}}{{println .}}{{end}}' <tag> | grep "^${IMAGE_NAME}@"
   | head -1 | cut -d@ -f2` *after* `docker push`. This is the digest
   GHCR returns, filtered to the image we care about so unrelated
   `RepoDigests` cannot leak in.
4. **Tag generation** → `docker/metadata-action` with `tags:` runs only
   in the push job. The build job has a labels-only `metadata-action`
   call (no `tags:` input) and uses a hard-coded local tag
   (`test-image:${{ matrix.arch }}`). No cross-job tag determinism
   question, no `outputs:` plumbing. Unqualified tags are arch-gated
   so amd64 owns `:latest` and semver; arm64 emits only
   `latest-arm64`.

---

## Plan Summary

**Plan saved to:** `.omc/plans/nkb-docker-publish-build-test-push.md`

**Scope:**
- 1 file touched (`.github/workflows/docker-publish.yml`)
- 6 implementation steps
- Estimated complexity: MEDIUM (workflow restructuring, no app code)

**Key Deliverables:**
1. `build` job: always produces per-arch tarball artifact, never pushes,
   labels-only `metadata-action` (no tag computation).
2. `test` job: single artifact-based path for PR and non-PR.
3. `push` job: gated on `test`, loads tarball, pushes with arch-gated
   tags (amd64 owns unqualified tags), signs with cosign.

**Open Questions** (logged to `.omc/plans/open-questions.md`):
- Confirm cosign per-arch signing is acceptable, or whether the
  manifest-list follow-up should be promoted to a blocker.
- Confirm whether `workflow_dispatch` from a fork should be allowed to
  reach the push job (current GHA defaults disallow this; no extra
  guard added).
- Decide whether a `concurrency:` block on `main` is worth adding in a
  separate change (currently logged as out-of-scope follow-up).
