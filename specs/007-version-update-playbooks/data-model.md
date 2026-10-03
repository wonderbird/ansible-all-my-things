# Data Model: Version Update Playbooks

## Entities

### Tracked Tool

Represents a tool whose version pin is managed by the update playbook. A
tracked tool is declared once, as one entry of
`playbooks/update-versions/vars/tools.yml`; the playbook loops over that
registry rather than carrying per-tool tasks.

Its fields are the registry entry shape documented in the header of
`playbooks/update-versions/vars/tools.yml`.

---

### Version Pin

A key-value entry in a role `defaults/main.yml` file that specifies the exact
version of a tool to install.

| Field | Description |
|-------|-------------|
| `key` | Ansible variable name (maps to an entry of the tool's `pins` list) |
| `current_value` | Value currently in the defaults file |
| `latest_value` | Value fetched from upstream at update time |

---

### Checksum

A hash value paired with a Version Pin, used to verify download integrity.

| Field | Description |
|-------|-------------|
| `key` | Ansible variable name (maps to an entry of the tool's `pins` list) |
| `algorithm` | `sha256` or `sha1` |
| `current_value` | Hash currently in the defaults file |
| `latest_value` | Hash fetched from upstream at update time |

**Invariant**: Checksum and its paired Version Pin MUST always be updated
together.

---

### Upstream Source

The authoritative external location from which the latest version of a tool is
fetched.

| Field | Description |
|-------|-------------|
| `type` | The kind of upstream source, queried by the `fetch-*.yml` files under `playbooks/update-versions/tasks/` |
| `url` | Endpoint or page URL |
| `version_field` | Path to version value in response |
| `checksum_field` | Path to checksum value in response (null if not provided by source) |
| `notes` | Constraints or known fragility (e.g. HTML scraping for Android) |

Which source each tool uses is recorded in its registry entry (`fetch.file`,
`fetch.args`).

---

## State Transitions

### perform-updates.yml

```text
defaults file (current_value)
    ↓ fetch upstream
Upstream Source → latest_value + latest_checksum
    ↓ `tasks/write-pins.yml` (each pin must match exactly one line; then written)
defaults file (every pin of the tool updated)
    ↓ no further action
operator reviews diff and commits manually
```
