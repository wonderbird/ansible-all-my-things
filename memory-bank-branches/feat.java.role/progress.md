# Progress: Java Role

## What Works

All role files are implemented and committed:

- `roles/java/defaults/main.yml` — variable default in place
- `roles/java/meta/main.yml` — galaxy_info present
- `roles/java/tasks/main.yml` — three-task per-user sequence, all idempotency
  guards correct (version-specific `creates:` path for JDK task)
- `roles/java/DESIGN.md` — non-obvious decisions documented
- `configure-linux-roles.yml` — `java` role integrated at line 22

Code has been reviewed; no outstanding implementation issues.

## What Is Left to Build / Verify

Acceptance testing (manual Vagrant runs) — none of the validation tasks have
been executed yet:

| Task | Criterion | Status |
| --- | --- | --- |
| T008 | SC-001: `java -version` exits 0 and contains "Temurin" (AMD64) | Not run |
| T010 | SC-002: sdkman installer skipped (`ok`) on second run | Not run |
| T012 | SC-004: version-override installs new JDK alongside old | Not run |
| T014 | SC-002: full second-run zero `changed` tasks | Not run |
| T015 | SC-003: ARM64 provisioning succeeds | Not run |
| T016 | Markdownlint clean on all modified `.md` files | Not run |

## Current Status

**Implementation: COMPLETE** | **Acceptance Testing: PENDING**

Branch `005-java-role` is ahead of `main` by two commits:

- `8cdb0db feat: provision sdkman and Temurin JDK per user via new java role`
- `8bea99a docs: add spec, plan and tasks for java role`

## Known Issues

None. No implementation defects identified during code review.

## Evolution of Decisions

| Decision | Outcome |
| --- | --- |
| sdkman installer URL | Using `https://get.sdkman.io/download` (direct download endpoint, not the redirect) |
| Idempotency guard path | Version-specific path chosen (not `current/`) per spec FR-005 |
| PATH modification | Delegated to sdkman installer (no `blockinfile` task needed) |
| ARM64 support | No architecture branching needed; sdkman detects arch at runtime |
| No Molecule | Accepted; SC-005 satisfied by manual Vagrant run per `CONTRIBUTING.md` |
| `SDKMAN_DIR` env var | Set on the sdkman install task to ensure correct target directory |
