# Review

## Done

- [x] windows_admin_password was undefined in provisioners/aws-windows.yml
- [x] Enable OpenSSH and allow SSH access as Administrator
- [x] The image id '[ami-0c02fb55956c7d316]' does not exist. It seems we have to use '[ami-01998fe5b868df6e3]' instead. Update all occurrences of Windows Server 2022 with Windows Server 2025.
- [x] Why is the message "Display Windows Server instance information" not printed after provisioning? This is because the configure-aws-windows.yml playbook must be executed manually after provisioning.
- [x] In memory-bank/progress.md tasks are only checked in the top section. Lower section tasks are still unticked.
- [x] After fixing these issues, the Windows Server is available, Claude Desktop can be installed manually and works.
- [x] Document how to read the IPV4_ADDRESS of the server. I like to use the following command: `export AWS_INSTANCE=lorien-windows; export IPV4_ADDRESS=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=$AWS_INSTANCE" "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].PublicIpAddress' --output text); echo "IP of AWS instance $AWS_INSTANCE: $IPV4_ADDRESS"`

## Ongoing: Findings that are currently fixed

Identifiziere das nächste Finding.

Dokumentations-Findings haben oberste Prio, damit ich meinen Projektfokus jederzeit wechseln kann und mich später wieder schnell zurecht finde.

## Backlog

### Todos in context with the review

- [x] Try the workflow described in mvp usage guide (starting, RDP connection and stopping windows works. Test configuration. Is the immage the right one?)
- [ ] Run the configure-aws-windows.yml file and check the results
- [ ] Can we use SSH for ansible automation instead of WinRM?
- [ ] Update all documentation to reflect that SSH is enabled on the server
- [ ] Set up a basic version of configure-aws-windows.yml with the following configuration: claude desktop
- [ ] Check whether structures can be simplified, merged and re-used; identify duplication, fix duplication

### Review Findings

#### Test Findings

- [ ] AWS does not allow ED25519 key pairs for Windows AMIs. Update the documentation

#### Duplication

- [ ] Plausi-Checks (asserts) are redundant in provisioners/aws-windows.yml, provision-aws-windows.yml, configure-aws-windows.yml

#### docs/windows-server-mvp-usage.md

- [ ] executing the configure-aws-windows playbook results in this error: ERROR! couldn't resolve module/action 'ansible.windows.win_chocolatey'. This often indicates a misspelling, missing collection, or incorrect module path.

- [ ] Secrets set up is described in important concepts. Remove the redundant information and replace it with a link to the important concepts. If necessary, update important concepts with new information.
- [ ] provision playbook should invoke the configure playbook. Implementation should be similar to the Hetzner pattern in provision.yml.
- [ ] Extract the section about performance, prerequisites, setting up the AWS account and environment variables into separate file. Re-use the file in docs/windows-server-mvp-usage.md and in docs/create-aws-vm.md
- [ ] ansible commands are missing the --vault-password-file ansible-vault-password.txt parameter; see docs/create-hetzner-vm.md for example.

#### docs/*aws*

- [ ] All AWS related documentation files should be placed into a separate folder docs/aws. Create a docs/aws.md that acts as an entry point to the detailed AWS documentation. Update top level README accordingly.

#### provision-aws-windows.yml

- [ ] Simplify configuration parameteres to the bare minimum. Remove options, if they are not needed for this iteration.

#### inventories/aws/group_vars/aws_windows/vars.yml

- [ ] Remove unused variables

#### scripts/create-remote-repository.sh and scripts/delete-remote-repository.sh

- [ ] The shell scripts in the scripts folder should be python scripts, so that they are more compatible with other platforms and so that they can be integrated into a real application later