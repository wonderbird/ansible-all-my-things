# Developer Setup

## Optional Prerequisite: Spec-Kit

[GitHub Spec Kit](https://github.com/github/spec-kit) and [Claude Code](https://claude.ai)
can be used to extend this application. Consider installing the corresponding
tools as described in the [Spec Kit Getting Started Guide](https://github.com/github/spec-kit).

After running `specify integration upgrade claude` (or any spec-kit update),
check whether any `.claude/commands/speckit.*.md` file now duplicates a
`.claude/skills/speckit-*/` entry, and delete the command file if so —
spec-kit's updater does not remove superseded files from older installs.

## CI/CD Pipeline Security

Workflow changes (adding, updating, or removing GitHub Actions) must follow
the two-tier pinning policy and allow-list requirements documented in
[ADR-002](docs/architecture/decisions/002-github-actions-pinning-policy.md).

The pinning policy is enforced by
[`.github/workflows/pinning-lint.yml`](./.github/workflows/pinning-lint.yml)
on every push and pull request.

### Fork setup (one-time)

The GitHub Actions allow-list is a repository setting and does not transfer
on fork. After forking, re-enable it in your fork:

1. Go to **Settings → Actions → General** in your fork.
2. Under "Actions permissions", select
   **"Allow select actions and reusable workflows"**.
3. Paste the following entries into the allow-list field and save:

   ```text
   actions/checkout@*,
   actions/setup-python@*,
   actions/download-artifact@*,
   actions/upload-artifact@*,
   docker/build-push-action@*,
   docker/login-action@*,
   docker/metadata-action@*,
   docker/setup-buildx-action@*,
   github/codeql-action/upload-sarif@*,
   sigstore/cosign-installer@*,
   zizmorcore/zizmor-action@*
   ```

The list above is the canonical source. When adding a new action, add its
`owner/repo@*` entry here and to the allow-list in repository settings. For
the two-tier pinning policy and rationale, see
[ADR-002](docs/architecture/decisions/002-github-actions-pinning-policy.md).

## Development Concepts

Development concepts are documented in
[docs/architecture/concepts](./docs/architecture/concepts/):

- [Role development workflow](./docs/architecture/concepts/role-development-workflow.md)
- [Toolchain docker image](./docs/architecture/concepts/toolchain-docker-image.md)
