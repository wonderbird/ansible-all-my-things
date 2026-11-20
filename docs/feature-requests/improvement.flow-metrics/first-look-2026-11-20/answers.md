## Answers

Under the fixed reading rules most trend answers read "no signal". That
does not mean "nothing found": the value of this look lies in the levels
(p̄) and in the composition, namely the version bumps inside manual work and
where rework lands.

Data as of snapshot `0455604` (2026-11-20), from 2026-04-01. Counts are
VERIFIED: they come from the script and reconcile with independent git and
gh baselines. Interpretations are marked INFERRED.

1. **Where did 2026-05 to 2026-10 go? (levels only)** Of 117 delivered
   non-automated items, 69 % were machines (81), 15 % lab (18) and 15 %
   rework (18) (VERIFIED). Besides these: 7 Dependabot PRs and 13 discarded
   PRs (VERIFIED). Version bumps, 2026-04 to 2026-11: 11 by the owner by
   hand and 3 by the agent (VERIFIED, plan's title pattern). The pattern
   misses bump titles such as "feat: update beads rust, …", so the real
   number is higher (INFERRED).
2. **Is rework growing?** No signal (VERIFIED).
   - p̄ = 17.5 %: 22 of 126 delivered non-automated items over the
     readable months 2026-04, 05, 06, 09 and 10. No readable month lies
     outside its p-chart limits.
   - With 5 readable months (Jul and Aug have n < 5), the 6-in-a-row rule
     could not fire.
   - Rework lands mostly on machines: 16 machines vs 2 lab for 2026-05 to
     2026-10, and 22 vs 3 for 2026-04 to 2026-11 (VERIFIED).
   - Rework on the agent rules is rare (INFERRED from that split).
3. **Does the path rule hold?** Mostly (INFERRED from the diagnostics).
   - 8 items are mixed (winning share below 2/3) and 5 are neutral-only
     (VERIFIED).
   - Top paths that fell to machines by default: `roles/` 86,
     `playbooks/` 56, `.github/` 22, `scripts/` 16, `CONTRIBUTING.md` 13,
     `inventories/` 12 (VERIFIED). The real judgement calls are `.github/`,
     `scripts/` and `CONTRIBUTING.md`.
   - The spot-check found #32 ("feat: flutter is provided via a role")
     counted as lab, 7:6, because memory-bank notes outvoted the role
     files. The owner ruled on 2026-11-20 that `memory-bank*/` is machines
     work. After the rerun, #32 is machines (VERIFIED).
4. **Is the owner's share of opened or committed work shrinking?** No
   signal (VERIFIED). The question is read as "who opened or committed",
   not "who did the work": git cannot separate hand work from interactive
   agent work (see the caveat below).
   - Manual share p̄ = 27.8 %: 35 of 126 delivered non-automated items
     over the readable months 2026-04, 05, 06, 09 and 10. With 5 readable
     months, the 6-in-a-row rule could not fire.
   - Across 2026-04 to 2026-11 there are 39 manual items: 15 PRs and 24
     direct commits.
   - Manual PRs alone per month (Apr to Nov): 3, 0, 4, 0, 1, 1, 3, 3.
     Manual direct commits: 2, 6, 4, 0, 0, 6, 6, 0.
   - Balancing metric: the rework share of agent items, p̄ = 18.7 % (17 of
     91 agent items over the readable months), no signal (VERIFIED).
   - 11 of the 39 manual items are version bumps by the plan's title
     pattern (VERIFIED). The true number is higher (INFERRED, see 1).
   - Caveat, opener vs commit author:
     - 6 PRs opened by the owner contain agent commits: #159, #114, #80,
       #40 and #29 contain only agent commits, and #28 is mixed.
     - The other way round, 23 agent-opened PRs carry 174 `Stefan Boos`
       commits, and 14 of these PRs were merged in 2026-06 (VERIFIED).
     - Ten contain only `Stefan Boos` commits: #31, #84, #85, #87, #88,
       #89, #90, #91, #93 and #95 (VERIFIED).
     - Message shapes (VERIFIED):
       - Of those 174 commits, 135 carry a Claude co-author trailer, 3
         have a body without one, and 36 are a headline only.
       - Of the owner's 24 direct commits, 17 are a headline only, 6 have
         a body and 1 carries a Claude trailer.
     - So agents commit under the owner's identity, and the owner works
       interactively with agents that write the commit messages
       (owner, 2026-11-20). Neither the git identity nor the message
       shape separates hand work from agent work.
     - The owner decided to keep the opener rule and to record this
       caveat. Measuring attention from transcripts is added as an epic
       option.

**Caveats.** A count is not effort. A rework item is a candidate, since
fixes also repair external breakage. Discarded is a lower bound (closed
PRs only).

### Durable-Script Decision

The owner decided on 2026-11-20: not yet, attention first. The category
chart (machines, lab, rework) proved useful, above all the
rework ratio, and also the lab-to-machines ratio. The author chart did not,
because git cannot separate the owner's work from agent work. The owner's
bigger question is the attention pattern: which work runs mostly automated
and needs only one condensed block of attention, and which work needs the
owner present for many small steps. The next consultation picks that
metric. The durable script for the category chart stays an epic option,
marked as proven useful.
