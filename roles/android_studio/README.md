# Android Studio

Install Android Studio (Stable) and pre-provision the Android SDK
for all desktop users.

## Requirements

- AMD64 Ubuntu Linux with snapd pre-installed.
- Internet access on the first provisioning run (snap and SDK downloads).
- `community.general` collection (already in `requirements.yml`).
- The `java` role applied first — see Dependencies below.

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to install Android Studio and the SDK for. Must contain at least one name; the role fails loudly if it is undefined or empty. |
| `android_cmdlinetools_build` | see `defaults/main.yml` | Build number of the cmdline-tools ZIP. |
| `android_cmdlinetools_sha1` | see `defaults/main.yml` | SHA-1 checksum of the cmdline-tools ZIP. |

`defaults/main.yml` carries both pins together with the upstream page they
are read from. Both must move together, and the version-update playbooks
refresh them from that page — see
[version-update-playbooks.md](../../docs/architecture/version-update-playbooks.md).

Note: Google publishes SHA-1 (not SHA-256) for cmdline-tools downloads.
See TD-009 in the technical debt register for the accepted risk.

## Dependencies

The `java` role, declared in `meta/main.yml`: `sdkmanager` is invoked with
`JAVA_HOME` pointing into the sdkman JDK that `java` installs, and the
identifier it reads is that role's own default, so this role hard-fails
without it. `java` runs in the base play of `configure-profile-roles.yml`,
and because this role declares it, Ansible resolves it again inside the
desktop play and re-runs its tasks there.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - android_studio
```

## License

MIT

## Author Information

Stefan Boos <kontakt@boos.systems>
