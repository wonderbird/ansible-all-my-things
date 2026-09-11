# Version-Update Apply-Order Checker

`check-version-update-order.py` is a static gate over the apply phase of
[`playbooks/update-versions/perform-updates.yml`](../../playbooks/update-versions/perform-updates.yml).
It reads that playbook as text, reconstructs what each task does, and fails
when the task order could write a version pin that does not belong with the
checksums beside it.

`.github/workflows/playbook-order-lint.yml` runs it, and this directory's test
suite, on every change under `playbooks/` or here. It needs no network, no
Podman and no pip, and finishes in about a second.

## The problem it solves

Every role defaults file in this repository carries a comment requiring its
version pin and its checksum pins to be updated together. Nothing enforced
that. `perform-updates.yml` applies tools one after another, and a tool's
section could write its version pin first and only then fetch that same tool's
checksums.

That ordering is a live hazard, not a theoretical one. When an upstream
download 404'd part-way through a run, the affected tool's version had already
been bumped to the new tag while its checksum still held the previous version's
digest — a defaults file that looks updated, installs nothing, and fails only
on the next machine build.

Further hazards are worse, because nothing observable reports them:

- `tasks/fetch-checksum-from-file.yml` sets a single play-scoped
  `fetched_checksum` fact that each include overwrites. Every reader must
  therefore consume it before the next include runs. Hoisting the includes
  together — an obvious-looking tidy-up — leaves every reader resolving to the
  last include's value. Several roles then receive the same wrong digest, no
  task fails, `failed=0` holds, and a second run is stably wrong, so a
  diff-based idempotency probe passes too.
- A reorder can transpose a pair of per-architecture values, or take a digest
  from another tool's alias. Both write plausible, distinct digests into
  plausible pins. Neither is visible to a positional check, to a distinctness
  check, or to a human reading a large reorder diff.

None of these surface until a role installs the tool on a real machine, which
is why they are worth a gate rather than a review convention.

## The apply-phase ordering contract

This is the authoritative statement of the contract.
[`docs/architecture/version-update-playbooks.md`](../../docs/architecture/version-update-playbooks.md)
describes the mechanism and links here for it.

- **Per-tool ordering.** Within a tool's section, no network or checksum task
  may follow that tool's first `replace`.
- **`fetched_checksum` adjacency.** Every task that reads the shared
  `fetched_checksum` fact must be the task immediately after its own
  `tasks/fetch-checksum-from-file.yml` include. The rule binds any reader, not
  only a `set_fact` alias: deleting an alias and interpolating the raw fact
  into a `replace` produces exactly the same corruption.
- **Pairing.** A per-architecture pin must be written from a value whose own
  name carries the same platform token, and a checksum pin fed from a
  `fetched_*` alias must be fed from its own alias rather than another tool's.

The contract is deliberately **not** full atomicity. Ansible has no
transaction, so an abort part-way through the phase still leaves a prefix of
the tools updated — and that partial progress is wanted: an outage in one tool
should not discard the tools already updated correctly before it. What the
contract guarantees is that each individual tool's pin and checksums are
consistent with one another, which is what the defaults files ask for.

An alternative shape was available: hoist every network task out of the apply
phase, leaving only `replace` calls. It was not taken. It *creates* the
`fetched_checksum` aliasing hazard above rather than avoiding it, it makes a
run all-or-nothing across every tracked upstream, and it splits each tool into
two halves hundreds of lines apart. Its one advantage — an invariant you can
confirm by reading a single line — is obtained here instead by making the
invariant machine-checked.

## How the checker works

The pipeline is a chain of stages, each a small pass over the previous one's
output.

1. **Slice.** Find the apply-phase marker comment in `perform-updates.yml` and
   split everything after it into tasks on `- name:` boundaries. Everything
   before the marker is the fetch phase and is not this gate's subject.
