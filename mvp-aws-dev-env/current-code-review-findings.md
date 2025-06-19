# Code Review findings

## Rationale for the decision to host in the cloud and to add AWS

The reason for hosting the development environment on Hetzner or AWS is that I can run tools that are only available for an amd64 archtiecture. At the moment, I only have arm64 (Apple Silicon).

The far goal of adding AWS to the supported providers is add Windows based developer VMs to the stack. This extends support to programs only available for Windows.

- [x] Please update the memory bank and mvp description accordingly.

## Code Review Findings

- [x] provision.yml should be changed to match the structure of provision-aws.yml
- [x] the added vars.yml contains more configuration parameters than actually needed. Keet the number of configurable parameters at a minimum in favour of understandability, maintainability and extensibility.
- [x] Make sure that in future sessions, understandability, maintainability and extensibility are considered as important architecture drivers.
- [x] Make sure that in future sessions, you inform the user about conflicting priorities of quality criteria that lead to unclear design.

create-aws-vm.md

- [ ] the provisioning script shows errors:
  - [ ] The task includes an option with an undefined variable. The error was: ansible-dev-{{ ansible_date_time.epoch }}: 'ansible_date_time' is undefined. 'ansible_date_time' is undefined. ansible-dev-{{ ansible_date_time.epoch }}: 'ansible_date_time' is undefined. 'ansible_date_time' is undefined\n\nThe error appears to be in '/home/galadriel/Documents/Cline/ansible-all-my-things/provisioners/aws-ec2.yml': line 52, column 7, but may\nbe elsewhere in the file depending on the exact syntax problem.\n\nThe offending line appears to be:\n\n\n    - name: Launch EC2 instance\n      ^ here
  - [ ] botocore.exceptions.ClientError: An error occurred (InvalidAMIID.NotFound) when calling the RunInstances operation: The image id '[ami-0c02fb55956c7d316]' does not exist
- [ ] simplify the inventory file aws_ec2.yml
- [ ] Development environment for AWS needs the packages: sudo apt install python3-full ansible-core
- [ ] check the differences between create-hetzner-vm.md
- [ ] doc says "... with your desktop user" but uses "gandalf". Does this finding also apply to create-hetzner-vm.md?
- [ ] instead of specifying -e "aws_ssh_key_name=your-key-pair-name", make this a configuration variable

## Refactoring

- [ ] When testing is complete, instruct the LLM to refactor the code for understandability, maintainability and extensibility.

## Add to verification

I should add automated testing next.

- [ ] Hetzner setup must still work
- [ ] Tart setup must still work
