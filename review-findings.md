# Review findings

## Rationale for the decision to host in the cloud and to add AWS

The reason for hosting the development environment on Hetzner or AWS is that I can run tools that are only available for an amd64 archtiecture. At the moment, I only have arm64 (Apple Silicon).

The far goal of adding AWS to the supported providers is add Windows based developer VMs to the stack. This extends support to programs only available for Windows.

- [x] Please update the memory bank and mvp description accordingly.

## General Findings

- [x] Make sure that in future sessions, understandability, maintainability and extensibility are considered as important architecture drivers.
- [x] Make sure that in future sessions, you inform the user about conflicting priorities of quality criteria that lead to unclear design.

The directory "mvp-aws-dev-env" contains documentation that fits to the same category as documentation in the memory-bank.

- [ ] Merge the file "implementation-plan.md" into the appropriate files of the memory-bank and then remove it
- [ ] Merge the file "use-case-description.md" into the appropriate files of the memory-bank and then remove it

## Code review findings

### provision.yml

- [x] provision.yml should be changed to match the structure of provision-aws.yml

### vars.yml

- [x] the added vars.yml contains more configuration parameters than actually needed. Keet the number of configurable parameters at a minimum in favour of understandability, maintainability and extensibility.

### provisioners/aws-ec2.yml

- [ ] The task includes an option with an undefined variable. The error was: ansible-dev-{{ ansible_date_time.epoch }}: 'ansible_date_time' is undefined. 'ansible_date_time' is undefined. ansible-dev-{{ ansible_date_time.epoch }}: 'ansible_date_time' is undefined. 'ansible_date_time' is undefined\n\nThe error appears to be in '/home/galadriel/Documents/Cline/ansible-all-my-things/provisioners/aws-ec2.yml': line 52, column 7, but may\nbe elsewhere in the file depending on the exact syntax problem.\n\nThe offending line appears to be:\n\n\n    - name: Launch EC2 instance\n      ^ here
- [ ] botocore.exceptions.ClientError: An error occurred (InvalidAMIID.NotFound) when calling the RunInstances operation: The image id '[ami-0c02fb55956c7d316]' does not exist

### inventories/aws/aws_ec2.yml

- [ ] simplify the inventory file aws_ec2.yml

### playbooks/setup-desktop.yml

- [ ] Development environment for AWS needs the packages: sudo apt install python3-full ansible-core

### docs/create-aws-vm.md

- [x] remove information not desired in a user's manual
- [ ] Markdown file violates code style rules
- [ ] add a section "Notes on Performance" to the top. Adopt the section from the corresponding section in create-hetzner-vm.md
