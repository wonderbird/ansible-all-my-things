# Java

Install sdkman and the Eclipse Temurin JDK for all desktop users on Ubuntu
Linux (AMD64 and ARM64).

## Requirements

- Ubuntu Linux (AMD64 or ARM64).
- `desktop_user_names` variable defined (list of users to receive sdkman and
  the JDK).
- Internet access on the first provisioning run (sdkman installer and JDK
  download).

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `java_sdkman_identifier` | `21.0.7-tem` | sdkman candidate identifier for the Eclipse Temurin JDK to install (e.g. `21.0.7-tem`). Bump this value to upgrade the JDK; re-running the playbook installs the new version alongside the old one. |

The identifier format is `<version>-<vendor>` as listed by `sdk list java`.
The default selects Eclipse Temurin 21 LTS.

## Dependencies

none

## Example Playbook

```yaml
- hosts: servers
  roles:
    - java
```

## License

MIT

## Author Information

Stefan Boos <kontakt@boos.systems>
