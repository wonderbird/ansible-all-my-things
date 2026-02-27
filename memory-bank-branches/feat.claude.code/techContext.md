# Tech Context

- **Core technology**: Ansible (min version 2.19)
- **Target OS**: Ubuntu Linux (glibc-based, not musl)
- **Target architectures**: `x86_64`, `aarch64`
- **Source control**: Git with conventional commits (`feat:`, `fix:`, etc.)

## Manifest API

- Base URL: `https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases`
- Pattern: `{base_url}/{version}/manifest.json`
- Returns JSON with `platforms.<key>.checksum` (SHA256 hex string)
- Platform keys: `linux-arm64`, `linux-x64`, `linux-arm64-musl`, `linux-x64-musl`

Example manifest structure (abbreviated):

```json
{"version": "2.1.59", "platforms": {"linux-arm64": {"binary": "claude", "checksum": "78b0ea5a...", "size": 224884646}}}
```

## Binary location

- Installed to `/home/{user}/.local/bin/claude`
- `claude --version` outputs the version string on stdout, e.g. `2.1.59`
- Parse with: `result.stdout | trim`

## Architecture mapping

| `ansible_architecture` | Manifest platform key |
|---|---|
| `x86_64` | `linux-x64` |
| `aarch64` | `linux-arm64` |

## Ansible modules relevant to this feature

- `uri` — fetch manifest JSON
- `stat` with `checksum_algorithm: sha256` — compute binary checksum
- `file` with `state: absent` — delete binary on mismatch
- `fail` — abort playbook with error message
- `shell` / `command` — run `claude --version`