2. **Classify.** A task is a WRITE if it is an `ansible.builtin.replace`
   targeting a `defaults/main.yml` under the roles directory; the path names
   the role. A task is a FETCH if it does network or disk I/O — `get_url`,
   `stat`, `uri`, or an include of a `tasks/fetch-*` file. Each task also
   records the `fetched_*` facts its body interpolates.
3. **Attribute.** WRITE tasks teach the checker which role each `fetched_*`
   fact feeds. FETCH tasks are then attributed to a role through the facts they
   interpolate, or, failing that, through the stem of an included
   `tasks/fetch-<role>-version.yml`.
4. **Judge.** The rules run over that classification: ordering and pairing on
   the attributed tasks, adjacency on the readers of the shared fact, plus two
   rules about the analysis itself — a FETCH that cannot be attributed to any
   role is an error rather than a pass (Principle XII, fail loud), and the
   number of roles analysed must equal the number of stale-check clauses in
   `query-versions.yml`.

That last rule does double duty. Deriving the expectation from
`query-versions.yml` avoids a second definition of the tracked-tool set
(Principle XI) and means a narrowed analysis cannot report a clean subset — if
the phase marker moves or a tool is dropped, the count disagrees and the run
fails. It is also a Constitution II registration check: a tool wired into
`perform-updates.yml` but never registered in `query-versions.yml` is reported
by name.

Report and exit code come from one function, so every finding is printed before
the process exits non-zero. There is no partial output and no first-error stop.

### Known limits of attribution

The secondary attribution path requires an included fetch file's stem to match
the **role directory**, while this repository names such files after the
*tool* — `fetch-android-version.yml` feeds the `android_studio` role. A future
tool following that convention lands in "cannot attribute". That is noisy
rather than dangerous: the checker fails closed, so the gate goes red and asks
for a `fetched_<role>_*` fact or a role-named file instead of passing the task
over.

One diagnosability quirk rides along. Roles are learned from WRITE tasks, and
the first role a `fetched_*` fact is seen with wins. If a WRITE interpolates a
foreign tool's fact, that fact stays bound to the wrong role for the rest of
the run, so the ordering rule can report a real defect against the wrong
section. The pairing rule reports the same defect correctly, so the gate still
goes red for the right reason — but a reader following only the ordering line
is sent to the wrong place.

## Running it

```bash
python3 scripts/version-update-order/check-version-update-order.py \
    playbooks/update-versions/perform-updates.yml
python3 scripts/version-update-order/test_check_version_update_order.py
```

The test suite generates its fixtures by mutating the live
`playbooks/update-versions/*.yml` pair into a temporary directory, rather than
checking in a copy of the playbook, so a fixture cannot drift away from the
file the gate actually protects (Principle XI).

## Cost, and how this shrinks

The checker is a recorded Principle IV (Simplicity/YAGNI) exception, as
[`.specify/memory/constitution.md`](../../.specify/memory/constitution.md)
Governance requires. A static analyser and a dedicated workflow are more
machinery than the observed defect strictly demands; fixing the upstream source
of the tool that 404'd resolves the reported symptom on its own. Justified
because the alternative is a per-tool ordering rule maintained by hand, and the
planning of the very change that introduced this checker enumerated the
affected sections incorrectly on its first attempt. The silent-corruption modes
above are invisible to a test run, to `failed=0` and to an idempotency diff.

The complexity is reducible. Giving `tasks/fetch-checksum-from-file.yml` a
result-variable parameter would remove the shared-fact aliasing at its root:
each include would write its own named fact, the adjacency hazard would become
unrepresentable, and both the adjacency rule and the alias half of the pairing
rule could be deleted outright. It was not bundled into the change that
introduced this checker because it touches every call site (tracked in
`ansible-all-my-things-x3wy`).

The gate also does not address the abort cascade it was written in response to:
a fetch failure still aborts the run at that point, masking every tool after
it. Per-tool failure isolation — accumulating failures and reporting them
together — is tracked in `ansible-all-my-things-clf3`.
