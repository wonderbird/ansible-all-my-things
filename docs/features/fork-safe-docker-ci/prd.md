# PRD: Fork-Safe Docker CI

## Objective

Fix `.github/workflows/docker-publish.yml` so it works correctly for any
GitHub fork: dynamic image name, both architectures tested on PRs without
requiring registry push access.

## Scope

### In scope

- Replace hardcoded `wonderbird/ansible-toolchain` image name with
  `${{ github.repository_owner }}/ansible-toolchain`
- Split build into per-arch matrix jobs (amd64, arm64) running on
  native runners
- On PRs: export each built image as a gzip tarball, upload as artifact,
  download and load in test job — no registry push required
- On non-PR: push per-arch images to ghcr.io; test job pulls from registry
- Both architectures tested natively on every PR (no QEMU emulation)
- Cosign signing unchanged: non-PR only

### Out of scope

- Multi-arch manifest merging (each arch pushes a tagged image; manifest
  list creation is a follow-up)
- Changing the container structure test suite or `.devcontainer/tests.yaml`
- Dependabot / SHA pinning for third-party actions

## User Stories

1. As a fork maintainer, I want PRs to build and test the Docker image
   against my fork's registry namespace, so that CI does not fail due to
   missing push credentials.
2. As a contributor to the upstream repo, I want PRs to test both amd64
   and arm64 images natively, so that architecture-specific defects are
   caught before merge.
3. As the upstream maintainer, I want non-PR pushes to publish images
   to ghcr.io under the actor's namespace, so that each fork publishes
   its own image independently.

## Acceptance Criteria

```gherkin
Scenario: PR from any fork — both archs build and test
  Given a pull_request event targeting main
  When the workflow runs
  Then build jobs run in parallel on ubuntu-24.04 (amd64) and ubuntu-24.04-arm (arm64)
  And each build job saves the image as a gzip tarball and uploads it as an artifact
  And each test job downloads the matching artifact, loads it, and runs container-structure-test
  And no docker push occurs

Scenario: Push to main — images published to correct registry namespace
  Given a push event to main
  When the workflow runs
  Then build jobs push images to ghcr.io/${{ github.repository_owner }}/ansible-toolchain
  And test jobs pull images from that registry path
  And cosign signs the pushed images

Scenario: Fork PR — no credential failure
  Given a pull_request event from a fork where GITHUB_TOKEN is read-only
  When the workflow runs
  Then no step attempts docker push or registry login
  And all steps complete successfully
```

## Implementation Plan

## Implementation Notes

### GHA env block limitation

Workflow-level `env` blocks do not support expressions (`${{ }}`) — only
literal values. `${{ github.repository_owner }}` cannot be set there.

**Fix:** compute the image name in a job step and export via `$GITHUB_ENV`,
then reference `$IMAGE_NAME` in subsequent steps. Alternatively, inline the
expression directly at each usage site.

### Push-before-test gap (known, accepted)

On non-PR pushes, the image is pushed before the test job validates it.
This gap exists in the current workflow and is not introduced by this change.
It is addressed by the follow-up issue `nkb`.

---

### Stage 1: Workflow changes

1. Compute image name in a step: `echo "IMAGE_NAME=ghcr.io/${{ github.repository_owner }}/ansible-toolchain" >> $GITHUB_ENV`
   in each job that needs it; remove hardcoded `wonderbird` from the workflow-level `env` block
2. Add per-arch matrix to `build` job: `ubuntu-24.04` (amd64) and
   `ubuntu-24.04-arm` (arm64); set `runs-on: ${{ matrix.runner }}`
3. Set `platforms: linux/${{ matrix.arch }}` on `build-push-action`
4. Set `load: ${{ github.event_name == 'pull_request' }}` and
   `push: ${{ github.event_name != 'pull_request' }}`
5. Add step after build (PR only): `docker save | gzip > image-${{ matrix.arch }}.tar.gz`
6. Add `actions/upload-artifact@v4` step (PR only) uploading
   `image-${{ matrix.arch }}.tar.gz` with `retention-days: 1`
7. Add matrix to `test` job matching build matrix
8. In `test` job:
   - PR: `actions/download-artifact@v4` then `docker load`
   - Non-PR: `docker pull` from registry
9. Move `cosign-installer` and sign step; guard with
   `github.event_name != 'pull_request'`
10. Update `cache-from/cache-to` to scope by arch:
    `scope=${{ matrix.arch }}`

### Stage 2: Verify

1. Open a test PR; confirm both build and test jobs succeed with no push
2. Confirm artifact size is within GitHub limits (< 2 GB per artifact)
3. Push to main; confirm images published to correct namespace
4. Verify cosign signing succeeds on non-PR push
