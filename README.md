# Ansible automation for my IT system

Automated setup and updates for my IT system.

## Overview

This repository defines virtual machine configurations for software developers. The following infrastructure is defined:

| Provider | Operating System | Host name |
| --- | --- | --- |
| AWS EC2 | Windows Server 2025 | moria |
| AWS EC2 | Ubuntu Linux | rivendell |
| Hetzner Cloud | Ubuntu Linux | hobbiton |
| Vagrant, Tart | Ubuntu Linux | lorien |
| Vagrant, Docker | Ubuntu Linux | dagorlad |

## Quick Start

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Install Ansible collections:**
   ```bash
   ansible-galaxy collection install -r requirements.yml
   ```

3. **Follow setup instructions:**
   - [Important Concepts](./docs/important-concepts.md)
   - [Create Virtual Machines](./docs/create-vm.md)
   - [Work with a VM](./docs/work-with-vm.md)
   - [Synchronize Git Repositories with a VM](./docs/synchronize-repos-with-vm.md)

## Documentation

The [/docs](./docs/) folder contains documentation for some aspects of the system.

## Notes on Performance

If you experience poor performance, then consider the following tuning parameters:

- select a different region to host the instance(s)
- select a larger instance type

## Acknowledgements

My first contact with Ansible was at the 36c3. Many thanks to Heiko Borchers for the inspiring talk [Ansible all the Things](https://media.ccc.de/v/36c3-90-ansible-all-the-things) (13 min) [borchers2019].

This project uses code, documentation and ideas generated with the assistance of large language models.

## References

[borchers2019] H. Borchers, _Ansible all the Things_, (Dec. 30, 2019). Accessed: May 29, 2025. [Online Video]. Available: [https://media.ccc.de/v/36c3-90-ansible-all-the-things](https://media.ccc.de/v/36c3-90-ansible-all-the-things)

[boos2025b] S. Boos, “wonderbird/ansible-for-devops: Exercises from the Book Jeff Geerling: ‘Ansible for DevOps’, 2nd Ed., Leanpub, 2023.” Accessed: May 03, 2025. [Online]. Available: [https://github.com/wonderbird/ansible-for-devops](https://github.com/wonderbird/ansible-for-devops)

[geerling2023] J. Geerling, _Ansible for DevOps_, 2nd ed. Leanpub, 2023. Accessed: Apr. 20, 2025. [Online]. Available: [https://www.ansiblefordevops.com/](https://www.ansiblefordevops.com/)
