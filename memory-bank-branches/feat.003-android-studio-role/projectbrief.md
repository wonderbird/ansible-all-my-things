# Project Brief: feat.003-android-studio-role

**Goal**: Ansible role that installs Android Studio via snap and
pre-provisions the Android SDK so the first-launch wizard completes
within 30 seconds.

**Spec artifacts**: `specs/003-android-studio-role/`
(`spec.md`, `plan.md`, `research.md`, `tasks.md`, `quickstart.md`)

**Key constraints** (details in plan.md):

- AMD64 Ubuntu only; ARM64 skipped via tag
- `community.general.snap` for install;
  `community.general.android_sdk` for SDK components
- Three-file role: `defaults/`, `meta/`, `tasks/`
- SPDX header on all YAML; no task-level `become: true`
- All test commands scoped to `--limit hobbiton`
