# Tech Context

- **Language**: YAML, Ansible 2.19+
- **Collections**: None new — `ansible.builtin.command` only
- **Target OS**: Ubuntu Linux, AMD64 only
- **snapd**: Pre-installed (standard Ubuntu); role does NOT set it up
- **Internet**: Required on first run (snap downloads from Snap Store)
- **Testing**: Manual via `ansible-playbook` on AMD64 Vagrant VM
  (see `specs/003-android-studio-role/quickstart.md`)
- **Lint**: markdownlint must pass on all spec artefacts
