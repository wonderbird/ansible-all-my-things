# Flutter

Install the Flutter SDK (stable channel) from the official `.tar.xz` archive
and configure PATH for all desktop users on AMD64 Ubuntu Linux.

## Requirements

- AMD64 Ubuntu Linux.
- Internet access on the first provisioning run (SDK download).
- The `java` role must have run before this role. It installs the Eclipse
  Temurin JDK via sdkman, required by the Android SDK tooling.
- The `android_studio` role must have run before this role. The Flutter
  toolchain requires the Android SDK to be present for the Android target.
  Even for Chrome/web builds, `flutter doctor` checks for the Android SDK.
- The `google_chrome` role must have run before this role. Chrome must be
  present on the machine for the Chrome/web target in `flutter doctor` to
  pass.

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to install the Flutter SDK for. Must contain at least one name; the role fails loudly if it is undefined or empty. |
| `flutter_version` | `3.41.6` | Pinned Flutter stable release to install. |
| `flutter_sha256` | `503b3e6b7d352fca5d21b6474eca95ad544d8fc3b053782eab63a360c7fc7569` | SHA-256 checksum of the Flutter SDK archive for `flutter_version`. |

Update both values together when upgrading Flutter. The current SHA-256 is
listed in the Flutter release manifest at:
<https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json>

## Dependencies

This role has no apply-time dependencies: no task in it consumes an artefact
another role provisions, and `meta/main.yml` keeps `dependencies: []`
accordingly. It installs the Flutter SDK on any host on its own.

A *working* Flutter installation needs three more roles, at use time rather
than at apply time:

- `java` — the Eclipse Temurin JDK via sdkman, which the Android SDK tooling
  needs.
- `android_studio` — the Android SDK that `flutter doctor` and the Android
  build targets look for.
- `google_chrome` — the browser the web target runs in.

`configure-profile-roles.yml` therefore orders `flutter` after
`android_studio` and `google_chrome` in the desktop play, and `java` runs in
the base play before either.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - java
    - android_studio
    - google_chrome
    - flutter
```

## License

MIT

## Author Information

Stefan Boos <kontakt@boos.systems>
