# Android Studio

Install Android Studio (Stable) and pre-provision the Android SDK
for all desktop users.

## Requirements

- AMD64 Ubuntu Linux with snapd pre-installed.
- `desktop_user_names` variable defined (list of users to receive the SDK).
- Internet access on the first provisioning run (snap and SDK downloads).
- `community.general` collection (already in `requirements.yml`).
- The `java` role MUST run before this role. It installs the Eclipse Temurin
  JDK via sdkman, which provides the Java 17+ runtime required by sdkmanager.

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `android_cmdlinetools_build` | `14742923` | Build number of the cmdline-tools ZIP. |
| `android_cmdlinetools_sha1` | `48833c34b761c10cb20bcd16582129395d121b27` | SHA-1 checksum of the cmdline-tools ZIP. |

Update both values when Google publishes a new cmdline-tools release.
The current values are listed at the Android Studio download page under
"Command line tools only".

Note: Google publishes SHA-1 (not SHA-256) for cmdline-tools downloads.
See TD-009 in the technical debt register for the accepted risk.

## Dependencies

The `java` role must be applied before this role (provides Temurin JDK via
sdkman for `sdkmanager`). This dependency is documented here only;
`meta/main.yml` keeps `dependencies: []` following project convention.

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
