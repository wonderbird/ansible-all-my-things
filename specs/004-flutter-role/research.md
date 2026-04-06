# Research: Flutter Ansible Role

**Branch**: `004-flutter-role` | **Date**: 2026-04-04

## Flutter Stable Release

**Decision**: Use Flutter 3.41.6 (latest stable as of 2026-04-04) as the
pinned default in `defaults/main.yml`.

**Rationale**: The spec requires a pinned stable release. The latest stable
at research time is 3.41.6. The `flutter_version` variable allows the
operator to upgrade by bumping the value.

**Alternatives considered**: Using a `latest` sentinel that fetches the
current release at runtime — rejected because it breaks idempotency (the
version would change silently between runs) and contradicts the spec
requirement to pin a specific version.

### Archive details

| Field | Value |
| ----- | ----- |
| Version | `3.41.6` |
| Archive | `flutter_linux_3.41.6-stable.tar.xz` |
| SHA-256 | `503b3e6b7d352fca5d21b6474eca95ad544d8fc3b053782eab63a360c7fc7569` |
| Download URL | `https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.41.6-stable.tar.xz` |
| Source | `https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json` |

The download URL is constructed from the version:

```text
https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_{{ flutter_version }}-stable.tar.xz
```

## Idempotency Strategy

**Decision**: Read the Flutter SDK version from the installed SDK's
`bin/flutter --version` output (or the `version` file at
`flutter/version`), compare to `flutter_version`, and skip
download/extraction when they match.

**Rationale**: The spec requires that if the installed version equals
`flutter_version`, all download and extraction tasks are skipped. The
Flutter SDK ships a `version` file at `<sdk_root>/version` containing
only the version string (e.g. `3.41.6`). This is simpler and more
reliable than parsing `flutter --version` output, which requires a
working Dart toolchain.

**Implementation**: Use `ansible.builtin.stat` to check for
`/home/{{ item }}/flutter/version`, then `ansible.builtin.slurp` to
read its content. Compare the decoded content (stripped) to
`flutter_version`. Use this comparison as a `when:` condition on the
download and extraction tasks.

**Alternatives considered**:

- Running `flutter --version` — rejected because it requires Dart
  runtime to be initialised, which may involve a first-run compilation
  step and is slower.
- Using `creates:` with a static path — rejected because `creates:` only
  tests for file existence, not for the correct version.

## PATH Configuration

**Decision**: Use `ansible.builtin.blockinfile` to add
`export PATH="$HOME/flutter/bin:$PATH"` to each user's `~/.bashrc`,
with a unique marker comment.

**Rationale**: This is exactly the pattern used by the `claude_code`
role (confirmed by inspection of
`roles/claude_code/tasks/main.yml`). It is idempotent by default and
clearly marks the managed block.

**Alternatives considered**: Adding to `/etc/profile.d/` — rejected
because other roles use per-user `~/.bashrc` and consistency across
roles reduces cognitive overhead.

## SDK Extract Directory

**Decision**: Extract to `/home/{{ item }}/flutter` per user.

**Rationale**: Specified in FR-015. Mirrors the `android_studio` role's
per-user `~/Android/Sdk` pattern.

## apt Prerequisites

**Decision**: Install `clang`, `cmake`, `ninja-build`, `pkg-config`,
`libgtk-3-dev`, `mesa-utils` using `ansible.builtin.apt` before the
SDK extraction.

**Rationale**: These are the exact packages specified in FR-017, based
on the user's confirmed manual installation experience. They are the
Flutter Linux desktop and Chrome/web build dependencies documented in
the Flutter manual installation guide.

**Post-install**: Run `ansible.builtin.systemd` with
`daemon_reload: true` after package installation (FR-018).

## `meta/main.yml` Dependencies

**Decision**: Keep `dependencies: []` in `meta/main.yml`. Document
`android_studio` as a prerequisite in `README.md` only.

**Rationale**: FR-020 and the clarification from the user (Q5 in the
spec). Meta-level dependencies are invisible to playbook readers, break
tag filtering, and are designed for redistributed Galaxy roles — not
private single-playbook provisioners.

## Tag Placement

**Decision**: Apply `not-supported-on-vagrant-arm64` at the role entry
level in `configure-linux-roles.yml`, not on individual tasks.

**Rationale**: FR-007 and the `android_studio` role pattern. The role
entry in `configure-linux-roles.yml` includes the comment from FR-008
about `apply: tags:` when using `include_role`.

## Download Integrity

**Decision**: Pass `checksum: "sha256:{{ flutter_sha256 }}"` to
`ansible.builtin.get_url`.

**Rationale**: FR-019. SHA-256 is available from the Flutter release
manifest (unlike the Android cmdline-tools which only publish SHA-1).
This mirrors the `android_studio` checksum pattern structurally.

## Android SDK Components: NDK, CMake, and Latest SDK Platform

**Decision**: Do **not** install NDK (Side by Side), Android SDK CMake, or
any additional `platforms;android-N` package beyond what the
`android_studio` role already provisions.

**Context**: A question arose (2026-04-06) about whether three Android SDK
components visible in Android Studio under *Languages & Frameworks > Android
SDK* were required for the declared use case:

- *SDK Platforms* — Android latest stable, API Level latest stable
- *SDK Tools* — NDK (Side by Side)
- *SDK Tools* — CMake (from the Android SDK, not the system apt package)

**Rationale**:

- **Target platform is Chrome/web only.** `flutter build web` compiles Dart
  to JavaScript/WebAssembly via `dart2js`/`dart2wasm`. No native Android
  toolchain is invoked at any point in this pipeline.
- **`flutter doctor` Chrome check is independent of the Android SDK.** The
  `[✓] Chrome` check verifies only that a `google-chrome` binary is
  executable. NDK, CMake, and SDK Platform entries are invisible to it.
- **`platforms;android-N` already covered.** The `android_studio` role
  dynamically detects and installs the latest stable API level via
  `sdkmanager --list --channel=0`. Installing the same package again via the
  `flutter` role would be redundant.
- **NDK and Android SDK CMake do not affect `flutter doctor` output.** The
  Android toolchain check in `flutter doctor` validates `platform-tools`,
  `build-tools`, `platforms`, `cmdline-tools/latest`, and a JDK — none of
  which include NDK or Android SDK CMake. All those items are already
  satisfied by the `android_studio` role.
- **Both components are inert for this use case.** NDK lives under
  `$ANDROID_HOME/ndk/<version>/` and is invoked only for native JNI code.
  Android SDK CMake lives under `$ANDROID_HOME/cmake/<version>/bin/cmake`
  and is invoked only by Android Gradle builds. Neither shadows system
  binaries nor interacts with system `cmake` or `clang`.

**Alternatives considered**: Installing NDK and Android SDK CMake — rejected
for three reasons:

1. **No requirement, no gain**: they provide no benefit for the Chrome/web
   target; the existing provisioning already produces a clean `flutter doctor`
   output without them.
2. **Provisioning cost**: each component adds download and installation time
   (NDK alone is ~500 MB–1 GB), slowing every VM provision and re-provision.
3. **Maintenance overhead**: each additional SDK component requires version
   tracking, checksum updates, and its own troubleshooting surface — all cost
   without corresponding value for this use case.

## No `contracts/` Directory Needed

**Decision**: Skip the `contracts/` directory.

**Rationale**: This role exposes no external API, network endpoint, or
machine-readable interface contract. Its only interface is the Ansible
variable contract (`flutter_version`, `flutter_sha256`,
`desktop_user_names`) documented in `README.md` and `data-model.md`.
