# Review

## Done

- [ ] windows_admin_password was undefined in provisioners/aws-windows.yml

## Ongoing: Findings that are currently fixed

- [ ] Enable OpenSSH and allow SSH access as Administrator
- [ ] The image id '[ami-0c02fb55956c7d316]' does not exist. It seems we have to use '[ami-01998fe5b868df6e3]' instead. Update all occurrences of Windows Server 2022 with Windows Server 2025.

## Backlog

### Todos in context with the review

- [x] Try the workflow described in mvp usage guide (starting, RDP connection and stopping windows works. Test configuration. Is the immage the right one?)
- [ ] Set up a basic version of configure-aws-windows.yml with the following configuration: claude desktop
- [ ] Check whether structures can be simplified, merged and re-used; identify duplication, fix duplication

### Review Findings

#### provisioners/aws-windows.yml

- [ ] Allow SSH access from the computer invoking the ansible scripts

#### Test Findings

- [ ] Update documentation to avoid the following error: Failed to run instances: An error occurred (Unsupported) when calling the RunInstances operation: ED25519 key pairs are not supported with Windows AMIs. Choose a different key pair type and try again.
- [ ] After fixing these issues, the Windows Server is available, Claude Desktop can be installed manually and works.

#### Duplication

- [ ] Plausi-Checks (asserts) are redundant in provisioners/aws-windows.yml, provision-aws-windows.yml, configure-aws-windows.yml

#### docs/windows-server-mvp-usage.md

- [ ] executing the configure-aws-windows playbook results in this error: ERROR! couldn't resolve module/action 'ansible.windows.win_chocolatey'. This often indicates a misspelling, missing collection, or incorrect module path.

- [ ] Secrets set up is described in important concepts. Update that file instead.
- [ ] provision playbook should invoke the configure playbook
- [ ] Extract the section about performance, prerequisites, setting up the AWS account and environment variables into separate file. Re-use the file in docs/windows-server-mvp-usage.md and in docs/create-aws-vm.md
- [ ] ansible commands are missing the --vault-password-file ansible-vault-password.txt parameter; see docs/create-hetzner-vm.md for example.

#### docs/*aws*

- [ ] All AWS related documentation files should be placed into a separate folder docs/aws. Create a docs/aws.md that acts as an entry point to the detailed AWS documentation. Update top level README accordingly.

#### provision-aws-windows.yml

- [ ] Simplify configuration parameteres to the bare minimum. Remove options, if they are not needed for this iteration.

#### memory-bank/progress.md

- [ ] Tasks are only checked in the top section. Lower section tasks are still unticked.
