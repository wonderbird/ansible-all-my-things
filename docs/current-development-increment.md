# Current Development Increment

## Work in progress: Apply idiomatic Ansible for secrets

Remove the explicit loading of `vars-usernames.yml` and `vars-secrets.yml` from all playbooks - especially the ones in the `/playbooks` folder. Transition from encrypted `playbook/vars-secrets.yml` to encrypted `inventories/group_vars/all/vars.yml`.

When setting up this project, I did not know how variables and secrets are handled in Ansible. Thus, I put encrypted variables into playbooks/vars-secrets.yml and excluded that file from git.

Meanwhile I have learned that idiomatic ansible expects encrypted variables in inventory group variables. Thus, I want to move the playbooks/vars-secrets.yml file to inventories/group_vars/all/vars.yml.

The steps required to achieve this goal are:

- [x] refactor: remove vars.yml (The existing vars.yml can safely be deleted, because there are no variables inside)
- [x] refactor: move vars-secrets.yml to vars.yml (exclude vars.yml from git and move the vars-secrets.yml file to inventories/group_vars/all)
- [x] refactor: playbooks do not need to load vars-secrets.yml explicitly
- [x] fix: test/tart configuration must consider changed secret handling
