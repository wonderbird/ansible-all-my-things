# Version-update wiring

Constitution Principle II: a role that pins a tool version in `defaults/main.yml`
MUST register with the version-update mechanism, or the pin silently drifts
behind upstream. Mechanism overview and the rules that govern it:
`docs/architecture/version-update-playbooks.md`.

Registering a tool is one registry entry, plus a fetch task file when no
existing one already queries that kind of source. Neither playbook is edited
per tool: both loop over the registry.

## Touchpoint 1 — the registry entry

Add the tool to `playbooks/update-versions/vars/tools.yml`:

```yaml
  <tool>:
    role: <role>                     # roles/<role>/defaults/main.yml
    fetch:
      file: fetch-github-release.yml # a task file under tasks/
      args:
        github_repo: owner/project
        required_asset_regexes: ['^tool-linux-amd64\.tar\.gz$']
      results:                       # every output this tool consumes, named
        version: "{{ fetched_github_tag }}"
    current_pin: <tool>_version      # the pin drift is measured against
    checksums:                       # omit when the role pins no digest
      - key: amd64
        kind: checksum_file          # checksum_file | download
        url: "https://example.invalid/{{ _fetched.version }}/checksums.txt"
        filename: "tool-linux-amd64.tar.gz"
    pins:
      - {pin: <tool>_version, value: "{{ _fetched.version }}"}
      - {pin: <tool>_sha256_amd64, value: "{{ _checksums.amd64 }}"}
```

Rules the pre-flight validation enforces, so a mistake fails at play start
rather than mid-run:

- every pin value is exactly one reference to this tool's own `_fetched.<name>`
  or `_checksums.<key>`, both of which are bound per tool, so a value can never
  come from the tool that ran before;
- `current_pin` is one of the tool's own pins;
- a per-architecture pin is written from a key carrying the same architecture;
- a GitHub release fetch declares `required_asset_regexes`, or states in
  `release_carries_no_consumed_asset` why the tool installs from elsewhere;
- pin names are unique across the whole registry;
- every role carrying a version or checksum pin has an entry at all.

Two digest sources exist, and the choice is not free: `checksum_file` reads a
digest upstream publishes, `download` fetches the artefact and hashes it
locally. Prefer `checksum_file` where upstream publishes one covering the exact
artefact. Where a project publishes both a combined checksums file and a
per-archive `<filename>.sha256` sidecar, wire the sidecar: a combined file has
been renamed across releases in at least one tracked project, and one spelling
carried hashes that did not match the archives.

## Touchpoint 2 — a fetch task, only for a new kind of source

Reuse a parametrized task under `playbooks/update-versions/tasks/` if the
upstream source type already exists. Write a new one only for a genuinely new
source type.

| Upstream source | Reuse this task | Arguments → results |
| --- | --- | --- |
| GitHub tagged release | `fetch-github-release.yml` | `github_repo`, plus `required_asset_regexes` or `release_carries_no_consumed_asset` → `fetched_github_tag` |
| Digest from a published checksums file | `fetch-checksum-from-file.yml` | wired by `kind: checksum_file`, not called directly |
| GitHub branch HEAD commit (no releases) | `fetch-github-commit-sha.yml` | `github_repo`, `git_ref` → `fetched_github_sha` |
| Structured JSON / SDKMAN / HTML | `fetch-flutter-version.yml` / `fetch-java-version.yml` / `fetch-android-version.yml` | see each file |

A new fetch task must fail loud (Principle XII): explicit failures on API
rate-limit, unexpected status and missing field. Mirror
`fetch-github-commit-sha.yml`. Name its outputs in the registry entry's
`fetch.results`, and add any new argument name to the argument list in
`tasks/fetch-tool.yml`, which must be a literal mapping.

**Every task that can fail because of a third party declares
`failure_source: upstream` in its own `vars:`.** An input assert declares
nothing: a bad argument is this repository's fault, and anything unclassified
is treated as ours and stops the run. `uri` and `get_url` tasks need no
declaration; a network module failing is recognised as third-party already.

## Touchpoint 3 — documentation

Update `docs/architecture/version-update-playbooks.md` where it lists source
types and tracked tools.

## Checking the wiring

```bash
ANSIBLE_CONFIG=playbooks/update-versions/tests/ansible.cfg \
  ansible-playbook playbooks/update-versions/tests/test-tool-registry.yml
./scripts/ci-local.sh
```

The first validates the registry, including the new entry. The second runs
every gate a commit must pass, including a network-free run of the real task
files over a fixture registry.
