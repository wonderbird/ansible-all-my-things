# Session Insights: Flow First Look, 2026-11-20

Insights from the planning, review and execution of the flow first look
(epic `tklf`, task `tklf.1`).

- **Evidence:** VERIFIED means measured in the session. INFERRED means
  reasoned.
- **Home:** where an insight could be kept. These are proposals to decide
  together with the flow consultant.

## A. What the Data Says About the Work

| # | Insight | Evidence | Proposed home |
| --- | --- | --- | --- |
| A1 | Rework is about 17.5 % of delivered non-automated items. It is stable, with no signal, and lands almost entirely on machine work: 22 machines vs 3 lab. Rework on the agent rules is rare. | VERIFIED (p-chart, 5 readable months) | Already in `tklf.1` notes |
| A2 | About 11 of the owner's 39 delivered items are version bumps by hand (`deps:` and similar), and the pattern undercounts. This is recurring maintenance demand that costs the owner's attention. | VERIFIED count; INFERRED undercount | Epic Options: "automate version bumps the owner still does by hand" |
| A3 | Agents commit under the owner's git identity: 135 of 174 `Stefan Boos` commits in agent PRs carry a Claude trailer. The owner also lets agents write commit messages in interactive sessions. Git authorship cannot separate human work from agent work. | VERIFIED | Already in notes; flow-consultant `data-sources.md` (trap) |
| A4 | The owner's real question is the attention pattern: which work runs mostly automated and needs one condensed block, and which needs the owner present for many small steps. | Owner, 2026-11-20 | Already an epic option, chosen as the next topic |
| A5 | Transcripts do not survive VM rebuilds: only 9 exist, from the last 5 days. Any attention metric needs a logger first. | VERIFIED | Already in the epic option; flow-consultant `data-sources.md` (coverage) |
| A6 | Delivery changed at 2026-04, from direct commits on `main` to PRs, probably together with agent adoption. History before that date is not comparable. | VERIFIED (monthly table) | Epic context; flow-consultant `data-sources.md` |
| A7 | 36 direct commits reached `main` after 2026-04 that are neither tracker exports nor `chore`, many `ai:` and `deps:`. The constitution allows only tracker-export commits without a branch and PR. The gap between policy and practice is unexamined. | VERIFIED count; INFERRED gap | Epic Options, or a question for the owner |
| A8 | GitHub `MERGED` does not mean delivered. #94 was closed as merged when #95 took its commit, and #113 merged into a feature branch (a stacked PR). | VERIFIED | flow-consultant `data-sources.md` (trap) |
| A9 | `memory-bank*/` held planning and documentation for machine work, so it counts as machines. `.github/`, `scripts/` and `CONTRIBUTING.md` stay judgement calls on the lab/machines boundary. | Owner ruling; VERIFIED counts | The durable-script option, if pulled |

## B. How to Measure (Method)

| # | Insight | Evidence | Proposed home |
| --- | --- | --- | --- |
| B1 | Counts show volume, not mix. With monthly n between 3 and 39, chart shares with n printed, and flag months with n < 5. | VERIFIED volume swing | flow-consultant `metrics.md` (reading guidance) |
| B2 | "Beyond the earlier range" fires by chance with probability 2/(k+1). Use p-charts for shares. With about 7 months the run rule cannot fire, so most answers read "no signal", and the value lies in the levels and the composition. | Consultant self-correction, round 2 | flow-consultant `SKILL.md` step 5 / `metrics.md` |
| B3 | Fix the bases and the decision rules before the look, so they are not chosen after seeing the data. | Consultant round 2 | flow-consultant `SKILL.md` step 6 (design fields) |
| B4 | "Wants X to shrink" is a target. Name a balancing metric (here: the agent rework share) and count every channel, here PRs plus direct commits. | Consultant round 1 | Already a skill ground rule; reinforced by example |
| B5 | For a one-off look, reconciling against independently counted baselines plus a stratified spot-check catches most faults more cheaply than many invariants and planted cases. A circular reconciliation, where the script is checked against its own numbers, proves nothing. | Architect, Critic and consultant | flow-consultant `SKILL.md` (one-increment verification) |

## C. How We Worked (Lab Insights)

