# System Patterns

Software installation is managed through dedicated Ansible roles. Each role is responsible for a single piece of software (e.g., `setup-vscode`, `setup-git`). Configuration logic is applied idempotently, ensuring systems reach the desired state regardless of their starting point. Playbooks orchestrate the application of these roles to specific host groups defined in the inventory.
