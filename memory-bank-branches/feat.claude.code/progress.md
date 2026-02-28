# Progress

## Done

- [x] Code review of `mob/claude-code` branch completed
- [x] Review finding 2 resolved: `claude_code` added to `configure-linux-roles.yml`, test playbook removed
- [x] Review finding 3 resolved: `blockinfile` markers made role-specific across all roles
- [x] Review finding 4 resolved: `meta/main.yml` descriptions fixed across all roles
- [x] Feature concept written (`docs/features/claude-code/concept.md`)
- [x] PRD written (`docs/features/claude-code/prd.md`)
- [x] PRD Stage 1: binary checksum verification implemented
- [x] Code review of binary integrity verification implementation
- [x] F3 resolved: `assert` task guards against unsupported `ansible_architecture`
- [x] F4 resolved: `when` condition guards `item.stat.checksum` with `not item.stat.exists`
- [x] F8 resolved: `return_content: true` (YAML 1.2 boolean)
- [x] F10 resolved: `validate_certs: true` explicit on all `uri` tasks
- [x] Manifest now fetched before installer runs — system unmodified on fetch failure
- [x] Flat task structure — `block`/`rescue` removed
- [x] Acceptance tests written (`docs/features/claude-code/acceptance-tests.feature`)
- [x] Technical debt register created (`docs/architecture/technical_debt.md`) with TD-001

## In progress

- [ ] PRD Stage 2: test, debug, and safety checks
