# Review

## Done

- [x] windows_admin_password was undefined in provisioners/aws-windows.yml
- [x] Enable OpenSSH and allow SSH access as Administrator
- [x] The image id '[ami-0c02fb55956c7d316]' does not exist. It seems we have to use '[ami-01998fe5b868df6e3]' instead. Update all occurrences of Windows Server 2022 with Windows Server 2025.
- [x] Why is the message "Display Windows Server instance information" not printed after provisioning? This is because the configure-aws-windows.yml playbook must be executed manually after provisioning.
- [x] Try the workflow described in mvp usage guide (starting, RDP connection and stopping windows works. Test configuration. Is the immage the right one?)
- [x] In memory-bank/progress.md tasks are only checked in the top section. Lower section tasks are still unticked.
- [x] After fixing these issues, the Windows Server is available, Claude Desktop can be installed manually and works.
- [x] Document how to read the IPV4_ADDRESS of the server. I like to use the following command: `export AWS_INSTANCE=lorien-windows; export IPV4_ADDRESS=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=$AWS_INSTANCE" "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].PublicIpAddress' --output text); echo "IP of AWS instance $AWS_INSTANCE: $IPV4_ADDRESS"`
- [x] We have a working OpenSSH server on the windows machine. Update all documentation to reflect that SSH is enabled on the server.
- [x] AWS does not allow ED25519 key pairs for Windows AMIs. Update the documentation
- [x] All AWS related documentation files should be placed into a separate folder docs/aws. Create a docs/aws.md that acts as an entry point to the detailed AWS documentation. Update top level README accordingly.
- [x] ansible commands are missing the --vault-password-file ansible-vault-password.txt parameter; see docs/create-hetzner-vm.md for example.
- [x] Secrets set up is described in important concepts. Remove the redundant information and replace it with a link to the important concepts. If necessary, update important concepts with new information.
- [x] Extract the section about performance, prerequisites, setting up the AWS account and environment variables into separate file. Re-use the file in docs/windows-server-mvp-usage.md and in docs/create-aws-vm.md
- [x] Run the configure-aws-windows.yml file and check the results
- [x] Required by parent: Can we use SSH for ansible automation instead of WinRM? -> Yes.
- [x] Required by parent: Set up key based SSH login
- [x] Windows Admin Passwort wird nicht in den Secrets benötigt, wenn der SSH Key geladen ist! - Falsch: Das Passwort wird für den Remote Desktop Nutzer benötigt.
- [x] Plausi-Checks (asserts) are redundant in provisioners/aws-windows.yml, provision-aws-windows.yml, configure-aws-windows.yml
- [x] executing the configure-aws-windows playbook results in this error: ERROR! couldn't resolve module/action 'ansible.windows.win_chocolatey'. This often indicates a misspelling, missing collection, or incorrect module path.
- [x] provision-aws-windows.yml: Remove unneccesary parts
- [x] provision-aws-windows.yml: Simplify configuration parameteres to the bare minimum. Remove options, if they are not needed for this iteration.
- [x] provision-aws-windows.yml: provision playbook should invoke the configure playbook. Implementation should be similar to the Hetzner pattern in provision.yml.
- [x] Remove unused variables in inventories/aws/group_vars/aws_windows/vars.yml
- [x] Dokumentation aus inventories/hcloud/hcloud.yml in ein Dok-Verzeichnis verschieben, welches die gesamte technische Infra beschreibt. Ggf. ist es an der Zeit, Konzepte in tech Dok festzuhalten.
- [x] hcloud_ssh_key_name gehört eigenlich in die secrets, oder? auch für AWS; selben key name benutzen
  - [x] Verifiziere nochmal, dass das destroy-aws.yml Playbook funktioniert, wenn es eine Linux und eine Windows Instanz gibt.
- [x] Vereinfache inventories/aws/aws_ec2.yml - Lösche nicht benötigte Variablen
- [x] Sicherstellen, dass die AWS Security Group für beide Playbooks dieselbe ist.
- [x] Below the inventories folder the groups aws_dev, windows and dev are present. Please rename the groups as follows: "aws_dev" and "dev" shall be named "linux" and address all virtual machines with a Linux operating system. The "windows" group shall stay as it is.
- [x] The host names for each combination shall be unique:

  - (hcloud, linux): hobbiton
  - (aws, linux): rivendell
  - (aws, windows): moria
  - (vagrant+tart, linux): lorien
  - (vagrant+docker, linux): dagorlad
- [x] The Ansible group "dev" should be renamed to"linux" group, i.e. merge "dev" with the existing group "linux". The group is used by the provisioners below the ./test/ directory.
- [x] Verify that the Vagrant groups have been completely renamed to linux
- [x] Run the test documented in the memory bank and verify that the unified inventory works
- [x] Können die Inventories für alle Provider in einer einzigen Datei zusammengeführt werden - nimm auch Vagrant+Docker und Tart+Docker in diese konsolidierte Ansible Konfiguration

## Ongoing: Findings that are currently fixed

Identifiziere das nächste Finding.

Dokumentations-Findings haben oberste Prio, damit ich meinen Projektfokus jederzeit wechseln kann und mich später wieder schnell zurecht finde.


## Backlog

### Todos in context with the review

- [ ] Verschiebe die Nicht-Geheimniss aus den secrets in die vars.yml Dateien

- [ ] Sollte das Ansible Vault statt in playbooks/vars-secrets.yml woanders liegen? z.B. unter dem jeweiligen Inventory? Bsp: inventories/aws/group_vars/aws_windows

- [ ] Document an overview of the group_vars design in inventories/README.md file. Keep it short and simple. Include the hierarchy as a mermaid diagram. Describe that hierarchy in a paragraph below the diagram.

- [ ] Installiere die notwendigen Tools auf der VM: aws cli, hcloud cli. Problem: hcloud CLI gibt es nicht für arm64 (tart) als binary; Man kann auf tart/linux hcloud cli auch nicht bauen. Folgt man der Bauanleitung in CONTRIBUTING.md, dann steigt eine Logging / Unit Testing Dependency mit dem Fehler aus, dass es keine Unterstützung für arm64/Linux gibt.

- [ ] Konfiguriere die Zugriffsrechte auf die Cloud Inventories.

- [ ] Will ich die Security Groups in AWS wirklich beibehalten? Sind sie nicht entgegen meines Use Case?

- [ ] Lösche unnötige Konfigurations-Optionen aus aws-windows.yml und aus der Doku; z.B. `aws_default_region` und die zugehörige Umgebungsvariable

- [ ] AWS Linux Computer soll genauso (fertig-)konfiguriert werden wie die Hetzner VM. Versuche, die Provider spezifische Konfiguration komplett über das entsprechende Provisioner Skript abzubilden. Falls das nicht möglich ist: Helfen Provider spezifische Inventory Gruppen, z.B. "hcloud_linux", "aws_linux", "aws_windows"?

- [ ] Check whether structures can be simplified, merged and re-used; identify duplication, fix duplication

## Nächste Schritte

- [ ] Struktur vereinheitlichen: linux (hetzner, aws); windows; setup scripte ggf. in Rollen umwandeln; linux sollte ggf. aws_linux heißen; aws_ec2 sollte in teilen ebenfalls aws_linux heißen; "linux" als Gruppe einführen analog zu "windows"; Playbooks auf owindows / linux einschränken - insbesondere die hcloud Playbooks enthalten "dev" oder "all" als Einschränkung
