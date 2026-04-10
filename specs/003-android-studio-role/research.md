# Research: Android Studio Ansible Role

**Feature**: `003-android-studio-role`
**Date**: 2026-03-31

## Decision 1 — Snap module vs. command module

**Decision**: Use `community.general.snap` with `state: present`.

**Rationale**: Official collection modules are preferred over raw
`ansible.builtin.command` for maintainability and faster upstream fixes.
`community.general.snap` expresses intent declaratively and handles
idempotency natively — it reports `changed` on first install and `ok` on
subsequent runs without a manual guard:

```yaml
- name: Install Android Studio via snap
  community.general.snap:
    name: android-studio
    classic: true
    state: present
```

`community.general` must be added to `requirements.yml` to satisfy this
dependency.

**Alternatives considered**:

- `ansible.builtin.command` with a `creates:` guard — rejected; custom guards
  are harder to maintain than a purpose-built module, and any bugs must be
  fixed in-repo rather than relying on upstream fixes.

## Decision 2 — Role file layout

**Decision**: Two-file layout matching `google_chrome`: `meta/main.yml` and
`tasks/main.yml` only. No `defaults/`, `vars/`, `handlers/`, or `templates/`
directories.

**Rationale**: The role has no configurable variables (snap package name is
fixed), no service restarts (snap handles its own daemon), no templates, and
no files to distribute. Adding empty directories is noise.

**Alternatives considered**: Full scaffold with all directories — rejected;
Constitution §IV prohibits speculative structure.

## Decision 3 — Idempotency

**Decision**: Rely on `community.general.snap` native idempotency; no manual
guard path needed.

**Rationale**: The module checks snap state before acting and reports `ok`
when the snap is already installed. A `creates:` guard is unnecessary and
would duplicate logic the module already encapsulates.

**Alternatives considered**:

- `creates: /snap/android-studio/current` — valid guard path for
  `ansible.builtin.command`, but not applicable now that the snap module is
  used (see Decision 1).

## Decision 4 — SDK automation approach

**Decision**: Use a combination of `ansible.builtin.get_url` (download
cmdline-tools), `ansible.builtin.unarchive` (extract), and
`community.general.android_sdk` (install SDK components + accept
licenses) per user in `desktop_user_names`.

**Verified** (2026-04-03): `community.general.android_sdk` confirmed
present via `ansible-doc community.general.android_sdk`. Module wraps
`sdkmanager`, supports `accept_licenses: true`, `sdk_root`, `state:
latest`, and `check_mode`. Requires `sdkmanager` and Java 17+ on the
managed node (`sdkmanager` comes from cmdline-tools bootstrap; Java 17+
comes from the Temurin JDK installed by the `java` role via sdkman).
`JAVA_HOME` is set to the versioned sdkman path
(`/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}`)
rather than the snap-bundled JBR — the versioned path is stable against
user `sdk default java` changes and does not depend on the snap being
present at runtime.

**Key constraint**: Package names require explicit versions (e.g.,
`platforms;android-35`). There is no symbolic `latest` token. The
latest API level must be detected at runtime by parsing
`sdkmanager --list` output.

**Rationale**: `community.general.android_sdk` handles license
acceptance (`accept_licenses: true`) and SDK component installation
declaratively. cmdline-tools must be bootstrapped first because the
snap does not expose `sdkmanager` at a known path.

**Alternatives considered**:

- Pure shell (`command`/`shell`) with `sdkmanager` — rejected; requires
  manual idempotency guards and license piping.

## Decision 5 — cmdline-tools build number

**Decision**: Expose the build number and SHA-256 checksum as role
variables `android_cmdlinetools_build` and
`android_cmdlinetools_sha256` in `defaults/main.yml`. The URL is
constructed as
`https://dl.google.com/android/repository/commandlinetools-linux-{build}_latest.zip`.
The download task validates the checksum via
`checksum: "sha256:{{ android_cmdlinetools_sha256 }}"`.

**Rationale**: There is no stable "latest" URL from Google. Role
variables are the simplest approach (§IV); values are bumped manually
when a new version is needed. Both the build number and SHA-256
checksum are listed at
<https://developer.android.com/studio/index.html#command-line-tools-only>.

**Alternatives considered**:

- Dynamic resolution from Google's repository XML — rejected; fragile,
  depends on undocumented endpoint, violates §IV Simplicity.

## Decision 6 — Per-user SDK provisioning

**Decision**: Loop over `desktop_user_names` using `loop:` at the task
level. Each SDK task runs as `become_user: "{{ item }}"` to ensure
files are owned by the correct user under `~/Android/Sdk`.

**Rationale**: ANDROID_HOME is per-user (`~/Android/Sdk`), not
system-wide. Each user needs their own SDK copy.
