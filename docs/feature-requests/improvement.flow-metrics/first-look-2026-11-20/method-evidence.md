## Method evidence

- **Snapshot:** `main` = `origin/main` = `0455604815252edec7fa4a0c2f33cb902f0c4d38`,
  committed 2026-11-20T18:31:23+01:00. Window: 2026-04-01 to the snapshot;
  2026-11 is partial.
- **Cutoff reason:** before 2026-04 most work landed as direct commits on
  main (2026-01: 45 direct, 1 PR), so PR counts misrepresent work. The break
  probably marks agent adoption.
- **Rules:**
  - **Decision 1:** rework wins over the path vote.
  - **Decision 2:** cutoff 2026-04-01.
  - **Decision 3:** direct commits count like PRs; `.beads/`-only and
    `chore` commits are excluded.
  - **Decision 4, author map:**
    - agent: `eudicy`, `Eudicy`, `galadriel`;
    - manual: `wonderbird`, `stefanboos`, `Stefan Boos`;
    - automated: `app/dependabot`, `dependabot[bot]`.
  - **Decision 5:** two share charts.
  - **Decision 6:** stdlib Python and Chart.js 4.4.1.
  - **Decision 7, path rule:**
    - lab: `.claude/`, `.specify/`, `.clinerules/`, `.cursor/`, `.omc/`,
      `AGENTS.md`, `CLAUDE.md`, `.codex/`, `.agents/`,
      `.rtk/`, `.skills.json`;
    - neutral: `docs/`, `specs/`, `README.md`, `CHANGELOG.md`,
      `.gitignore`, `.beads/`;
    - machines: everything else, including `memory-bank*/` (owner ruling
      2026-11-20, after the first run).
  - **D1:** #94 is absorbed into #95 and #113 into #112.
  - **D2:** the rework pattern is `^(fix|bug|revert)\b`.
  - **D3:** `beads-backup.jsonl` and `beads_export.jsonl` are neutral, and
    `skills-lock.json` is lab.
  - **D4:** "manual" is decided by the PR opener.
  - **D5:** five author segments; question 4 counts both channels and is
    balanced by the agent rework share.
  - **D6:** the chore pattern applies to direct commits only.
  - **D7:** 2026-11 is partial.
  - **D8:** p-charts on fixed bases over the readable months 2026-04 to
    2026-10 with n ≥ 5.
  - **D9:** discarded is a lower bound.
- **Reconciliation (all PASS):**

  | Check | Script | Baseline |
  | --- | --- | --- |
  | delivered PRs + absorbed | 126 | 126 merged PRs |
  | delivered PRs | 124 | 124 merge commits |
  | delivered direct commits | 36 | 36 (re-derived one-liner) |
  | discarded + closed Dependabot | 14 + 2 | 16 closed PRs |

  A deliberate break (dropping direct commit `e43c6d1`) failed with
  35 vs 36.
- **Planted cases:** 12 cases, 27 checks across both directions, all PASS
  (`check_cases.py`).
- **Unproven guards:** the merge-subject assertion and the `gh` limit
  assertion. Neither has a planted case; this script is never merged.
- **Spot-check:** seed 20261120, 10 items, stratified (one per category, 2
  direct commits, 3 random), plus 1 discarded PR. All match the hand
  classification.
- **Fix-like words not at the start of the title, not counted as rework:**
  #66, #69, #92, #94, #123.
