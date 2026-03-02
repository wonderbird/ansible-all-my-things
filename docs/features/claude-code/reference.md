# Reference: Claude Code Binary Integrity Verification

## API endpoints

### GitHub Releases API

- **URL:** `https://api.github.com/repos/anthropics/claude-code/releases/latest`
- **Auth:** None required (public repo); unauthenticated rate limit is 60 requests/hour per IP — not an issue for single-machine playbook runs
- **Relevant field:** `tag_name` (e.g. `"v2.1.62"`)
- **Strip leading `v`:** `result.json.tag_name | regex_replace('^v', '')`

### Anthropic release manifest

- **Base URL:** `https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases`
- **Pattern:** `{base_url}/{version}/manifest.json`
- **Relevant field:** `platforms.<platform-key>.checksum` (SHA256 hex string)

Example manifest structure (abbreviated):

```json
{
  "version": "2.1.59",
  "platforms": {
    "linux-arm64": {
      "binary": "claude",
      "checksum": "78b0ea5a...",
      "size": 224884646
    }
  }
}
```

## Architecture mapping

| `ansible_architecture` | Manifest platform key |
|---|---|
| `x86_64` | `linux-x64` |
| `aarch64` | `linux-arm64` |

musl variants (`linux-x64-musl`, `linux-arm64-musl`) exist in the manifest but are out of scope — see concept.md.

## Binary location

```
/home/<user>/.local/bin/claude
```

Installed for each user in `desktop_user_names`. The path may be a symlink; see implementation decisions below.

## Implementation decisions

### `stat` module: `follow: true`

The `stat` module is called with `follow: true` so that the SHA256 checksum is computed on the
file the symlink points to, not the symlink itself. Without this, the checksum would be wrong
if the installer places the binary behind a symlink.

### `when: not item.stat.exists` guard on checksum comparison

The checksum comparison task is guarded by `not item.stat.exists`. If the installer exits
without creating the binary, `item.stat.checksum` is undefined. Accessing an undefined variable
causes an Ansible template error rather than a clean failure message. The guard lets the
subsequent `fail` task emit a clear "binary is absent" message instead.
