# Project Brief: Java Role (sdkman + Temurin JDK)

**Feature Branch**: `005-java-role`
**Spec**: `specs/005-java-role/spec.md`
**Created**: 2026-04-07

## Goal

Implement an Ansible role (`roles/java/`) that installs sdkman and uses it to
provision the current LTS version of the Eclipse Temurin JDK into the home
directory of every user listed in `desktop_user_names`.

## Scope

- One Ansible role: `roles/java/`
- Three tasks per user: download installer, run installer, install JDK
- One configurable variable: `java_sdkman_identifier` (default `"21.0.7-tem"`)
- No system-wide Java installation; per-user sdkman installations only
- No Molecule test suite; acceptance is a manual Vagrant run per `CONTRIBUTING.md`

## Out of Scope

- Air-gapped / offline support
- Windows targets
- Automatic sdkman self-updates
- Multiple simultaneous JDK vendors
- Removing or switching between installed versions

## Success Criteria

| ID | Criterion |
| --- | --- |
| SC-001 | `java -version` as any provisioned user exits 0 and output contains "Temurin" |
| SC-002 | Zero `changed` tasks on second consecutive playbook run |
| SC-003 | Role runs successfully on both AMD64 and ARM64 Ubuntu hosts |
| SC-004 | Installed JDK version matches `java_sdkman_identifier` in `defaults/main.yml` |
| SC-005 | Role can be exercised in isolation per `CONTRIBUTING.md` |
