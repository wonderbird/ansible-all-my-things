# Developer Setup

## Optional Prerequisite: Spec-Kit

[GitHub Spec Kit](https://github.com/github/spec-kit) and [Claude Code](https://claude.ai)
can be used to extend this application. Consider installing the corresponding
tools as described in the [Spec Kit Getting Started Guide](https://github.com/github/spec-kit).

## CI/CD Pipeline Security

Workflow changes (adding, updating, or removing GitHub Actions) must follow
the two-tier pinning policy and allow-list requirements documented in
[ADR-002](docs/architecture/decisions/002-github-actions-pinning-policy.md).
That document also covers the one-time allow-list setup required when forking
this repository.

The pinning policy is enforced by
[`.github/workflows/pinning-lint.yml`](./.github/workflows/pinning-lint.yml)
on every push and pull request.

## Development Concepts

Development concepts are documented in
[docs/architecture/concepts](./docs/architecture/concepts/):

- [Role development workflow](./docs/architecture/concepts/role-development-workflow.md)
- [Toolchain docker image](./docs/architecture/concepts/toolchain-docker-image.md)
