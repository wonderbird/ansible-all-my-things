# Improvement Backlog

## Done

- [x] Create a backup for configuration files in the home directory, especially for ~/.gitconfig
- [x] Should the Ansible Vault be located somewhere else instead of in playbooks/vars-secrets.yml? E.g., under the respective inventory? Example: inventories/aws/group_vars/aws_windows
  
## In progress

nothing

## Backlog

Sorted by priority - Last update: 2025-07-15

- [ ] To provision Vagrant VMs, use the same `--extra-vars "provider=hcloud platform=linux"` mechanism as for cloud instances. The mechanism is described in [./create-vm.md](./create-vm.md). I assume that we can move the vagrant commands into a provisioner specific playbook and then provision and destroy the VMs like for the cloud instances.

- [ ] Create automatic tests

  - [ ] Install the necessary tools on the VM: aws cli, hcloud cli. Problem: hcloud CLI is not available for arm64 (tart) as a binary; you cannot build hcloud cli on tart/linux either. If you follow the build instructions in CONTRIBUTING.md, a logging/unit testing dependency will fail with the error that there is no support for arm64/Linux.

  - [ ] Configure access rights to the cloud inventories.

- [ ] Create a backup for the claude configuration files

- [ ] The backup should only be restored for galadriel. Other users should configure their own credentials, API keys, etc.

- [ ] Is an Alpine Linux on a minimal VM sufficient to serve Visual Studio Code remote editing?

- [ ] Document an overview of the group_vars design in inventories/README.md file. Keep it short and simple. Include the hierarchy as a mermaid diagram. Describe that hierarchy in a paragraph below the diagram.

- [ ] Do I really want to keep the IP restriction in the security groups in AWS? Aren't they contrary to my use case?

- [ ] Configure the firewall on Hetzner the same way as on AWS

- [ ] Move the non-secrets from the secrets to the vars.yml files

- [ ] AWS Linux computers should be configured in the same way as the Hetzner VM. Try to map the provider-specific configuration completely using the corresponding provisioner script. If this is not possible: Do provider-specific inventory groups help, e.g., “hcloud_linux,” “aws_linux,” “aws_windows”?
  - [ ] Convert setup scripts into roles if necessary; restrict playbooks to Windows/Linux – in particular, the hcloud playbooks contain “dev” or “all” as a restriction.

- [ ] Check whether structures can be simplified, merged and re-used; identify duplication, fix duplication

---

Parts of this document were translated with DeepL.com (free version) (Thank you, DeepL ❤️)