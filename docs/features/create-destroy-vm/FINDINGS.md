# Review Findings

/developer This is the second instruction in an asynchronous review. The previous instruction produced the file @docs/features/create-destroy-vm/FINDINGS.md and I have added my replies as paragraphs starting with `__Reviewer:__`.

Now it is your turn to process my replies. The following options are possible:

A) **Instruction to record finding:** When I instruct you to record the issue as a finding in beads, then follow the idea of the "record-findings" skill. First, create the corresponding gate, then add the findings. However, skip asking me for feedback on each finding, because the discussion is already finished in the file. After having added the finding to beads, remove it from the FINDINGS.md file.

B) **Request for more information:** Answer the request. Do not add an issue to beads yet. Keep the entry.

## playbooks/vars/hostname_pool_docker.yml

**Finding:** Introducing this dedicated hostname pool is correct. However,
you must rename the existing pool from `playbooks/vars/hostname_pool.yml` to
stay consistent. Also update the references of the folder name itself, e.g.
in specifications, plans and tasks.

**Reply:** Agree on the rename for symmetry —
`playbooks/vars/hostname_pool.yml` → `playbooks/vars/hostname_pool_tart.yml`.
A repo-wide search finds 17 files referencing `hostname_pool.yml`:
`playbooks/tasks/create/tart.yml` (the actual `include_vars`),
`docs/features/create-destroy-vm/README.md`,
`docs/feature-requests/feat.create-destroy-vm/solution-design.md`,
`playbooks/vars/hostname_pool_docker.yml` (comment), plus spec docs under
both `specs/011-docker-vm-provider/` (in-flight) and `specs/009-create-destroy-vm/`
(already-shipped feature spec).

I'd update the live code reference and currently-active docs (README,
`hostname_pool_docker.yml` comment, `specs/011-docker-vm-provider/*`). I'm
less sure about editing `specs/009-create-destroy-vm/*` — those are the
historical record of an already-completed feature, and the constitution
treats git history as the canonical record of past decisions rather than
something to keep retroactively in sync. Open to either; flagging it so the
scope is clear before this becomes an issue.

__Reviewer:__ Specs must always be true, because the system might be recreated according to specs later. The constitution instruction on using git as history shall prevent comments used as history records in code and documentation. The intention of the constitution instruction is to ensure that documentation and code are always current and easy to understand. Please reply to this question: Think hard about the constitution - Should we clarify the corresponding rule so that the intent gets clearer?. Do not file a finding yet.

**Reply 2:** Re-reading the constitution, the "git history is canonical"
rule actually lives in the Governance section's final paragraph, and it is
scoped explicitly to **rules files** — `AGENTS.md`, `CLAUDE.md`, skill
`SKILL.md` files, and the constitution's own Sync Impact Report. It says
these "MUST NOT contain version history, changelogs, or amendment logs" and
"document current operational rules only." It says nothing about
`specs/NNN-*/` directories.

So my hesitation above was me over-extending that rules-files exemption to
specs — the constitution itself doesn't grant specs that exemption. On
reflection, treating `specs/009-create-destroy-vm/*` as a frozen historical
snapshot also conflicts with Principle XI (Avoid Duplication/DRY): once
`specs/011-docker-vm-provider/*` and the live code both use the renamed file,
an unrenamed `specs/009-*` becomes a second, stale "source of truth" for that
filename — a reader recreating the system from `specs/009-*` alone would
recreate a file that no longer matches the codebase.

**Conclusion:** rename throughout, including `specs/009-create-destroy-vm/*`
— all 17 references should be updated to `hostname_pool_tart.yml`.

**On clarifying the constitution:** yes, worth a small clarification, since
the ambiguity came from reading the rules-files exemption too broadly. I'd
propose appending one sentence to the Governance section's final paragraph:

> This exemption applies only to the rules files named above. Feature
> specifications under `specs/NNN-*/` are not exempt: they MUST stay
> consistent with the current codebase (file paths, names, interfaces) for
> any feature they describe, since they serve as the blueprint for
> recreating the system. Git history, not an outdated spec, is the record of
> how an implementation evolved.

This would be a PATCH (clarifying an existing rule's scope, no new
principle). Let me know if you'd like this filed as a finding/amendment for
this round, or handled separately.
