# Project Brief — feat.podman.role

## Project

`ansible-all-my-things` — an Ansible automation repository that provisions
Linux (Ubuntu) and Windows Server machines on local VMs (Vagrant + Tart /
Docker) and cloud targets (AWS EC2, Hetzner Cloud).

## Iteration Goal

Add a `podman` Ansible role that installs rootless Podman on an Ubuntu Linux
VM, so that an AI coding agent running inside that VM can build and run the
Docker-compatible containers shipped with this repository.

## Problem Statement

The developer wants to run an AI coding agent (e.g. Claude Code) inside a
sandboxed Linux VM. The sandbox prevents the agent from modifying the host
laptop. The agent needs to execute acceptance tests for Ansible roles
autonomously — without the developer manually running commands. Podman is
the container runtime that enables the agent to build the Ansible control
node container (`.devcontainer/Dockerfile`) and spin up test targets.

## Scope

- New role: `roles/podman/`
- Install Podman via Ubuntu `apt`
- Configure rootless Podman per-user (loop over `desktop_user_names`)
- Manage `/etc/subuid` and `/etc/subgid` with `ansible.builtin.lineinfile`
- No Docker compatibility shim; `podman build` / `podman run` directly
- Only `.devcontainer/Dockerfile` is in scope; `test/docker/Dockerfile`
  (systemd-based) is explicitly out of scope for this iteration

## Out of Scope

- Running containers with systemd inside (privileged / rootful mode)
- `podman-docker` shim
- `registries.conf` customisation
- `loginctl enable-linger` (no container services, interactive use only)
- Ubuntu version pre-flight assert
