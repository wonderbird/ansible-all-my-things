# Improvement Backlog

## Done

- [x] Allow distinguishing the instances by their fixed names. Rename lorien-windows to moria, lorien (aws,linux) to rivendell
- [x] Create a backup for configuration files in the home directory, especially for ~/.gitconfig
- [x] Move Ansible Vault from playbooks/vars-secrets.yml to inventories/aws/group_vars/all
- [x] Simplify the "admin_user_on_fresh_system" concept - The admin_user_on_fresh_system can be configured in the inventory of the corresponding group in vars.yml. Do I want to keep the `gandalf` user?

## In progress

This section lists all started product increments. The list is sorted by start date, newest on top. If there is more than one increment, then the older ones were interrupted by the newer ones. Reason is usually a dependency or feature split.

However, be careful not to allow feature creep!

- [ ] (large increment) **Command restrictions:** Deploy command restriction system to target systems that prevents AI agents from executing infrastructure commands.

- [ ] (large increment) **Consistent provisioning style:** To provision Vagrant VMs, use the same `--extra-vars "provider=hcloud platform=linux"` mechanism as for cloud instances. The mechanism is described in [./create-vm.md](./create-vm.md). I assume that we can move the vagrant commands into a provisioner specific playbook and then provision and destroy the VMs like for the cloud instances.

- [ ] **docs/update**: Transfer insights from memory bank to user facing documentation and to developer facing documentation.

## Backlog of large increments

This backlog contains larger increments. It is sorted by priority.

- [ ] Create automatic tests
  - [ ] Install the necessary tools on the VM: aws cli, hcloud cli. Problem: hcloud CLI is not available for arm64 (tart) as a binary; you cannot build hcloud cli on tart/linux either. If you follow the build instructions in CONTRIBUTING.md, a logging/unit testing dependency will fail with the error that there is no support for arm64/Linux.
  - [ ] Configure access rights to the cloud inventories.

- [ ] Document an overview of the group_vars design in inventories/README.md file. Keep it short and simple. Include the hierarchy as a mermaid diagram. Describe that hierarchy in a paragraph below the diagram.

- [ ] The number of instances shall be easy to change
  - [ ] Allow adding instances and one by one on demand
  - [ ] Allow destroying individual instances on demand

- [ ] Create a backup for the claude configuration files

- [ ] Is an Alpine Linux on a minimal VM sufficient to serve Visual Studio Code remote editing?

- [ ] Next for the Windows VM: Install updates to AWS Windows and reboot the machine if necessary

- [ ] Do I really want to keep the IP restriction in the security groups in AWS? Aren't they contrary to my use case?

- [ ] Configure the firewall on Hetzner the same way as on AWS

- [ ] Reconsider backup concept. At the moment, the first desktop user is backed up, the others are ignored.
  - [ ] The backup should only be restored for galadriel. Other users should configure their own credentials, API keys, etc.
  - [ ] Rename the folder `configuration/home/my_desktop_user` to `.../backup_user`

- [ ] AWS Linux computers should be configured in the same way as the Hetzner VM. Try to map the provider-specific configuration completely using the corresponding provisioner script. If this is not possible: Do provider-specific inventory groups help, e.g., “hcloud_linux,” “aws_linux,” “aws_windows”?
  - [ ] Convert setup scripts into roles if necessary; restrict playbooks to Windows/Linux – in particular, the hcloud playbooks contain “dev” or “all” as a restriction.

- [ ] The shell scripts in the scripts folder should be python scripts, so that they are more compatible with other platforms and so that they can be integrated into a real application later

## Backlog of small improvements (pick one for each large increment)

- [ ] (small improvement) **Keep only seecrets in vault:** Move the non-secrets from the secrets to the vars.yml files

- [ ] Do I want to allow updating a VM? Today, updating a VM by re-executing the corresponding configure-*.yml playbook is not possible. Is this because of some deactivation in `setup-users.yml`?

- [ ] Check whether structures can be simplified, merged and re-used; identify duplication, fix duplication
  - [ ] Is it possible to reduce code duplication for determining the value of the `desktop_user_names` and `all_users`? (Important concept: Separate user names from passwords so that we can log them without accidentially logging the passwords)

---

Parts of this document were translated with DeepL.com (free version) (Thank you, DeepL ❤️)