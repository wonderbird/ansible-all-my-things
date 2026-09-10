<!-- SPDX-License-Identifier: MIT-0 -->
# obsidian — Design

Non-obvious decisions for the `obsidian` role.

## Installation Method

Obsidian publishes a `.deb` directly on each GitHub release (no apt
repository, unlike `github_cli` or `google_chrome`). The role downloads that
`.deb`, verifies it against a locally pinned SHA-256, and installs it with
`ansible.builtin.apt: deb=...`, which resolves the package's dependency tree
from the standard Ubuntu archive. Flatpak and AppImage were considered and
rejected: Flatpak would add a package manager not otherwise used in this
project (Principle IV — YAGNI); AppImage requires manual `.desktop`/icon
integration for a real desktop install, which is more work than one `apt`
step for no additional benefit.

## Architecture Support

Obsidian's upstream releases (`obsidianmd/obsidian-releases`) publish an
amd64 `.deb` only — arm64 builds exist only as an AppImage/tarball, not a
`.deb`. The role therefore asserts `ansible_facts['architecture'] ==
'x86_64'` with an actionable failure message, and its entry in
`configure-profile-roles.yml` carries `tags: not-supported-on-arm64` (the
same pattern `google_chrome` uses for the same reason).

The role's Molecule scenario pins `FROM --platform=linux/amd64` in its
`Dockerfile` so the scenario exercises the real amd64 install path
regardless of the host's native architecture (this repo's local Molecule
hosts are ARM64 — see `README.md`). This relies on `podman build`/buildah's
native `FROM --platform` support and, on an ARM64 host, on
`qemu-user-static`/`binfmt` being registered; if it is not, `podman create`
fails loudly rather than silently running the wrong architecture. A
`platform:` key on the `molecule.yml` platforms entry was tried first and
rejected: the podman driver (`molecule-plugins`) does not thread that key
into either its build or run task, so it is silently ignored — the
Dockerfile-level pin is the only mechanism that actually works.

## Version Pinning and the URL/Filename Asymmetry

`obsidian_version` stores the GitHub release tag in `v`-prefixed form (e.g.
`v1.12.7`), matching every other GitHub-Releases-backed tool in this project.
Obsidian's release **tag** keeps the `v` prefix, but the **asset filename**
does not: the download URL is
`.../releases/download/v1.12.7/obsidian_1.12.7_amd64.deb` — `v` in the path
segment, stripped in the filename. Both the role's `tasks/main.yml` and
`playbooks/update-versions/perform-updates.yml` apply
`obsidian_version | regex_replace('^v', '')` specifically when building the
filename, not the URL path.

## Idempotency

The role gates its download and install behind a `_obsidian_needs_install`
fact, computed from `ansible.builtin.package_facts` (`manager: apt`) rather
than the `stat` + `<binary> --version` pattern used by `dolt_sql_server` and
`opencode`: Obsidian is an apt-managed package (not a bare binary), so
`package_facts` gives a direct, structured version comparison. As with
those two roles, the downloaded `.deb` in `/tmp` is never deleted — leaving
it there is what makes the `get_url` task's `checksum:` comparison report
`ok` instead of re-downloading on every run. An earlier draft modeled the
task flow on `cursor_ide` (download, install, then delete the `.deb`), which
was rejected during planning: deleting the artefact forces a re-download on
every subsequent run, which reports `changed` on Molecule's `idempotence`
phase and fails it.

## One Repository, Two Release Lines

`obsidianmd/obsidian-releases` publishes the Android and the desktop release
lines from a single repository and a single tag namespace. Its GitHub "latest
release" is therefore regularly an Android tag whose asset list holds an
`.apk` and no `.deb` at all. The two lines interleave continuously, so this is
a recurring condition rather than a one-off.

Anything that resolves "the newest release" without also requiring the asset
it needs will eventually pin a tag whose amd64 `.deb` does not exist, and the
download 404s. The vendor's `desktop-releases.json` feed on the `master`
branch tracks the desktop line alone and is the source this project uses
instead.

If that feed is ever moved or renamed, the recovery path is to page
`GET /releases?per_page=N` on the same repository and select the newest
release that carries an `obsidian_*_amd64.deb`. That was the alternative
considered when the feed was adopted. It costs no extra API request, since it
replaces the `releases/latest` call rather than adding to it, and its
selection rule is better defined than a file on a vendor branch. It was not
chosen because "newest" is ambiguous when two release lines interleave —
`published_at` order and list order can disagree.

## Version-Update Integration

The role registers with the project-wide version-update mechanism through a
dedicated `fetch-obsidian-version.yml` task rather than the shared
`fetch-github-release.yml`, for the reason above. Why that task derives the
tag the way it does is documented in its own header comment, which is what
someone editing it will have in front of them.

- `query-versions.yml` reads the pinned tag from `defaults/main.yml`,
  fetches the desktop feed's tag, and reports STALE if the two differ.
- `perform-updates.yml` downloads the amd64 `.deb` and computes its SHA-256
  **before** writing either pin, so an upstream failure cannot leave a new
  version paired with the previous version's checksum. That ordering is
  enforced by
  [`scripts/version-update-order/`](../../scripts/version-update-order/README.md).
