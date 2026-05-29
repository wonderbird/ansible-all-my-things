# Data Model: Version Update Playbooks

## Entities

### Tracked Tool

Represents a tool whose version pin is managed by the update playbooks.

| Field | Description |
|-------|-------------|
| `name` | Human-readable tool name (e.g. "Flutter SDK") |
| `role` | Ansible role that owns the defaults file (e.g. `flutter`) |
| `defaults_file` | Absolute path to the role's `defaults/main.yml` |
| `version_key` | Variable name holding the pinned version (e.g. `flutter_version`) |
| `checksum_key` | Variable name holding the paired checksum, if applicable (e.g. `flutter_sha256`) |
| `checksum_algorithm` | Hash algorithm: `sha256` or `sha1` (null if no checksum) |
| `upstream_source` | Reference to the Upstream Source used to fetch latest version |

**Tracked Tool Inventory** (all tools in scope for first increment):

| Tool | Role | version_key | checksum_key | Algorithm |
|------|------|-------------|--------------|-----------|
| Flutter SDK | `flutter` | `flutter_version` | `flutter_sha256` | sha256 |
| gitmux | `tmux` | `tmux_gitmux_version` | — | — |
| Nerd Fonts (Hack) | `tmux` | `tmux_font_version` | — | — |
| Android cmdline-tools | `android_studio` | `android_cmdlinetools_build` | `android_cmdlinetools_sha1` | sha1 |
| Java (Temurin) | `java` | `java_sdkman_identifier` | — | — |

---

### Version Pin

A key-value entry in a role `defaults/main.yml` file that specifies the exact version of a tool to install.

| Field | Description |
|-------|-------------|
| `key` | Ansible variable name (maps to `version_key` of its Tracked Tool) |
| `current_value` | Value currently in the defaults file |
| `latest_value` | Value fetched from upstream at query/update time |
| `is_current` | Whether `current_value` equals `latest_value` |

---

### Checksum

A hash value paired with a Version Pin, used to verify download integrity.

| Field | Description |
|-------|-------------|
| `key` | Ansible variable name (maps to `checksum_key` of its Tracked Tool) |
| `algorithm` | `sha256` or `sha1` |
| `current_value` | Hash currently in the defaults file |
| `latest_value` | Hash fetched from upstream at update time |

**Invariant**: Checksum and its paired Version Pin MUST always be updated together.

---

### Upstream Source

The authoritative external location from which the latest version of a tool is fetched.

| Field | Description |
|-------|-------------|
| `type` | `json-api`, `github-releases`, `sdkman-api`, or `html-scrape` |
| `url` | Endpoint or page URL |
| `version_field` | Path to version value in response |
| `checksum_field` | Path to checksum value in response (null if not provided by source) |
| `notes` | Constraints or known fragility (e.g. TD-009 for Android) |

**Upstream Source Registry**:

| Tool | Type | URL | Notes |
|------|------|-----|-------|
| Flutter SDK | `json-api` | `https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json` | Version + sha256 both in manifest |
| gitmux | `github-releases` | `https://api.github.com/repos/arl/gitmux/releases/latest` | `tag_name` field |
| Nerd Fonts (Hack) | `github-releases` | `https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest` | `tag_name` field |
| Android cmdline-tools | `html-scrape` | `https://developer.android.com/studio` | Fragile; isolated task file; SHA-1 only (TD-009) |
| Java (Temurin) | `sdkman-api` | `https://api.sdkman.io/2/candidates/java/linuxx64/versions/all` | Filter by major version + `tem` distribution |

---

## State Transitions

### query-versions.yml

```
defaults file (current_value)
    ↓ read
Version Pin (current_value set)
    ↓ fetch upstream
Upstream Source → latest_value
    ↓ compare
is_current = true  → report "up to date"
is_current = false → report "stale: current=X latest=Y", exit non-zero
```

### perform-updates.yml

```
defaults file (current_value)
    ↓ fetch upstream
Upstream Source → latest_value + latest_checksum
    ↓ ansible.builtin.replace
defaults file (updated: version_key=latest_value, checksum_key=latest_checksum)
    ↓ no further action
operator reviews diff and commits manually
```
