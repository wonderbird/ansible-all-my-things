<!-- SPDX-License-Identifier: MIT-0 -->
# binary_version_gate

Ansible role that tells whether an installed binary reports exactly its pinned
version. Roles that install a pinned release binary call it before their
download block and install only when the answer is no.

Gating the install on the reported version rather than on the file existing
makes a pin bump reach a host that already has an older version. A gate on
file presence alone would never upgrade that host; only fresh hosts would get
the new pin.

The role changes nothing on the host. It runs `<binary> --version` and sets a
fact.

## Requirements

- Ansible 2.19+

## Role Variables

All three are required and have no defaults.

| Variable | Meaning | Example |
| --- | --- | --- |
| `binary_version_gate_path` | Absolute path of the installed binary | `/usr/local/bin/rtk` |
| `binary_version_gate_output_prefix` | Text that `--version` prints before the version number, empty when the version comes first | `"rtk "`, `"bv v"`, `""` |
| `binary_version_gate_pin` | Pinned version, `MAJOR.MINOR.PATCH` with an optional leading `v` | `v1.0.1`, `0.13.5` |

The prefix is literal text, not a regular expression. The leading `v` of the
pin is dropped before the comparison, so a `v`-prefixed release tag can be
passed as is. When the tool itself prints a `v`, put it in the prefix.

## Result

The host fact `binary_version_gate_current` is `true` when the binary exists
and its `--version` output starts with the prefix followed by exactly the pin,
then a space or the end of the output. Otherwise it is `false`.

The version is compared as a whole token, so pin `1.2.3` does not match an
installed `1.2.30`.

Every call overwrites the fact. Read it right after the call, or copy it into a
fact of your own when another call comes in between.

## Failure Modes

The role stops the play (Constitution Principle XII) when:

- a variable is missing, the path is not absolute, the prefix is not a string,
  or the pin is not `MAJOR.MINOR.PATCH` with an optional leading `v`. Pre-release
  pins such as `v1.4.0-rc1` are rejected;
- the binary exists but its `--version` output does not start with the prefix
  followed by `MAJOR.MINOR.PATCH`. Treating that as "not installed" would
  reinstall on every run without saying why. The message names the output and
  says to remove the binary to let the calling role reinstall it.

## Dependencies

None.

Calling roles use `include_role` and do not list this role in their
`meta/main.yml` `dependencies:`. A dependency entry would run the role once
without its required variables, and the role provisions no artefact that
would call for one.

## Example

```yaml
- name: Check whether the installed rtk reports the pinned version
  ansible.builtin.include_role:
    name: binary_version_gate
  vars:
    binary_version_gate_path: /usr/local/bin/rtk
    binary_version_gate_output_prefix: "rtk "
    binary_version_gate_pin: "{{ rtk_version }}"

- name: Install rtk
  when: not binary_version_gate_current | bool
  block:
    - name: Download and install the pinned release
      ansible.builtin.debug:
        msg: get_url and unarchive go here
```

## Testing

The Molecule scenario plants fake binaries that print fixed `--version`
output. It checks the answer for a matching, older, longer and absent binary,
and checks that every failure mode above stops the gate with its message.

## License

MIT-0