| # | Insight | Evidence | Proposed home |
| --- | --- | --- | --- |
| C1 | **Rigour drift.** Each review round added rigour (4 invariants, 26 planted cases, more charts) and pushed the throwaway look from about 2 h to about 3.5 h. Only the owner's explicit "minimal yet helpful" lens cut it back to about 2 h. Reviewers optimise correctness, not cost. | Session history | Review prompts and the flow-consultant skill: state "the cheapest thing that cannot mislead" up front |
| C2 | **Complementary reviewer lenses.** Architect and Critic found a false premise (#94/#113) and a circular verification. The flow consultant found noise read as signal and the target-gaming risk. Neither group would have found the other's issues. | Session history | AGENTS.md or a workflow note: which plans need which lens |
| C3 | **The session itself shows the owner-presence pattern.** It needed about 15 owner decisions and approvals, several clarifications and 4 review loops. It is an instance of "work that needs the owner present for many small steps". | INFERRED from the session | Input for the attention-pattern consultation |
| C4 | **Decide the outcome's home at plan time.** The plan made everything a throwaway in `/tmp`. Only at the end did it become clear that the useful page and scripts would be lost. | Session history | flow-consultant `SKILL.md` step 6: "where the look's evidence lives" |
| C5 | **The owner wants a page that explains itself**, to reread in a month and to show friends: a short intro and plain-language explanations of verdicts and tables. | Owner feedback | flow-consultant `metrics.md` / report template guidance |
| C6 | **Late and duplicated teammate messages** (idle notifications repeating earlier results) cost reading time without new information. | Session history | Optional: note on teammate use |

## D. Tool Friction

| # | Insight | Proposed home |
| --- | --- | --- |
| D1 | Plain `bd show` drops backticks and reflows text. Read raw text with `bd show <id> --json`, which returns a list (`.[0].description`). | `bd remember` or AGENTS.md (Beads section) |
| D2 | `bd update --claim` on an issue the same user already holds did not renew an expired lease. | `bd remember` |
| D3 | OMC ralph wrote no PRD scaffold, and the architect's approval did not set `architectVerified`, so closeout refused. Both were fixed by hand. | Already in `.omc/notepads/ralph/problems.md` |
| D4 | `python3 -I` breaks sibling imports in your own scripts. | Already in the notepad |

## E. Collaboration in This Session

| Fact | Value | Evidence |
| --- | --- | --- |
| Duration | About 2 h 46 min wall-clock time, from 18:52Z to 21:38Z (Claude Code `total_duration_ms` = 9,974,986). The model worked for about 56 min of it (`total_api_duration_ms` = 3,375,588). The session was not restarted: one `/clear` at the start and one session ID throughout. An earlier status-line reading of 1 h 40 min matches neither measure. | VERIFIED from the transcript and the status-line input |
| Split of the wall-clock time | Planning, interview and reviews: 18:52Z to 20:24Z, about 1 h 32 min. Execution and follow-up: 20:24Z onwards. | VERIFIED from session state |
| Structured questions to the owner | About 24. 7 were interview questions: precedence, cutoff, authors, author view, chart medium, path rule, git identity. 4 were rejected so the owner could clarify first. Several answers were counter-questions that changed the plan: the cutoff, the chart technology, the minimality lens, the artifact home. | INFERRED count from the session |
| Review passes | About 17 in total: Architect 6 (4 plan iterations, the cuts, the execution check), Critic 5 (4 plan iterations, the cuts), flow consultant 6 (3 rounds, minimality, the check of the slimmed plan, the decision to keep the scripts). | INFERRED count from the session |
| Plan versions | 4 consensus iterations, 3 consultant rounds, 1 minimality cut, 1 round of conditions. The estimate went from about 2 h to 3.5 h and back to about 2 h. | VERIFIED from plan history |
| Execution | Ralph ran 6 stories. The owner was involved again for the identity question, the decision and the artifact home. | VERIFIED |

Pattern: the owner was needed for many small decisions spread across the
whole session, not in one condensed block. This is the "presence" pattern
that the attention-pattern option wants to measure (INFERRED).

## Open Point

The flow-consultant skill is linked from the skill manager (symlink
`.claude/skills/flow-consultant`, registered in `.skills.json`), so it is not
lost on a VM rebuild. Its link is missing from the skill-manager list in
`.gitignore`, so it shows up in `git status` as untracked.
