# Progress

## What Works

- Provisioning and basic configuration of the `rivendell` and `hobbiton` Ubuntu VMs is fully automated.
- A pattern for adding new software via Ansible roles is well-established.

## What's Left to Build

- [ ] Research and document the manual installation steps for Kiro IDE on Ubuntu.
- [ ] Create a new Ansible role, tentatively named `setup-kiro-ide`.
- [ ] Implement tasks within the role to download and install the Kiro IDE.
- [ ] Update the main configuration playbooks to apply the `setup-kiro-ide` role to the `rivendell` and `hobbiton` hosts.
- [ ] Test the playbook to ensure Kiro IDE is installed correctly and the process is idempotent.
