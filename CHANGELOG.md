# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/2.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- `configure-profile.yml` fails at preflight when `login_users` is undefined
  or empty.
- Roles that configure per-user state fail when `login_user_names` is
  undefined or empty.
- `perform-updates.yml` reports every tool that failed, and keeps updating the
  other tools when one upstream source is unavailable.
- `perform-updates.yml` no longer supports `--check`.

### Removed

- `podman` role default `login_user_names: []` — callers must supply at least
  one user name.

### Fixed

- `perform-updates.yml` fails, naming the file and pin, when a pin is missing
  or duplicated.
- `perform-updates.yml` fails, naming the repository and tag, when a tool's
  latest GitHub release lacks the asset that tool installs.

[Unreleased]: https://github.com/wonderbird/ansible-all-my-things/commits/main
