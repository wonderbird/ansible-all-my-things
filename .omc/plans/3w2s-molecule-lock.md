# Plan: ansible-all-my-things-3w2s — Molecule test lock file

Status: **pending approval**
Consensus: Planner -> Architect (2 rounds) -> Critic (3 rounds) -> APPROVE

## Problem

All `roles/*/molecule/default/molecule.yml` (7 files) hardcode
`platforms: - name: instance`, so the podman container name `instance` is a
single shared global resource per host — even across separate git worktrees,
since the container namespace is not repo-path-scoped. A concurrent agent
session running `molecule test` for one role can `podman rm -f instance` and
rebuild it mid-converge of another session's `molecule test` for a different
role, corrupting that run. Confirmed twice in the field.

## RALPLAN-DR Summary

**Principles:**
1. Lock must serialize host-wide, not per-worktree — the collision spans
   separate worktrees on the same host (Constitution Principle IV implies:
   solve the actual contended resource, not a proxy for it).
2. Trap-based cleanup, no manual lock removal required in the normal path.
3. Fail loud on a stuck/contended lock, never silently hang forever
   (Constitution Principle XII).
4. Minimal new surface — one wrapper script, no new dependencies
   (Constitution Principle IV, YAGNI).
5. Reuse the same wrapper for both `test-molecule-all.sh` and the
   manually-documented per-role `molecule test` workflow (Constitution
   Principle XI, DRY).

**Decision Drivers:** portability (macOS hosts lack `flock` by default; the
fixed lock path must NOT depend on `$TMPDIR`, which is per-user on macOS and
would silently defeat cross-session serialization on that platform); reuse
across both entry points; survive ungraceful process/VM death (Constitution
"Agent Environment": the VM running the agent is destroyed regularly).

**Options considered:**
- **A. `mkdir`-based lock** (atomic dir-create, POSIX, no extra binary) —
  works identically on macOS + Linux. **Chosen.**
- **B. `flock`-based lock** (kernel advisory lock, native `-w` timeout) —
  not preinstalled on macOS; would add a brew dependency just for this.
  Invalidated: portability driver is a hard blocker.
- **C. Per-worktree/per-role container names** (rename `instance` in each
  `molecule.yml`) — would allow true parallelism instead of serialization.
  Deferred, not rejected: 7-file blast radius, larger scope than this issue.
  Recorded as the escape hatch if host-wide serialization later becomes a
  throughput bottleneck.

## Design (final, post-consensus)

**New script:** `scripts/with-molecule-lock.sh <cmd...>` — generic
command-runner wrapper (lock mechanism is not molecule-specific).

**Lock path:** hardcoded literal `/tmp/ansible-all-my-things-molecule.lock`
— NOT `${TMPDIR:-/tmp}`. `$TMPDIR` is per-user on macOS, which would put
different sessions on different lock paths and silently defeat cross-session
serialization on the very platform the `mkdir`-over-`flock` decision targets.

**Acquire:** `mkdir "$LOCK_DIR" 2>/dev/null` (atomic test-and-set). On
success: write PID + timestamp atomically (`pid.tmp` then `mv` into place —
never a torn write), install `trap 'rm -rf "$LOCK_DIR"' EXIT INT TERM`
**only on this success branch, never before acquire** (so a Ctrl-C during
the wait loop can't delete someone else's lock), run the wrapped command,
preserve its exit code.

**Contention (EEXIST):**
- If `$LOCK_DIR/pid` is missing (narrow window right after another
  process's bare `mkdir`, before it writes the pid file) → treat as
  held-not-stale, sleep+retry. Never attempt reclaim on incomplete info.
- If present, check `kill -0 <pid>`:
  - **PID dead → reclaim immediately.** No age check, ever. Reclaim via
    atomic rename: `mv "$LOCK_DIR" "$LOCK_DIR.stale.$$" 2>/dev/null` (only
    one racing waiter's `mv` can succeed — `rename(2)` on an existing path
    is atomic, the rest get ENOENT and re-loop to re-read current state),
    then `rm -rf` the moved-aside copy, then retry `mkdir`.
  - **PID alive → never reclaim, regardless of how long it has held the
    lock.** Just sleep+retry. This is the load-bearing correctness
    property: liveness is authoritative, age can never override it. (Two
    earlier iterations used an age-based OR-trigger that could reclaim a
    legitimately long-running holder — removed entirely after Critic
    iteration 3 found it deterministically destroys a live holder's lock
    past the ceiling. Dropping age-based reclaim also eliminates a deeper
    TOCTOU the Architect separately flagged: a dead lock's directory is
    now provably stable until some waiter's atomic `mv` wins, since no
    newcomer can `mkdir`-acquire in place while the dead dir still exists.)
- **Overall wait cap:** `MOLECULE_LOCK_MAX_WAIT` env var, default 1800s
  (30min), overridable for fast/deterministic tests. On expiry: fail loud
  (Constitution Principle XII) naming the lock path, the holder PID, and —
  per Critic's residual note — the literal manual cleanup command
  (`rm -rf /tmp/ansible-all-my-things-molecule.lock`) in case the holder
  is a dead-but-PID-recycled orphan that couldn't self-heal (see Residual
  risks below).

