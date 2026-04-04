# Active Context: feat.flutter.role

## Current State

Implementation is **complete and acceptance-tested**. Branch `004-flutter-role`
is ahead of `main` by 4 commits:

- `90e64d1` — `fix: flutter role re-installed SDK on every playbook run`
  (idempotency bug found during acceptance test, fixed)
- `eecc8ef` — `feat: provision Flutter SDK for Chrome/web development`
  (role implementation + all code review fixes)
- `e8e9e50` — `docs: flutter role specification, plan, and task breakdown`
- `81b81a8` — `fix: home-folder-files restore failed when .envrc is absent`

## What Was Done This Session

1. Ran acceptance test on `hobbiton` — all criteria passed except AC#3
2. Diagnosed idempotency failure: Flutter 3.41.6 ships no `version` file at
   the SDK root; the guard always found `stat.exists: False`
3. Fixed: replaced the missing `flutter/version` path with a stamp file
   (`flutter/.ansible_installed_version`) written by Ansible after extraction
4. Verified fix: second run returned `changed=0` for all flutter tasks
5. Committed fix as `90e64d1`
6. Awaiting user review before opening PR

## Next Immediate Action

**Open PR**: `004-flutter-role` → `main`

After user approves the commit, open a pull request.

## Open Decisions / Risks

- None remaining. All acceptance criteria pass.

## Session Learnings (for next agent)

- `speckit.specify` auto-increments the spec directory number from the
  branch name. If the branch already exists (e.g. `004-flutter-role`), the
  script may still create `specs/005-flutter-role/`. Always verify the
  correct spec dir and delete stale ones before merging.
- `speckit.plan` adds a "Recent Changes" section to `CLAUDE.md` — this
  violates rule 330 (no version history in docs). Remove it before commit.
- The correct speckit workflow order is:
  `specify → clarify → plan → tasks → analyze → implement`
  NOT `specify → clarify → analyze` (analyze needs tasks to be generated
  first).
- `ansible.builtin.systemd daemon_reload: true` always reports `changed`.
  Always add `changed_when: false` to daemon-reload tasks.
- `get_url` with a checksum is idempotent by design. Never loop it over
  users for a version-specific archive — download once to `/tmp/`.
- Flutter 3.x does NOT ship a `version` file at the SDK root. Use a stamp
  file (`flutter/.ansible_installed_version`) written by Ansible instead.

## Key Decisions Made

| Decision | Choice | Rationale |
| --- | --- | --- |
| Install method | Official tarball from flutter.dev | Per official manual install guide |
| Install path | `/home/{{ item }}/flutter` per user | Consistent with android_studio pattern |
| PATH setup | `blockinfile` in `~/.bashrc` | Consistent with claude_code role |
| Upgrade trigger | Bump `flutter_version` variable | Operator-driven; strict idempotency |
| Checksum | `flutter_sha256` in defaults/main.yml | Mirrors android_studio pattern |
| Role dependency | README.md only; meta: `dependencies: []` | Avoids tag-filtering breakage |
| apt packages | clang, cmake, ninja-build, pkg-config, libgtk-3-dev, mesa-utils | Proven from manual installs |
| Idempotency guard | Stamp file `.ansible_installed_version` | Flutter 3.x has no `version` file at SDK root |
