# Developer Setup

## Initialize a Fresh Clone

On a VM provisioned by this repository, run from the repository root:

```shell
python3 -m scripts.init_dev
```

The [init_dev README](scripts/init_dev/README.md) describes what it sets up
and how to develop it.

## Optional Prerequisites: OMC, Skills, Spec-Kit

When developing in this repository I use Claude Code with the
[Oh My Claude Code](https://github.com/yeachan-heo/oh-my-claudecode) plugin.

In addition, I use the skills listed in `.skills.json` with
[Skill Manager](https://github.com/omrikais/skill-manager). The
initialization above deploys them into the clone.

[GitHub Spec Kit](https://github.com/github/spec-kit) and
[Claude Code](https://claude.ai)
can be used to extend this application. Consider installing the corresponding
tools as described in the
[Spec Kit Getting Started Guide](https://github.com/github/spec-kit).

After upgrading Spec Kit, check whether any `.claude/commands/speckit.*.md` file
now duplicates a `.claude/skills/speckit-*/` entry, and delete the command file
if so — spec-kit's updater does not remove superseded files from older installs.

## Contributing Changes

The per-change workflow — branch naming, local testing, commit format,
changelog entries, review and merge — is defined in
[the project constitution](.specify/memory/constitution.md), section
"Development Workflow". It is binding for human and agent contributors alike.

Agent-specific runtime guidance lives in [AGENTS.md](AGENTS.md).

### Python Scripts

ruff formats and lints the Python scripts under `scripts/`, configured by
[`ruff.toml`](ruff.toml). The pre-commit git hook, which the initialization
installs, runs it on every commit and rejects a commit until its scripts
pass; [`.pre-commit-config.yaml`](.pre-commit-config.yaml) defines the hook.

To run ruff by hand, from the repository root with the venv active:

```shell
ruff format scripts/
ruff check scripts/
```

## CI/CD Pipeline Security

Workflow changes (adding, updating, or removing GitHub Actions) must follow
the single-tier pinning policy and allow-list requirements documented in
[ADR-007](docs/architecture/decisions/007-single-tier-action-pinning.md).

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
the pinning policy and rationale, see
[ADR-007](docs/architecture/decisions/007-single-tier-action-pinning.md).

## Development Concepts

Development concepts are documented in
[docs/architecture/concepts](./docs/architecture/concepts/):

- [Testing concepts](./docs/architecture/concepts/testing.md)
- [Toolchain docker image](./docs/architecture/concepts/toolchain-docker-image.md)
