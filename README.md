# Ansible automation for my IT system

Automated setup and updates for my IT system.

## Overview

This repository defines virtual machine configurations for software developers.
The following infrastructure is defined:

| Provider      | Platform | Operating System    | Architecture | Host name pool                              | Region          | Auth chain              |
| ------------- | -------- | ------------------- | ------------ | -------------------------------------------- | --------------- | ----------------------- |
| AWS EC2       | Windows  | Windows Server 2025 | AMD64        | [`playbooks/vars/hostname_pool_aws.yml`](./playbooks/vars/hostname_pool_aws.yml)       | eu-north-1      | Administrator           |
| AWS EC2       | Linux    | Ubuntu Linux        | AMD64        | [`playbooks/vars/hostname_pool_aws.yml`](./playbooks/vars/hostname_pool_aws.yml)       | eu-north-1      | ubuntu → galadriel      |
| Hetzner Cloud | Linux    | Ubuntu Linux        | AMD64        | [`playbooks/vars/hostname_pool_hcloud.yml`](./playbooks/vars/hostname_pool_hcloud.yml)    | Helsinki (hel1) | root → galadriel        |
| Tart          | Linux    | Ubuntu Linux        | ARM64        | [`playbooks/vars/hostname_pool_tart.yml`](./playbooks/vars/hostname_pool_tart.yml)      | local           | admin → galadriel       |
| Docker        | Linux    | Ubuntu Linux        | ARM64        | [`playbooks/vars/hostname_pool_docker.yml`](./playbooks/vars/hostname_pool_docker.yml)    | local           | root → galadriel        |

For current pricing see the comments in the provider-specific group_vars
files, e.g. [`hcloud_linux/vars.yml`][hcloud-linux-vars].

[hcloud-linux-vars]: ./inventories/group_vars/hcloud_linux/vars.yml

## Quick Start

New to this repository? Start here:

- [First Steps: Docker VM with Basic Profile](./docs/user-manual/first-steps.md)

Further setup instructions:

- [Create Virtual Machines](./docs/user-manual/create-vm.md)
- [Important Concepts](./docs/user-manual/important-concepts.md)
- [Work with a VM](./docs/user-manual/work-with-vm.md)
- [Backup and Restore](./docs/user-manual/backup-restore.md)
- [Synchronize Git Repositories with a VM](./docs/user-manual/synchronize-repos-with-vm.md)

## Documentation

The [/docs](./docs/) folder contains documentation for some aspects of the system.

## Notes on Performance

If you experience poor performance, then consider the following tuning parameters:

- select a different region to host the instance(s)
- select a larger instance type

## Acknowledgements

My first contact with Ansible was at the 36c3. Many thanks to Heiko Borchers
for the inspiring talk [Ansible all the Things][aat] (13 min) [borchers2019].

[aat]: https://media.ccc.de/v/36c3-90-ansible-all-the-things

This project uses code, documentation and ideas generated with the assistance
of large language models.

## References

[borchers2019] H. Borchers, _Ansible all the Things_, (Dec. 30, 2019).
Accessed: May 29, 2025. [Online Video]. Available: [media.ccc.de][aat]

[boos2025b] S. Boos, “wonderbird/ansible-for-devops: Exercises from the Book
Jeff Geerling: ‘Ansible for DevOps’, 2nd Ed., Leanpub, 2023.”
Accessed: May 03, 2025. [Online]. Available: [github.com][boos2025b-url]

[boos2025b-url]: https://github.com/wonderbird/ansible-for-devops

[geerling2023] J. Geerling, _Ansible for DevOps_, 2nd ed. Leanpub, 2023.
Accessed: Apr. 20, 2025. [Online]. Available:
[ansiblefordevops.com][geerling2023-url]

[geerling2023-url]: https://www.ansiblefordevops.com/