**Call sites:**
1. `scripts/test-molecule-all.sh:25` — wrap the existing `molecule test`
   call inside the per-role loop: `"${PROJECT_ROOT}/scripts/with-molecule-lock.sh" molecule test`.
   Placed per-invocation inside the loop (not around the whole script) to
   minimize hold time without widening concurrency — the script's own
   per-role loop is already sequential, so this doesn't change its
   behavior, it only lets an external single-role run interleave between
   roles instead of waiting for the entire multi-role suite.
2. `.claude/skills/molecule-testing/SKILL.md` — add a short "Concurrency"
   subsection near the existing "Running the tests" sections (~lines
   216-221, 239-244) pointing at the wrapper as the canonical entry point
   for manual runs, rather than rewriting the bare `molecule test` example
   in place (avoids a second place that must track the wrapper's
   name/interface — Constitution Principle XI, DRY).
3. CI (`.github/workflows/molecule.yml` calls `test-molecule-all.sh`) needs
   no special-casing: it's a single job with no contention, so the wrapper
   is a no-op there.
4. The issue's acceptance criteria also named CONTRIBUTING.md — confirmed
   zero references to `molecule test`/`test-molecule-all` exist in that
   file (grep, 0 matches). That clause is vacuous; flagging the gap back
   rather than inventing a section to satisfy it verbatim.

## Acceptance Criteria (from issue, all testable)

- Two concurrent `molecule test` invocations on the same host (different
  roles, can be different worktrees) → second one observably waits, does
  not run concurrently with the first.
- Lock is reliably removed after a run, success or failure (trap on the
  success branch) — and self-heals on the next acquisition attempt even
  after an ungraceful kill, via dead-PID reclaim.
- `scripts/test-molecule-all.sh` and the molecule-testing skill doc both
  route through the wrapper (grep both post-change for
  `with-molecule-lock.sh`).
- Verified by manually running two concurrent invocations and observing
  the second wait rather than collide.

## Verification Steps

1. Run `scripts/test-molecule-all.sh` solo — confirm no regression (all
   roles still pass, same as current behavior).
2. Manual concurrency test: two shells, `cd roles/<roleA> &&
   ../../scripts/with-molecule-lock.sh molecule test` and the same for
   `<roleB>` started ~2s apart — confirm the second prints a waiting
   message until the first finishes, then proceeds. Directly satisfies the
   issue's explicit verification requirement.
3. Orphan self-heal: start a wrapped long-running command, `kill -9` the
   wrapper process itself mid-run (bypasses the trap by design), confirm
   the lock is orphaned but the *next* acquisition attempt reclaims it via
   the dead-PID check and proceeds.
4. **Live-holder-never-reclaimed test** (closes the round-2 gap): with
   `MOLECULE_LOCK_MAX_WAIT=5`, start a wrapped long-sleep (alive, well past
   5s) holder, start a second wrapper concurrently, confirm the second
   waits the full 5s and then fails loud — proving a live holder is never
   reclaimed regardless of how long it runs.
5. Two-waiters-racing-on-a-stale-lock test (closes round-1 gap): orphan a
   lock via `kill -9`, then start two wrapped commands concurrently;
   confirm exactly one acquires (inspect timestamps/output for no
   overlapping converge windows) — proving the atomic-`mv` reclaim has
   exactly one winner.

## Residual risks (non-gating, from final Critic approval)

