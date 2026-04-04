# Progress: feat.flutter.role

## Status: Implementation Complete — Pending Acceptance Test

## What Works

- `roles/flutter/` role fully implemented and committed
- `configure-linux-roles.yml` updated with flutter role entry
- All spec artifacts complete: spec.md, plan.md, research.md,
  data-model.md, quickstart.md, tasks.md
- 10 code review findings all resolved
- Markdownlint passes on all modified files
- `home-folder-files.yml` idempotency fix also committed (F-003)

## What Is Left

| Task | Description |
| --- | --- |
| T013a | **MANUAL**: Run acceptance test on hobbiton (see activeContext.md) |
| T022 | Delete `specs/005-flutter-role/` stale directory before merge |
| — | Open PR: `004-flutter-role` → `main` after acceptance test passes |

## spec.md Task Completion

All 22 tasks (T001–T022) in `specs/004-flutter-role/tasks.md` are marked
`[X]` — but T013a is a manual validation gate, not an automated check.

## Known Issues / Risks

- Acceptance test is manual and untested at time of commit
- `specs/005-flutter-role/` stale directory may still exist (check before
  opening PR)
- Flutter 3.41.6 checksum sourced from research.md — verify against
  official manifest if time has passed:
  `https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json`

## Commits on Branch

```
eecc8ef feat: provision Flutter SDK for Chrome/web development
e8e9e50 docs: flutter role specification, plan, and task breakdown
81b81a8 fix: home-folder-files restore failed when .envrc is absent  ← also on branch
```

## Evolution

- Scope started as "Android Studio SDK extension" → corrected to separate
  `flutter` role with `android_studio` as documented prerequisite
- Install method: tarball chosen over snap/apt per official flutter.dev
  manual install guide
- Version upgrade: operator-driven via `flutter_version` bump (not
  automatic) — deliberate tradeoff for strict idempotency
