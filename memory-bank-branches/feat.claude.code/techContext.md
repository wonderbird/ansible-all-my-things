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

## Version discovery

- GitHub Releases API: `https://api.github.com/repos/anthropics/claude-code/releases/latest`
- No authentication required (public repo); unauthenticated rate limit is 60 req/hour per IP (non-issue for single-machine playbook runs)
- Returns JSON; relevant field: `tag_name` (e.g. `"v2.1.62"`)
- Strip leading `v` with: `result.json.tag_name | regex_replace('^v', '')`
- Running `claude --version` is intentionally avoided — the binary must not be executed before its integrity is confirmed

## Binary location

- Installed to `/home/{user}/.local/bin/claude`

## Architecture mapping

| `ansible_architecture` | Manifest platform key |
|---|---|
| `x86_64` | `linux-x64` |
| `aarch64` | `linux-arm64` |

## Ansible modules relevant to this feature

- `assert` — verify supported processor architecture before any network requests
- `uri` — fetch GitHub Releases API response and manifest JSON
- `stat` with `checksum_algorithm: sha256` and `follow: true` — compute binary checksum
- `file` with `state: absent` — delete binary on mismatch
- `fail` — abort playbook with error message
