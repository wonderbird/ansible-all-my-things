# Product Context — feat.podman.role

## Why This Feature Exists

The developer runs an AI coding agent inside a sandboxed Linux VM to prevent
the agent from accidentally modifying the host laptop. The agent needs to
autonomously verify Ansible role acceptance criteria — which requires
building and running containers from this repository.

Podman is the container runtime chosen because:

- It runs rootless (no daemon, no root privilege required)
- It is available in the Ubuntu apt package repository
- `podman build` natively supports the `--mount=type=cache` syntax used in
  `.devcontainer/Dockerfile` (Podman 4+ / buildah backend)
- No Docker daemon or systemd socket needed

## Containers in Scope

### `.devcontainer/Dockerfile` — Ansible Control Node

- Base: `docker.io/python:trixie`
- Purpose: runs Ansible playbooks and CLI tools (AWS CLI, Hetzner CLI)
- Uses BuildKit cache mounts (`--mount=type=cache`) — supported by Podman
  natively; the `# syntax=docker/dockerfile:1` comment is silently ignored
- Built with: `podman build -t devcontainer .devcontainer/`

### `test/docker/Dockerfile` — Test Target (OUT OF SCOPE)

- Base: `ubuntu:24.10` with systemd + SSH
- Requires privileged / rootful mode to run systemd inside
- Explicitly excluded from this iteration

## User Experience Goals

After the role is applied to the VM, any user in `desktop_user_names` can:

```bash
podman build -t devcontainer .devcontainer/
podman run --rm devcontainer ansible --version
```

The AI agent uses these commands to verify that the Ansible tooling is
available before running further automation tasks.

## Broader Vision

The Podman role is a prerequisite for a larger AI agent sandbox feature:
the agent will use the devcontainer to run Ansible playbooks and acceptance
tests autonomously, replacing manual acceptance test execution by the
developer.
