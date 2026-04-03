# System Patterns

## Role layout

Three files: `defaults/main.yml`, `meta/main.yml`,
`tasks/main.yml`. Mirrors `google_chrome` role where
applicable. See `specs/003-android-studio-role/plan.md`
for exact fields and code conventions.

## configure-linux-roles.yml

Role entry tagged `not-supported-on-vagrant-arm64` at
role-entry level only. Roles sorted alphabetically.

## Research decisions

`specs/003-android-studio-role/research.md` — six decisions
covering snap module, layout, idempotency, SDK automation
approach, cmdline-tools versioning, and per-user provisioning.