1. **Recycled-PID orphan needs manual cleanup.** If a dead holder's PID
   happens to be recycled by the OS to an unrelated live process before
   any waiter checks it, `kill -0` reads "alive" and the orphan is never
   auto-reclaimed; waiters wait the full cap then fail loud. This is
   safe-by-construction (never destroys live work) — the fail-loud message
   must include the literal `rm -rf /tmp/ansible-all-my-things-molecule.lock`
   command so the operator isn't left guessing.
2. **`.stale.$$` leak on waiter crash.** A waiter killed between a winning
   `mv` and its subsequent `rm -rf` leaks `/tmp/...lock.stale.<pid>`.
   Harmless, accumulates slowly. Accepted, documented — no sweep
   implemented (YAGNI; revisit only if it becomes a real annoyance).
3. **Same-filesystem assumption.** Atomic-rename validity requires
   `$LOCK_DIR` and `.stale.$$` to share a filesystem; both are hardcoded
   under `/tmp`, satisfying this. Add a one-line code comment so a future
   refactor doesn't relocate `.stale` and silently break atomicity.

## ADR

- **Decision:** implement a host-wide `mkdir`-based lock wrapper script at
  a fixed absolute path outside the repo (`/tmp/ansible-all-my-things-molecule.lock`),
  with dead-PID-only reclaim via atomic rename and a fail-loud overall wait
  cap.
- **Drivers:** cross-worktree serialization requirement (the real bug),
  macOS/Linux portability, survive ungraceful VM/process death, never
  destroy a live holder's in-progress test run.
- **Alternatives considered:** `flock` (rejected — not preinstalled on
  macOS); per-worktree lock path (rejected — defeats cross-worktree
  serialization, which is the actual bug); age-based reclaim of long-running
  locks (tried in iteration 2, rejected after Critic found it
  deterministically reclaims legitimately-alive long-running holders);
  per-worktree/per-role container renaming for true parallelism (deferred,
  not rejected — larger blast radius, recorded as a future escape hatch).
- **Why chosen:** the only option satisfying portability, the actual
  cross-worktree collision this issue reports, and the never-destroy-a-live-holder
  invariant, with the simplest mechanism that achieves all three.
- **Consequences:** one new script to maintain; both call sites must go
  through the wrapper (documented via the skill's Concurrency subsection
  and the script's own usage); molecule testing is host-wide sequential
  again (intentional trade — a corrupted mid-converge run is worse than a
  slow one); a recycled-PID orphan needs a manual `rm -rf` in the rare case
  it occurs.
- **Follow-ups:** none beyond the acceptance criteria — no untracked debt.
  Per-worktree container naming remains the documented escape hatch if
  host-wide serialization later becomes a throughput bottleneck.

## Changelog (consensus iterations)

- Iteration 1 (Architect): adjusted lock placement to per-invocation inside
  the loop (not whole-script), replaced skill-doc inlining with a
  Concurrency subsection, dropped the vacuous CONTRIBUTING.md clause,
  recorded the per-worktree-container-name deferral explicitly.
- Iteration 1 (Critic ITERATE): found the original two-step
  check-then-`rm` stale reclaim was racy, and `$TMPDIR` differs per-user on
  macOS, defeating cross-session serialization on that platform.
- Iteration 2: switched lock path to hardcoded `/tmp/...`; replaced the
  racy reclaim with atomic `mv`-based rename; added atomic pid-file writes;
  added the two-waiters-race verification step.
- Iteration 2 (Architect follow-up): flagged a narrower TOCTOU (reclaim
  decision racing against a fresh legitimate holder) and a torn-pid-write
  risk; both patched (re-confirm-after-mv, atomic pid.tmp+mv).
- Iteration 3 (Critic ITERATE): found the age-based OR-trigger could
  reclaim a legitimately alive long-running holder, and the re-confirm
  patch didn't catch it since it re-applied the same age test.
- Iteration 3 (final): removed the age-based reclaim trigger and the
  re-confirm-after-mv step entirely — reclaim is now dead-PID-only, which
  independently eliminates the TOCTOU from the prior round (a dead lock's
  directory cannot be replaced in place by a newcomer). Added
  `MOLECULE_LOCK_MAX_WAIT` override for deterministic testing of the
  fail-loud path. **Critic verdict: APPROVE.**
