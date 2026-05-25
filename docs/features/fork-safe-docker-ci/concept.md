# Concept: Fork-Safe Docker CI

## Feature Name

Fork-compatible Docker image build, test, and publish pipeline.

## Description

Build job runs as a per-arch matrix (amd64, arm64) on native runners. On
PRs, each build job exports the image as a gzip tarball artifact; the test
job downloads and loads it — no registry push needed. On non-PR events,
images push to `ghcr.io/${{ github.repository_owner }}/ansible-toolchain`
and test jobs pull from there. No per-fork configuration required.

## User Value

Fork users currently get CI failures: push steps fail (read-only token) and
test steps validate the wrong image (upstream `:latest`). This fix makes CI
green on every fork PR and tests the actual built image on both architectures.

## Design Rationale

### Tarball artifact pattern instead of PR registry push

GitHub Actions `GITHUB_TOKEN` on fork PRs has read-only scope — registry
push is blocked. Alternatives considered:

- **`pull_request_target`**: grants write token but executes fork code in a
  privileged context — rejected as a security risk.
- **Separate deploy key / PAT**: requires per-fork secret setup — rejected,
  too much operator burden.
- **QEMU multi-arch on single runner**: avoids the split, but `load: true`
  is incompatible with multi-platform builds in `docker/build-push-action`.
  Also, emulated arm64 is slow and can mask architecture-specific bugs.

Tarball artifact: build job saves `docker save | gzip`, uploads via
`actions/upload-artifact`; test job downloads and `docker load`. Artifacts
are ephemeral (1-day retention) and sized within GitHub's 2 GB limit for
typical toolchain images.

### Per-arch matrix build jobs on native runners

`load: true` only works for a single platform. Splitting into two matrix
jobs (one per arch, each on its native runner) lets both architectures build
natively and be tested in the same workflow without QEMU.

### Dynamic image name from `github.repository_owner`

Hardcoding `wonderbird` as the registry namespace means every fork publishes
to `ghcr.io/wonderbird/...` — which fails without the upstream owner's
credentials. Using `${{ github.repository_owner }}` scopes the image to the
acting user's namespace automatically with zero configuration.

### GHA cache scoped per arch

`cache-from/cache-to` keys are scoped with `scope=${{ matrix.arch }}` to
prevent cross-contamination between amd64 and arm64 layer caches.

## Out of Scope

- **Multi-arch manifest list**: each arch pushes a separate tagged image.
  Creating a combined manifest (e.g. via `docker buildx imagetools create`)
  is a follow-up task.
- **arm64 signing**: cosign signing is guarded to non-PR only; per-arch
  signing granularity is not changed.
- **SHA pinning for third-party actions**: `checkout@v6`, `setup-buildx`,
  etc. remain at floating major tags consistent with the rest of the repo.
