# Version-update wiring

Constitution Principle II: a role that pins a tool version in `defaults/main.yml`
MUST register with the version-update mechanism, or the pin silently drifts
behind upstream. All four touchpoints are required. Mechanism overview:
`docs/architecture/version-update-playbooks.md`.

## Touchpoint 1 — fetch task (reuse before writing)

Reuse a parametrized task under `playbooks/update-versions/tasks/` if the
upstream source type already exists. Only write a new one for a genuinely new
source type.

| Upstream source | Reuse this task | Inputs → fact |
| --- | --- | --- |
| GitHub tagged release | `fetch-github-release.yml` | `github_repo` → `fetched_github_tag` |
| Checksum from a release file | `fetch-checksum-from-file.yml` | `checksum_file_url`, `checksum_target_filename` → `fetched_checksum` |
| GitHub branch HEAD commit (no releases) | `fetch-github-commit-sha.yml` | `github_repo`, `git_ref` → `fetched_github_sha` |
| Structured JSON / SDKMAN / HTML | `fetch-flutter-version.yml` / `fetch-java-version.yml` / `fetch-android-version.yml` | see each file |

A new fetch task must fail loud (Principle XII): explicit failures on API
rate-limit, unexpected status, and missing field. Mirror
`fetch-github-commit-sha.yml`.

## Touchpoint 2 — `query-versions.yml` (detect drift)

Add, in the existing groups:

1. Slurp the role defaults.
2. Extract the current pin into a `current_<role>_version` fact in the
   `set_fact` block.
3. Include the fetch task + save the fetched fact.
4. Add a `debug` report line (`current=… upstream=… status=…`).
5. Add the comparison to the aggregate `Fail if any version pins are stale`
   `when:` condition.

Slurp + extract shape:

```yaml
- name: Read <role> role defaults
  ansible.builtin.slurp:
    src: "{{ _roles_dir }}/<role>/defaults/main.yml"
  register: _<role>_defaults_raw

# ...in the set_fact block:
current_<role>_version: >-
  {{ _<role>_defaults_raw.content | b64decode
     | regex_search('<role>_version:\s*"([^"]+)"', '\1')
     | default([], true) | first }}
```

## Touchpoint 3 — `perform-updates.yml` (apply)

1. Include the same fetch task + save the fetched fact (fetch section).
2. `replace` the pin in defaults (apply section).
3. If checksummed: re-download the artefact and `stat` with
   `checksum_algorithm: sha256`, then `replace` each sha — version and checksums
   are always updated together (see the `opencode` block).

Pin `replace` shape:

```yaml
- name: Update <role>_version in <role> role defaults
  ansible.builtin.replace:
    path: "{{ _roles_dir }}/<role>/defaults/main.yml"
    regexp: '<role>_version:\s*"[^"]+"'
    replace: '<role>_version: "{{ fetched_<role>_value }}"'
```

## Touchpoint 4 — the doc

Update `docs/architecture/version-update-playbooks.md` in three places:

- the upstream source-type sentence,
- the `tasks/` tree (only if you added a new fetch task),
- the Tracked-tools table row.

## Verify the wiring

```bash
cd playbooks/update-versions
ansible-playbook query-versions.yml        # reports UP TO DATE / STALE per tool
```

A freshly pinned tool should report `UP TO DATE` immediately after pinning.
