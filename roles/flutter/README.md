# Flutter

Install the Flutter SDK (stable channel) from the official `.tar.xz` archive
and configure PATH for all desktop users on AMD64 Ubuntu Linux.

## Requirements

- AMD64 Ubuntu Linux.
- `desktop_user_names` variable defined (list of users to receive the SDK).
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
| `flutter_version` | `3.41.6` | Pinned Flutter stable release to install. |
| `flutter_sha256` | `503b3e6b7d352fca5d21b6474eca95ad544d8fc3b053782eab63a360c7fc7569` | SHA-256 checksum of the Flutter SDK archive for `flutter_version`. |

Update both values together when upgrading Flutter. The current SHA-256 is
listed in the Flutter release manifest at:
<https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json>

## Dependencies

This role has no Ansible meta-level dependencies (`meta/main.yml` keeps
`dependencies: []`). The following roles are **prerequisite dependencies**
that must be applied before this role in the provisioning playbook:

- `java` — provides the Eclipse Temurin JDK via sdkman (required by Android
  SDK tooling invoked through `android_studio`).
- `android_studio` — provides the Android SDK required by Flutter.
- `google_chrome` — provides the Chrome browser required for the web target.

All three roles are listed before `flutter` in `configure-linux-roles.yml`.

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
