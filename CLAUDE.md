# CLAUDE.md

This project's authoritative guidance lives in **`AGENTS.md`** (agent
runtime) and **`.specify/memory/constitution.md`** (project rules).

**Before ANY action — including clarifying questions — read both files:**

1. Read `AGENTS.md`
2. Read `.specify/memory/constitution.md`

Do not proceed until both are read. Do not duplicate rules here — update
`AGENTS.md` or the constitution instead.

<!-- bd-doctor-divergence: ok -->


## Active Technologies
- Ansible (YAML), ansible-core (project default) + Vagrant 2.x, vagrant-tart provider, `tart` CLI (macOS) (009-create-destroy-vm)
- Static YAML inventory `inventories/vagrant_tart.yml`; per-VM (009-create-destroy-vm)

## Recent Changes
- 009-create-destroy-vm: Added Ansible (YAML), ansible-core (project default) + Vagrant 2.x, vagrant-tart provider, `tart` CLI (macOS)
