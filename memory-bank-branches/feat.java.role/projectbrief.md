# Project Brief: Java Role (sdkman + Temurin JDK)

**Feature Branch**: `005-java-role`
**Primary source of truth**: [`specs/005-java-role/`](../../../../specs/005-java-role/)

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

For user stories, requirements, success criteria, edge cases, and assumptions
see [`specs/005-java-role/spec.md`](../../../../specs/005-java-role/spec.md).
