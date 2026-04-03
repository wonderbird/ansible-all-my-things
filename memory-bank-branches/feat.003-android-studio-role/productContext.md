# Product Context

Developers add `android_studio` to their playbook and get
Android Studio installed automatically on AMD64 VMs, with the
Android SDK pre-provisioned so the first-launch wizard completes
within 30 seconds. ARM64 Vagrant VMs are skipped without errors.
Re-running the playbook is a true no-op (idempotent).

Full user stories and acceptance scenarios:
`specs/003-android-studio-role/spec.md`.
