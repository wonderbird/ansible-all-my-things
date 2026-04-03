# Active Context

## Current Focus

SDK pre-provisioning tasks T007–T011 are implemented in
`roles/android_studio/tasks/main.yml` and
`roles/android_studio/defaults/main.yml`. Code is pending
user review before committing.

## Recent Changes

- Created `defaults/main.yml` with cmdline-tools build number
  and SHA-256 checksum (T007). User updated values to
  build `14742923`.
- Added 8 tasks to `tasks/main.yml` for SDK pre-provisioning:
  download, create dirs, extract, rename, detect API/build-tools
  versions, install SDK components (T008–T011).
- Marked T007–T011 as complete in tasks.md.

## Next Steps

1. User review of implemented code.
2. Commit the implementation.
3. Validate on Vagrant VM — T012 idempotency + SC-005 wizard test.
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
