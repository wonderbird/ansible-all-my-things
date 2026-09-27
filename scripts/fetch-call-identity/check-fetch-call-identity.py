#!/usr/bin/env python3
"""Fail if a fetch task file stamps fetched_for outside the task writing an output.

Every fetch task file writes its outputs as Ansible facts, and a fact outlives the
loop iteration that set it. A fetch whose output is SKIPPED rather than failed
therefore leaves the previous tool's value readable, and `tasks/fetch-tool.yml`
would record it as this tool's result. The guard is a stamp: the same set_fact
writes `fetched_for: "{{ fetch_call_id }}"`, and the caller refuses any output not
stamped with the identity it asked for.

The stamp only works in the SAME task as the output. Given its own task, a
condition on the output alone leaves a fresh stamp over a stale value, and the
caller's assert passes -- observed: a fetch whose output carried `when: false`
while a separate stamping task ran unconditionally recorded the previous tool's
tag with zero failures.

Nothing at runtime can object to a stamp in the wrong place, because a run where
no output is ever skipped behaves identically. It is therefore checked statically,
here.

A file that COMPOSES another fetch is checked for the mirror fault. Reading an
output another producer wrote makes this file a caller too, and its own caller
only ever sees the LAST stamp: a stamp written after the borrowed value was read
is fresh whether or not that value was. Such a file must assert `fetched_for`
itself.

Scope: every `fetch-*.yml` under the given directory's `tasks/`, except
`fetch-tool.yml`, which is the caller that asserts the stamp rather than a
producer that writes one.

Usage: check-fetch-call-identity.py <directory>
"""
import os
import re
import sys

import yaml

STAMP = "fetched_for"
OUTPUT_PREFIX = "fetched_"
CALLER_FILES = ("fetch-tool.yml",)
# a fetched_* name read inside a template expression
READ = re.compile(r"\{\{[^}]*?\b(" + OUTPUT_PREFIX + r"[a-z0-9_]+)\b[^}]*?\}\}")


def set_fact_mappings(path):
    """Return the set_fact mapping of every task in `path` that has one."""
    with open(path) as handle:
        tasks = yaml.safe_load(handle) or []
    mappings = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        for key, value in task.items():
            if key in ("set_fact", "ansible.builtin.set_fact") and isinstance(value, dict):
                mappings.append((task.get("name", "<unnamed task>"), value))
    return mappings


def outputs_written(path):
    """Return every fetched_* fact `path` writes, the stamp excluded."""
    return {key
            for _, keys in set_fact_mappings(path)
            for key in keys
            if key.startswith(OUTPUT_PREFIX) and key != STAMP}


def borrowed_outputs(path):
    """Return every fetched_* fact `path` reads but never writes itself."""
    with open(path) as handle:
        body = handle.read()
    written = outputs_written(path) | {STAMP}
    return sorted({name for name in READ.findall(body) if name not in written})


def asserts_the_stamp(path):
    """True when `path` asserts the stamp itself rather than trusting its caller."""
    with open(path) as handle:
        tasks = yaml.safe_load(handle) or []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        for key, value in task.items():
            if key not in ("assert", "ansible.builtin.assert"):
                continue
            if STAMP in str((value or {}).get("that", "")):
                return True
    return False


def violations(path):
    """Return every stamping fault in `path`, as a list of messages."""
    mappings = set_fact_mappings(path)
    stamping = [(name, keys) for name, keys in mappings if STAMP in keys]

    if not stamping:
        return [f"writes no {STAMP} stamp at all, so its caller cannot tell this "
                f"fetch's outputs from the previous one's"]

    faults = []
    for name, keys in stamping:
        outputs = [k for k in keys
                   if k.startswith(OUTPUT_PREFIX) and k != STAMP]
        if not outputs:
            faults.append(
                f"stamps {STAMP} in a task that writes no output of its own "
                f"({name!r}). A condition on the output alone would then leave a "
                f"fresh stamp over a stale value, and the caller would accept it.")

    borrowed = borrowed_outputs(path)
    if borrowed and not asserts_the_stamp(path):
        faults.append(
            f"reads {', '.join(borrowed)} from another fetch without asserting "
            f"{STAMP} itself. Its own caller sees only the LAST stamp, which this "
            f"file writes after reading the borrowed value, so a stale borrowed "
            f"value would pass unnoticed.")
    return faults


def scan(root):
    """Return every finding under `root`, as (path, message)."""
    tasks_dir = os.path.join(root, "tasks")
    if not os.path.isdir(tasks_dir):
        tasks_dir = root
    findings = []
    for name in sorted(os.listdir(tasks_dir)):
        if not name.startswith("fetch-") or not name.endswith((".yml", ".yaml")):
            continue
        if name in CALLER_FILES:
            continue
        path = os.path.join(tasks_dir, name)
        findings.extend((path, message) for message in violations(path))
    return findings


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(f"usage: {os.path.basename(__file__)} <directory>", file=sys.stderr)
        return 2

    findings = scan(argv[0])
    for path, message in findings:
        print(f"{path}: STAMP: {message}")

    print(f"\n{len(findings)} call-identity violation(s)")
    if findings:
        print(f"Every fetch task file writes {STAMP} in the same set_fact as an "
              f"output, so a skipped output means a skipped stamp.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
