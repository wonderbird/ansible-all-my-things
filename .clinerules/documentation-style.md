# Documentation Style

## Ansible Playbook Commands in Documentation

Shell commands MUST follow the same pattern, so that the users can use their shell history most efficiently.

In the documentation, `ansible-playbook` commands MUST always follow this format:

```shell
ansible-playbook --vault-password-file ansible-vault-password.txt PLAYBOOK.yml
```

Depending on the playbook, the `--extra-vars` and `--skip-tags` paramters MUST FOLLOW AFTER the PLAYBOOK.yml file name.
