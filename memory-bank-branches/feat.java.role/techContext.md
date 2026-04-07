# Tech Context: Java Role

## Technologies Used

| Technology | Version / Detail |
| --- | --- |
| Ansible | 2.19+ |
| Ansible collection | `ansible.builtin.*` (no community.general needed) |
| sdkman | Latest installer from `https://get.sdkman.io/download` |
| Eclipse Temurin JDK | `21.0.7-tem` (default; OpenJDK 21 LTS, Adoptium) |
| Target OS | Ubuntu Linux (AMD64 + ARM64) |

## Key Variables

| Variable | Default | Location |
| --- | --- | --- |
| `java_sdkman_identifier` | `"21.0.7-tem"` | `roles/java/defaults/main.yml` |
| `desktop_user_names` | (required, no default) | playbook / `group_vars` |

## File-System Entities Created on Target

| Path | Owner | Notes |
| --- | --- | --- |
| `/tmp/sdkman-install.sh` | root | Installer script; not cleaned up; harmless |
| `/home/<user>/.sdkman/` | `<user>` | sdkman installation tree per user |
| `/home/<user>/.sdkman/bin/sdkman-init.sh` | `<user>` | sdkman init guard path |
| `/home/<user>/.sdkman/candidates/java/<id>/` | `<user>` | Temurin JDK per version |
| `/home/<user>/.sdkman/candidates/java/<id>/bin/java` | `<user>` | JDK idempotency guard path |

## Technical Constraints

- Internet access to `https://get.sdkman.io` and sdkman distribution servers
  is required during provisioning.
- No checksum verification of the sdkman installer (sdkman publishes none).
  HTTPS transport integrity is the accepted control (per `android_studio` convention).
- No system-wide Java; `apt` is not used for JDK installation.
- No Molecule; acceptance is manual Vagrant run per `CONTRIBUTING.md`.

## Local Test Setup

```bash
# 1. Isolate the java role in configure-linux-roles.yml
# 2. Run against local VM
ansible-playbook -i inventories/local configure-linux-roles.yml

# 3. Verify as provisioned user
java -version 2>&1 | grep -i temurin

# 4. Re-run to verify idempotency (expect zero changed tasks)
ansible-playbook -i inventories/local configure-linux-roles.yml
```

## Upgrading the Pinned JDK Version

Edit `roles/java/defaults/main.yml` (or override in `host_vars`/`group_vars`):

```yaml
java_sdkman_identifier: "21.0.8-tem"
```

Re-run the playbook. The new version is installed alongside the old one; only
the new version's task runs (old `creates:` guard is still satisfied).
