# Product Context: feat.flutter.role

## Why This Role Exists

The developer provisions `hobbiton` (hcloud AMD64 instance), makes coffee,
then returns expecting the machine to be ready for Flutter web development.
Without this role, Flutter SDK must be installed manually after provisioning
— blocking work for 10–30 minutes. This role eliminates that gap.

## User Workflow This Enables

```
ansible-playbook configure-linux.yml   # provision + coffee break
git clone <flutter-project>            # back from coffee
flutter build web                      # works immediately
```

## Problems Solved

- Flutter SDK not present after provisioning → role installs it
- SDK dependencies missing → role installs 6 proven apt packages
- Flutter not on PATH → role adds $HOME/flutter/bin via blockinfile
- SDK version drift → flutter_version variable pins the version

## What "Done" Looks Like

- `flutter doctor` output: Chrome/web section shows no errors
- `flutter build web` completes on a freshly cloned project
- No manual steps between `ansible-playbook` and `flutter build web`

## Design Intent

- Separation of concerns: `flutter` role is independent of but ordered
  after `android_studio` in the playbook. The `android_studio` role
  remains useful standalone.
- No scope creep: Chrome/web target only. Android emulator, Linux desktop
  app builds, and AVD creation are explicitly out of scope.
