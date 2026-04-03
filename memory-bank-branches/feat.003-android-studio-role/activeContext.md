# Active Context

## Current Focus

Implement SDK pre-provisioning (tasks T007–T012 in
`specs/003-android-studio-role/tasks.md`). All blockers
resolved — see research.md Decisions 4–6 and plan.md SDK
Design for the agreed approach.

## Next Steps

1. Implement T007–T012 (T010a included) in order.
2. Validate idempotency (T012 / quickstart.md).
3. Run SC-005 manual wizard test (wizard <= 30 s).
4. Open PR.

## Open Issues — Address During Implementation

- **M3**: Document `become_user` inheritance in plan.md
  (play sets `become: true`; per-user tasks must not repeat
  it).
- **M4**: Tighten US1 scenario 2 / US2 overlap in spec.md.
- **L1–L3**: Minor spec wording fixes (see tasks.md notes).

## Known Bug (unrelated to android_studio)

`PLAY [Restore home folder files]` fails with
`file (/home/galadriel/.envrc) is absent, cannot continue`
when `.envrc` does not exist on the target VM. Workaround:
create `.envrc` manually before running the full playbook.
