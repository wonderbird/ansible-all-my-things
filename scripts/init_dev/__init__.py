"""Initialize a fresh clone of this repository for development.

Runs on the Ubuntu VMs this repository provisions. Every step is safe to
re-run, because agent VMs are destroyed and re-provisioned regularly.

The package uses the standard library only: it runs on the system python3,
before the venv and its packages exist.

Usage, from the repository root: python3 -m scripts.init_dev
"""
