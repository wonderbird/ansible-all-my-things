# Progress

## Done

- Feature spec (`specs/003-android-studio-role/spec.md`)
- Implementation plan (`specs/003-android-studio-role/plan.md`)
- Research (`specs/003-android-studio-role/research.md`)
- Quickstart test guide (`specs/003-android-studio-role/quickstart.md`)
- `/speckit.tasks` — `specs/003-android-studio-role/tasks.md` generated
- `/speckit.analyze` — cross-artefact consistency check and review complete
- Spec artefact review — user findings applied: `community.general.snap` adopted,
  all playbook commands scoped to `--limit hobbiton`
- `/speckit.implement` — all tasks T001–T006 implemented and committed (`6330042`)
  - `roles/android_studio/meta/main.yml` created
  - `roles/android_studio/tasks/main.yml` created
  - `configure-linux-roles.yml` updated (android_studio entry + FR-008 comment)
  - `requirements.yml` updated (`community.general >= 1.0.0`)
  - `docs/architecture/technical-debt/technical-debt.md` TD-003 updated
- User code review complete — two fixes applied and amended into commit:
  - `community.general` version constraint added to `requirements.yml`
  - TD-003 updated to mention snapd automatic background refresh

## Remaining

- [x] Install test — `snap list android-studio` returned rev 209, `latest/stable`, `snapcrafters✪`
- [x] Idempotency test — android_studio task reported `ok` on second full playbook run
- [x] ARM64 skip test — android_studio tasks absent from output (skipped by tag); playbook failure was unrelated `.envrc` bug
- [x] configure-linux-roles.yml restored — roles sorted alphabetically (android_studio, claude_code, google_chrome)
- [ ] Run markdownlint on `specs/003-android-studio-role/spec.md` once markdownlint is available in the shell PATH used by Claude Code (skipped this session — tool not found)
- [ ] SDK automation: extend role to install Android SDK for all desktop users (spec updated; plan next)
- [ ] Open PR (after SDK automation is implemented and validated)

## Known Issues / Decisions

- `community.general.snap` chosen over `ansible.builtin.command`; idempotency
  is native to the module (no `creates:` guard needed)
- `community.general >= 1.0.0` added to `requirements.yml`
- Version pinning deferred; fresh machines at different times may get
  different snap revisions (accepted technical debt — TD-003)
- snapd auto-refresh can change the installed version at any time without
  a playbook run (noted in TD-003)
- ARM64 skip relies on `--skip-tags not-supported-on-vagrant-arm64`
- All test playbook commands are scoped to `--limit hobbiton`
