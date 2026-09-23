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
| `android_cmdlinetools_build` | `14742923` | Build number of the cmdline-tools ZIP. |
| `android_cmdlinetools_sha1` | `48833c34b761c10cb20bcd16582129395d121b27` | SHA-1 checksum of the cmdline-tools ZIP. |

Update both values when Google publishes a new cmdline-tools release.
The current values are listed at the Android Studio download page under
"Command line tools only".

Note: Google publishes SHA-1 (not SHA-256) for cmdline-tools downloads.
See TD-009 in the technical debt register for the accepted risk.

## Dependencies

The `java` role, declared in `meta/main.yml`: `sdkmanager` is invoked with
`JAVA_HOME` pointing into the sdkman JDK that `java` installs, and the
identifier it reads is that role's own default, so this role hard-fails
without it. The desktop play also lists `java`'s play before this one.

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
