# Install patterns — exemplar roles

Match your tool to the closest archetype and copy that role's shape. These
roles are the living templates; read the real files rather than a copy that can
drift.

| Archetype | Exemplar role | Fetch/source | Checksum | Idempotence signal |
| --- | --- | --- | --- | --- |
| Binary tarball → single system binary | `opencode` | GitHub release tarball via `get_url` | per-arch sha256 in `defaults`, `get_url checksum:` | `<tool> --version` contains pin |
| Binary tarball → multi-file install + symlinks | `nodejs` | nodejs.org dist tarball | per-arch sha256 | `stat` on installed binary |
| Source build from a git ref (no releases) | `skill_manager` | `git` clone at pinned commit SHA, then `npm ci`/`npm run build` | none (commit SHA is the pin) | `.git_sha` marker file |
| apt repository (GPG-signed) | `github_cli` | `deb822_repository` + keyring, `apt` with `gh=<version>` | apt/GPG (no manual sha) | apt handles it |
| Language pkg manager, per-user | `specify_cli` | `pipx install git+…@<tag>`, loop over `login_user_names` | none | `shell creates:` on the per-user binary |
| git clone of a repo, per-user workspace | `ai_agent_workspace` | `ansible.builtin.git`; depends on the `git` role | none | `git` module idempotence |
| Checksum published upstream in a file | `rtk`, `beads_go`, `beads_viewer` | `get_url` tarball | literal per-arch sha256 pinned in `defaults` (the *update mechanism* refreshes it from upstream `checksums.txt` via `fetch-checksum-from-file.yml` — not fetched at converge time) | version compare |

## Choosing between them

- **Upstream ships a checksummed release artefact** → tarball archetype
  (`opencode`/`nodejs`). Compute the per-arch sha256 locally on first pin; the
  version-update mechanism recomputes on bumps.
- **Upstream publishes a checksums file** covering the exact asset you install →
  `rtk`/`beads_go` (reuse `fetch-checksum-from-file.yml`); avoids a local
  download-and-hash.
- **Upstream ships no artefacts, only source** → `skill_manager` (build on the
  target; pin a commit SHA; marker-based idempotence).
- **Upstream maintains an apt repo** → `github_cli` (GPG-verified; version
  pinned through the apt package spec; no manual checksum).
- **A Python CLI on PyPI/git** → `specify_cli` (pipx, per-user loop).

## Fail-loud validation block (all archetypes)

Assert required vars before use (Principle XII). Shape from `opencode`:

```yaml
- name: Validate required variables
  ansible.builtin.assert:
    that:
      - <role>_version is match('^v[0-9]+\.[0-9]+\.[0-9]+')   # or 40-hex SHA
      - <role>_sha256_amd64 | length == 64                    # if checksummed
    fail_msg: >-
      <role>_version must be a v-prefixed semver tag; the sha256 values must
      each be a 64-character hex digest.
```

## Integrity notes

- `get_url` with `checksum:` gates the download — a tampered/corrupt file fails
  before it is written or extracted. This plus HTTPS is the trust chain when
  upstream does not sign.
- A pinned **commit SHA** is itself the integrity pin for source builds — no
  separate checksum.
- See `docs/architecture/concepts/checksum-verification-pattern.md` for how a
  role consumes a checksum the update mechanism has pinned.
