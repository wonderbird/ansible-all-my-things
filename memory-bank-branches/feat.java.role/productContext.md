# Product Context: Java Role

**Primary source of truth**: [`specs/005-java-role/spec.md`](../../../../specs/005-java-role/spec.md)

## Why This Feature Exists

Developer workstations provisioned by this project need Java. Using sdkman
as the installation vehicle gives each developer self-service control to
install, switch, and update JDK versions without re-running the playbook.
Pinning a specific Temurin identifier in `defaults/main.yml` ensures
reproducible builds across the team.

## User Stories and Acceptance Scenarios

See [`specs/005-java-role/spec.md`](../../../../specs/005-java-role/spec.md)
— User Stories 1–3 with acceptance scenarios and success criteria.

## How It Works

See the task sequence and idempotency model in
[`specs/005-java-role/data-model.md`](../../../../specs/005-java-role/data-model.md).
