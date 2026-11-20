# Verification record (flow first look)

## Planted cases

```text
PASS case 1: fix(x) on .claude/ is rework
PASS case 1: contrast feat(x) on .claude/ is lab
PASS case 2: Dependabot fix: is automated
PASS case 2: contrast agent fix: is rework
PASS case 3: .claude/ + .beads/ is lab
PASS case 3: contrast .claude/ + roles/ is not lab
PASS case 4: 1 lab + 1 roles is machines, mixed
PASS case 4: contrast 2 lab + 1 roles is lab, not mixed
PASS case 5: docs/ + specs/ is machines, neutral_only, not mixed
PASS case 5: contrast docs/ + .claude/ is lab, not neutral_only
PASS case 6: .beads/-only direct commit is excluded
PASS case 6: contrast .beads/ + roles/ is not excluded
PASS case 7: chore(x): direct commit is excluded
PASS case 7: contrast feat(x): is not excluded
PASS case 8: 2026-03-31T23:59:59Z is out
PASS case 8: contrast 2026-04-01T00:00:00Z is in
PASS case 8: 2026-04-01T01:59:59+02:00 is out (UTC)
PASS case 9: unknown in-scope opener stops naming author map
PASS case 9: contrast known opener does not stop
PASS case 10: galadriel and lowercase eudicy are agent
PASS case 10: contrast Galadriel (case differs) stops
PASS case 11: month at p-bar 0.2 with n=30 gives no signal
PASS case 11: contrast month at 0.9 with n=30 gives a signal
PASS case 11: month with n=4 is flagged and left out of p-bar
PASS case 12: third merged PR without own merge stops naming {94, 113}
PASS case 12: contrast only 94 and 113 without own merge does not stop
PASS case 9,12: real snapshot passes every guard (passing direction)
27/27 checks passed
```

## Reconciliation

```text
PASS delivered PRs + absorbed = merged PRs: 126 vs 126
PASS delivered PRs = merge commits: 124 vs 124
PASS delivered direct commits = direct baseline: 36 vs 36
PASS discarded + closed Dependabot = closed PRs: 16 vs 16
```

## Deliberate break

```text
deliberate break: dropped direct commit e43c6d1
PASS delivered PRs + absorbed = merged PRs: 126 vs 126
PASS delivered PRs = merge commits: 124 vs 124
FAIL delivered direct commits = direct baseline: 35 vs 36
PASS discarded + closed Dependabot = closed PRs: 16 vs 16
exit=1
```

## Stratified spot-check (seed 20261120)

Hand classification from `git diff --stat M^1 M` / `git show --stat`,
compared with the script. 10 of 10 match.

| Item | Hand: lab vs machines files, rule | Hand result | Script |
| --- | --- | --- | --- |
| #73 feat hcloud | 3 lab (.claude, .specify) vs 6 playbooks | machines | machines |
| #32 feat flutter role | 7 lab (.claude, memory-bank-branches) vs 6 (roles, configure-linux-roles.yml) | lab, mixed | lab |
| #81 fix molecule runs | title fix | rework (vote lab 3:2) | rework |
| #129 Dependabot bump | opener app/dependabot | automated | automated |
| 121b978 ai: shared skills | 5 lab (.agents, .claude) vs 0, Stefan Boos | lab, manual | lab, manual |
| ec1006d improvement: omc setup prompt | 0 lab vs 1 roles (.beads neutral), Eudicy | machines, agent | machines, agent |
| #48 ci: fork-safe Docker CI | 9 lab vs 13 machines | machines | machines |
| #140 docs ADR-006 | docs only | machines, neutral-only | machines |
| #40 fix tmux restore | title fix, wonderbird | rework, manual | rework, manual |
| #104 discarded deps update | closed 2026-09-06, stefanboos | discarded 2026-09, manual | discarded 2026-09, manual |

Observation for question 3: #32 follows the rule but not the intent;
memory-bank notes outvote the role files.

The owner ruled on 2026-11-20, after this spot-check, that `memory-bank*/`
is machines work. In the rerun that produced `counts.json`, #32 is machines
(1 lab file vs 12 machines files). The planted cases (27/27) and the
reconciliation (4/4) still pass.
