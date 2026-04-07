# Project Brief: feat.flutter.role

## Feature

Branch: `004-flutter-role`
Spec: `specs/004-flutter-role/spec.md` (Status: Clarified)

## Goal

Deliver a new Ansible role `flutter` that installs the Flutter SDK on the
`hobbiton` hcloud AMD64 Linux instance, so that a developer can provision
the machine, clone a Flutter GitHub project, and run `flutter build web`
targeting Chrome — without any manual steps.

## Scope

- New role: `roles/flutter/`
- Depends on: `android_studio` role (already implemented, merged to main)
- Chrome/web target only; Android emulator and Linux desktop targets are
  out of scope
- AMD64 only; ARM64 is skipped gracefully via existing tag mechanism

## Acceptance Criteria

1. `flutter doctor` reports no errors for the Chrome/web target on a
   freshly provisioned AMD64 VM
2. `flutter build web` succeeds after cloning a Flutter project — no
   manual steps required
3. Second playbook run reports zero `changed` tasks for the flutter role
4. Playbook run on ARM64 completes without errors; all flutter tasks skip

## Relationship to Broader Vision

The `flutter` role is the second slice of a Flutter development environment:
- Slice 1: `android_studio` role — IDE + Android SDK (done, merged)
- Slice 2: `flutter` role — Flutter SDK + web dependencies (this feature)
- Future: AVD creation, device testing (out of scope for now)
