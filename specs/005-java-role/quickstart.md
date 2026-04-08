<!-- SPDX-License-Identifier: MIT-0 -->

# Quickstart: Java Role (sdkman + Temurin JDK)

**Branch**: `005-java-role` | **Date**: 2026-04-07

This guide covers the minimum steps to implement, test, and verify the `java`
role locally.

## Prerequisites

- Local test VM provisioned per `CONTRIBUTING.md` (Vagrant + Docker or
  Vagrant + Tart).
- `desktop_user_names` configured in your inventory or `group_vars`.
- Internet access from the VM to `https://get.sdkman.io` and to the sdkman
  distribution servers (for Temurin JDK download).

## Role File Checklist

Create the following files under `roles/java/`:

```text
roles/java/
├── defaults/main.yml    # java_sdkman_identifier: "21.0.7-tem"
├── meta/main.yml        # galaxy_info block
├── tasks/main.yml       # Three-task per-user loop
└── DESIGN.md            # Non-obvious design decisions
```

Every YAML file must begin with `#SPDX-License-Identifier: MIT-0`.

## Local Test Procedure

1. Activate only the `java` role in `configure-linux-roles.yml` (comment out
   all other roles).
2. Run the playbook against the local VM:

   ```bash
   ansible-playbook -i inventories/local configure-linux-roles.yml
   ```

3. Verify the acceptance criteria:

   ```bash
   # Log in as a provisioned user (or use ansible -m shell)
   java -version 2>&1 | grep -i temurin
   ```

   Expected: output contains "Temurin" and command exits 0.

4. Run the playbook a second time and confirm zero `changed` tasks (idempotency
   check, SC-002):

   ```bash
   ansible-playbook -i inventories/local configure-linux-roles.yml
   ```

## Acceptance Criteria Summary

| Criterion | How to verify |
| --------- | ------------- |
| SC-001: `java -version` succeeds and contains "Temurin" | Run `java -version` as each provisioned user |
| SC-002: Zero changed tasks on second run | Re-run playbook; inspect Ansible output |
| SC-003: Works on AMD64 and ARM64 | Run against both Vagrant targets |
| SC-004: JDK version matches `java_sdkman_identifier` | `java -version` output matches pinned identifier |
| SC-005: Role testable in isolation | Comment out other roles; playbook runs without error |

## Overriding the Default JDK Version

To install a different Temurin LTS patch, override `java_sdkman_identifier` in
your inventory:

```yaml
# group_vars/linux.yml or host_vars/<hostname>.yml
java_sdkman_identifier: "21.0.8-tem"
```

Then re-run the playbook. A new JDK version is installed alongside the old one;
the `creates:` guard for the old path is still satisfied, so the old-version
task is skipped.
