# Active Context: feat.flutter.role

## Current State

Implementation is **complete and committed**. Branch `004-flutter-role` is
ahead of `main` by 2 commits:

- `eecc8ef` — `feat: provision Flutter SDK for Chrome/web development`
  (role implementation + all code review fixes)
- `e8e9e50` — `docs: flutter role specification, plan, and task breakdown`

## What Was Done This Session

1. Spec created: `specs/004-flutter-role/spec.md` (speckit.specify)
2. Spec clarified: 5 questions answered, status → Clarified (speckit.clarify)
3. Plan created: plan.md, research.md, data-model.md, quickstart.md
   (speckit.plan)
4. Tasks generated: tasks.md — 22 tasks, 7 phases (speckit.tasks)
5. Consistency analysis: 14 findings, 12 auto-resolved, 2 user decisions
   (speckit.analyze)
6. Implementation: all role files created, configure-linux-roles.yml updated
   (speckit.implement)
7. Code review: 10 findings across CRITICAL/HIGH/MEDIUM/LOW
8. All findings fixed and committed

## Next Immediate Action

**Run acceptance test on `hobbiton`:**

```bash
ansible-playbook configure-linux.yml
# then on hobbiton:
flutter doctor       # Chrome/web target must show no errors
flutter build web    # must succeed on a cloned Flutter project
```

After acceptance test passes → open PR to merge `004-flutter-role` into
`main`.

## Open Decisions / Risks

- Acceptance test not yet run on real hardware — T013a is the manual gate
- `specs/005-flutter-role/` stale directory: T022 in tasks.md requires
  deleting it before merge (check: `ls specs/005-flutter-role/` — if
  present, run `rm -rf specs/005-flutter-role/` and commit)
- Flutter 3.41.6 is pinned at time of implementation; check if a newer
  stable release is available before provisioning if significant time
  has passed

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
