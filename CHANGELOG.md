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

### Removed

- `podman` role default `login_user_names: []` — callers must supply at least
  one user name.

[Unreleased]: https://github.com/wonderbird/ansible-all-my-things/commits/main
