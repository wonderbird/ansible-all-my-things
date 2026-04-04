# Progress: feat.flutter.role

## Status: Acceptance Test Passed — Ready for PR

## What Works

- `roles/flutter/` role fully implemented and committed
- `configure-linux-roles.yml` updated with flutter role entry
- All spec artifacts complete: spec.md, plan.md, research.md,
  data-model.md, quickstart.md, tasks.md
- 10 code review findings all resolved
- Markdownlint passes on all modified files
- `home-folder-files.yml` idempotency fix also committed (F-003)
- Acceptance test on `hobbiton` passed:
  - `flutter doctor`: Chrome/web target `[✓]`
  - `flutter build web`: `✓ Built build/web`
  - Second run: `changed=0` for all flutter tasks

## What Is Left

| Task | Description |
| --- | --- |
| — | Open PR: `004-flutter-role` → `main` (user review pending) |

## spec.md Task Completion

All 22 tasks (T001–T022) in `specs/004-flutter-role/tasks.md` are marked
`[X]`. T013a (manual validation gate) is now verified on real hardware.

## Known Issues / Risks

- None. All acceptance criteria verified on `hobbiton`.

## Commits on Branch

```
90e64d1 fix: flutter role re-installed SDK on every playbook run
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
- Idempotency guard: originally used `flutter/version` (expected SDK file);
  fixed to use Ansible-written stamp file after discovering Flutter 3.x
  does not ship that file
