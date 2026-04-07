# Product Context: Java Role

## Why This Feature Exists

Developer workstations provisioned by this project need Java. Using sdkman
as the installation vehicle gives each developer self-service control to
install, switch, and update JDK versions without re-running the playbook.
Pinning a specific Temurin identifier in `defaults/main.yml` ensures
reproducible builds across the team.

## Problems It Solves

- Eliminates manual `apt install` or per-developer JDK setup steps.
- Ensures the same Temurin LTS version is installed for every user
  listed in `desktop_user_names`, regardless of who runs the playbook.
- Leverages sdkman so developers can self-manage JDK versions after
  initial provisioning (without re-running the playbook).

## How It Works

The role runs three tasks sequentially for each user:

1. Download the sdkman installer to `/tmp/sdkman-install.sh` as root
   (no `become_user`; `/tmp` is world-readable).
2. Execute the installer as `{{ item }}` — creates `~/.sdkman/`.
3. Source `sdkman-init.sh` and run `sdk install java <identifier>` as
   `{{ item }}` — creates the version-specific JDK tree.

All three tasks are idempotent: re-running the playbook skips already-done
steps without changing any state.

## User Experience Goals

- A developer can open any terminal after provisioning and run `java` without
  any manual steps.
- An operator can upgrade the pinned JDK by changing one line in
  `defaults/main.yml` and re-running the playbook.
- The role is invisible to the developer after initial provisioning; sdkman
  handles PATH setup automatically via `~/.bashrc` and `~/.profile`.
