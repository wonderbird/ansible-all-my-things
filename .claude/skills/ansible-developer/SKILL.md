---
name: ansible-developer
description: >
  Use when expert knowledge of Ansible is required to analyze, implement, or
  fix features. Project scope: setting up and maintaining virtual machines.
---
Act as an experienced senior ansible automation developer.

Your goal is to analyze and implement features and to identify and fix bugs.

Use the Context7 library /ansible/ansible-documentation for documentation and
programming guidelines.

## Current Goal

$ARGUMENTS

## Ask when goal unclear

Ask me, if "Current Goal" section empty and context does not clearly identify
goal.

## Constraints

- Whenever you ask me questions, **ask questions one by one**, so that I can
  focus at the individual problem at hand.

## Known Gotchas

Project-specific Ansible pitfalls discovered during implementation. This
section grows over time — check it before re-diagnosing a problem that may
already be solved here. `ansible-technical-coach` references this section directly
rather than duplicating it (Constitution Principle XI), so keep it current
for both personas.

### Windows SSH Readiness Checks

Never use a module-execution-based readiness check (e.g.
`ansible.builtin.wait_for_connection`, which probes with the
`ansible.builtin.ping` module) against a Windows host reached over a plain
`ssh` connection. `ping` needs Python; Windows has none at boot, and the
automatic `ping`→`win_ping` redirect only triggers for `winrm`/`psrp`
connections, never for `ssh`. Symptom: `timed out waiting for ping module
test: 'ping'` — even though the host is fully reachable and authenticating
fine over a manual `ssh` connection. Raising the timeout does not help; the
probe can never succeed regardless of duration.

Use a protocol-level check instead — no module execution needed:
`ansible.builtin.wait_for: {host, port: 22}` (pure TCP), or an
`ssh-keyscan` + `retries` loop that polls until the host key can be
fetched. `playbooks/tasks/create/aws.yml` demonstrates the
`wait_for: port=22` form for `profile == 'windows'`,
alongside the still-`wait_for_connection`-based path used for Linux (which
works there because Linux has Python).

Budget materially more time for Windows boot+readiness than Linux: from
production experience, a Linux server is usually available on the 3rd
readiness-check try, a Windows server on the 13th try.

### Duplicate Mapping Keys

A YAML mapping that declares the same key twice keeps only the last value; a
task with two `vars:` blocks is the common case. Symptom: settings from the
earlier block have no effect,
and the run still exits 0. Cause: YAML keeps the last value of a repeated key.
Ansible only warns about it by default (`DUPLICATE_YAML_DICT_KEY=warn`), and
only when it loads the file: `--syntax-check` never loads a task file that is
included at runtime. `yaml.safe_load` collapses the mapping without any
warning.

Detect the class with a YAML loader that reports a key seen twice, never with
plain `yaml.safe_load`, which cannot see the duplicate. For a single run,
`ANSIBLE_DUPLICATE_YAML_DICT_KEY=error` turns the warning into a failure for
every file Ansible loads. That check needs a real run: `--syntax-check` does
not load files pulled in by `include_tasks`, so it passes them unseen. Prove
the detector on a planted duplicate before trusting a clean result
(Constitution Principle XV).

### Values From `vars_files` Render When Read

In ansible-core 2.21, a value loaded through `vars_files` is a trusted
template. Symptom: merely referencing the variable, for example to validate
it, renders every Jinja expression inside it, and a template that depends on a
variable not yet defined aborts the play. Fix: to inspect the raw text, read
the file with `lookup('ansible.builtin.file', path) | from_yaml`. Values loaded
that way are untrusted, so they stay as written. For an applied example, see
`playbooks/update-versions/tasks/preflight.yml` and
`docs/architecture/version-update-playbooks.md`.

### `default(omit)` in Include Vars Stays Defined

`vars:` on `ansible.builtin.include_tasks` must be a literal mapping, so every
variable a caller might pass is written out by name. A conditional argument
therefore tends to be written as `"{{ x | default(omit) }}"`. Symptom: in the
included file, `x is defined` is true even when the caller had no value.
Cause: `omit` in include vars is not removed; it binds the variable to an omit
placeholder object. Fix: in the callee, test the shape of the value you need
(for example `is sequence and is not string`), never `is defined` alone.
`default(omit)` must never stand in for a required value (Constitution
Principle XII).

### `set_fact` With a Templated Dictionary Sets Nothing

Observed in ansible-core 2.21: `ansible.builtin.set_fact: "{{ some_dict }}"`
reports `ok` but registers none of the dictionary's keys as facts. Fix: to set
a fact whose name is computed, template the key and loop over the names, for
example `ansible.builtin.set_fact: {"{{ item }}": "{{ some_dict[item] }}"}`
with `loop:`.

### Running Playbooks From a Coding Agent

Under a coding agent, `ansible-playbook` can abort with
`ERROR: Ansible requires blocking IO on stdin/stdout/stderr`, because the
agent hands it non-blocking stdin, stdout, and stderr. A gate script then
reports a failure that has nothing to do with the code. Give it fresh handles:
stdin from `/dev/null`, stdout and stderr to a file. Working form:

```bash
log=$(mktemp)
bash scripts/ci-local.sh </dev/null >"$log" 2>&1; echo EXIT=$?; tail -n 20 "$log"
```

A fresh agent VM has no `ansible-playbook` on `PATH`. Create the repository's
gitignored `.venv` from `requirements.txt`, which lists `ansible-core`, then
put `.venv/bin` on `PATH`, or pass the interpreter as the header of
`scripts/ci-local.sh` describes.

### Comment and Documentation Robustness

Describe intent and purpose rather than current implementation specifics.
The rule, its worked examples, and how to handle a document that must state a
current value are defined in `.specify/memory/constitution.md`, Documentation
Standards, under "Write Against Intent, Not Against Implementation Details".
It binds every agent, so it is not restated here (Principle XI).
