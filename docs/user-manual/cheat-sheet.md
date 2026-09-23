# Cheat Sheet and Recommendations

Prerequisite: You have run through [First Steps: Docker VM with Basic Profile](./docs/user-manual/first-steps.md).

## Periodically check for updates

```shell
ansible-playbook playbooks/update-versions/perform-updates.yml
git diff
git commit -am "build(deps): update [application], [application]"
git push
```

The run reports which tools it updated, which it skipped and which failed,
and `git diff` shows exactly what moved.

More information can be found in [Version Update Playbooks](./docs/architecture/version-update-playbooks.md).

## Shortcut to create and configure the first docker container

```shell
ansible-playbook playbooks/create-vm.yml --extra-vars provider=docker \
  && ansible-playbook playbooks/configure-profile.yml --skip-tags "not-supported-on-docker" --limit tatooine
```

## Quickly connect to host on any provider

```shell
HOST=edoras
inv=$(ansible-inventory --host "$HOST")
ssh -p "$(echo "$inv" | jq -r .ansible_port)" galadriel@"$(echo "$inv" | jq -r .ansible_host)"
```

Above command works even for docker hosts, where the port is other than 22
and ip is always 127.0.0.1.

## Quickly copy a file from a host to your local machine

For example to copy the setup-omc-prompt.md file from the remote into the
corresponding role's files directory:

```shell
HOST=tatooine
inv=$(ansible-inventory --host "$HOST")
scp -P "$(echo "$inv" | jq -r .ansible_port)" \
  "galadriel@$(echo \"$inv\" | jq -r .ansible_host):Documents/Cline/setup-omc-prompt.md" \
  ./roles/claude_code_config/files
```
