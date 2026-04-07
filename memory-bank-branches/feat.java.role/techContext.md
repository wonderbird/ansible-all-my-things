# Tech Context: Java Role

**Primary source of truth**: [`specs/005-java-role/`](../../../../specs/005-java-role/)

## Technologies

| Technology | Detail |
| --- | --- |
| Ansible | 2.19+ |
| Ansible modules | `ansible.builtin.*` only (no community.general needed) |
| sdkman | Installer from `https://get.sdkman.io/download` |
| Eclipse Temurin JDK | Default `21.0.7-tem` (OpenJDK 21 LTS, Adoptium) |
| Target OS | Ubuntu Linux — AMD64 and ARM64 |

## Variables, File-System Entities, and Constraints

See [`specs/005-java-role/data-model.md`](../../../../specs/005-java-role/data-model.md)
for the full variable reference, file-system paths, and idempotency guards.

Technical constraints and assumptions (internet access, no checksum, no
system-wide Java, no Molecule) are in
[`specs/005-java-role/spec.md`](../../../../specs/005-java-role/spec.md)
under the Assumptions section.

## Local Testing and Version Upgrades

Follow [`specs/005-java-role/quickstart.md`](../../../../specs/005-java-role/quickstart.md)
for the step-by-step local test procedure and version override instructions.
