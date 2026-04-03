# Tech Context

- **Language**: YAML, Ansible 2.19+
- **Collections**: `community.general` (for `community.general.snap` and `community.general.android_sdk`) — already in `requirements.yml`
- **Target OS**: Ubuntu Linux, AMD64 only
- **snapd**: Pre-installed (standard Ubuntu); role does NOT set it up
- **Internet**: Required on first run (snap downloads from Snap Store; cmdline-tools and SDK components also downloaded)
- **Testing**: Manual via `ansible-playbook` on AMD64 Vagrant VM
  (see `specs/003-android-studio-role/quickstart.md`)
- **Lint**: markdownlint must pass on all spec artefacts

## Android SDK automation — technical facts

- **ANDROID_HOME**: `~/Android/Sdk` (per user, not system-wide)
- **SDK must be set up for**: all users in `desktop_user_names` (user decision)
- **Java**: Snap bundles JetBrains Runtime (JBR) at
  `/snap/android-studio/current/android-studio/jbr/bin/java` — covers the Java 17+ requirement for sdkmanager
- **sdkmanager bootstrap**: The snap does NOT expose `sdkmanager` at a known path.
  Standalone cmdline-tools must be downloaded from Google and extracted to
  `~/Android/Sdk/cmdline-tools/latest/` before sdkmanager can be used.
- **cmdline-tools URL**: `https://dl.google.com/android/repository/commandlinetools-linux-{BUILD}_latest.zip`
  The build number changes with every release; there is no static "latest" alias.
  Open design question: make the build number a role variable?
- **"Latest" SDK detection**: `"platforms;android-latest"` is NOT a valid sdkmanager package name.
  The latest API level must be detected by parsing `sdkmanager --list` output at runtime.
- **Ansible module**: `community.general.android_sdk` supports `accept_licenses: true`,
  removing the need for `yes | sdkmanager --licenses`.
- **Minimal SDK component set** (what the Standard setup wizard downloads):
  - `platform-tools`
  - `platforms;android-<latest>`
  - `build-tools;<latest>`
  - `emulator`
  - `sources;android-<latest>` (platform sources)
