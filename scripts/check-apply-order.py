#!/usr/bin/env python3
"""Fail if a tool's apply-phase network task follows that tool's first write.

Walks the apply phase of playbooks/update-versions/perform-updates.yml task by
task. A task is a WRITE if it is an ansible.builtin.replace targeting
<_roles_dir>/<role>/defaults/main.yml. A task is a FETCH if it performs
network/disk I/O (get_url, stat, uri, or an include of tasks/fetch-*). FETCH
tasks are attributed to a tool by the fetched_* fact their vars interpolate,
mapped to the role they feed.

Five independent checks run over that classification:

1. Ordering -- a FETCH attributed to role R must not appear after the first
   WRITE to R.
2. Adjacency -- every consumer of the shared, play-scoped `fetched_checksum`
   fact must be the task immediately following its own
   tasks/fetch-checksum-from-file.yml include. Any task that reads the fact
   counts, not only a `set_fact` alias: deleting an alias and interpolating
   the raw fact into a `replace` produces the same corruption.
3. Fail closed -- an apply-phase FETCH that cannot be attributed to a role is
   an error, not a pass.
4. Scope -- the number of roles analysed must equal the number of tracked pins
   derived from query-versions.yml, so a narrowed analysis cannot report a
   clean subset.
5. Pairing -- a WRITE to a per-arch pin must interpolate a value whose own name
   carries the same platform token, and a checksum pin fed from a `fetched_*`
   alias must be fed from its own alias rather than another tool's.
"""
import os
import re
import sys

NAME = re.compile(r'^(\s*)-\s+name:\s*(.+)$')
NET = re.compile(r'ansible\.builtin\.(get_url|stat|uri):|include_tasks:\s*tasks/fetch-')
REPLACE = re.compile(r'ansible\.builtin\.replace:')
ROLEPATH = re.compile(r'_roles_dir\s*\}\}/([A-Za-z0-9_]+)/defaults/main\.yml')
FACT = re.compile(r'fetched_([a-z0-9_]+?)(?:_tag|_version|_sha256\w*|_stripped\w*)?\b')
# secondary attribution: tasks/fetch-<role>-version.yml names its own role
INCLUDE_ROLE = re.compile(r'include_tasks:\s*tasks/fetch-([a-z0-9-]+?)-version\.yml')
SHARED = "fetched_checksum"
TOKENS = ("amd64", "arm64", "x86_64", "aarch64", "x64", "linux_amd64", "linux_arm64")
PIN = re.compile(r"replace:\s*'([a-z0-9_]+):\s*\"\{\{\s*([A-Za-z0-9_.]+)")

PHASE_MARKER = "Apply updates to role defaults files"
STALE_CLAUSE = re.compile(r"current_\w+\s*!=\s*fetched_\w+")


def expected_role_count(path):
    """Number of tracked pins, derived from query-versions.yml's stale check.

    That `when:` list is the existing authoritative enumeration of tracked
    pins, so deriving the expectation from it avoids a second definition
    (Principle XI) and turns check 4 into a Constitution II registration
    check: a tool wired into perform-updates.yml but not into
    query-versions.yml is caught here.
    """
    qv = os.path.join(os.path.dirname(os.path.abspath(path)), "query-versions.yml")
    if not os.path.exists(qv):
        return 18
    with open(qv) as handle:
        return len(STALE_CLAUSE.findall(handle.read()))


def parse_tasks(path):
    """Split the apply phase of `path` into tasks."""
    with open(path) as handle:
        lines = handle.read().splitlines()
    start = next(i for i, line in enumerate(lines) if PHASE_MARKER in line)

    tasks = []
    cur = None
    for i in range(start, len(lines)):
        match = NAME.match(lines[i])
        if match:
            if cur:
                tasks.append(cur)
            cur = {"line": i + 1, "name": match.group(2).strip(), "body": []}
        elif cur is not None:
            cur["body"].append(lines[i])
    if cur:
        tasks.append(cur)

    for task in tasks:
        body = "\n".join(task["body"])
        task["is_write"] = bool(REPLACE.search(body))
        task["is_fetch"] = bool(NET.search(body))
        rolepath = ROLEPATH.search(body)
        task["role"] = rolepath.group(1) if rolepath else None
        task["facts"] = set(FACT.findall(body))
    return tasks


def analyse(path):
    """Run all five checks and return their findings."""
    tasks = parse_tasks(path)

    # fact -> role, learned from write tasks
    fact_role = {}
    for task in tasks:
        if task["is_write"] and task["role"]:
            for fact in task["facts"]:
                fact_role.setdefault(fact, task["role"])

    first_write = {}
    for task in tasks:
        if task["is_write"] and task["role"] and task["role"] not in first_write:
            first_write[task["role"]] = task["line"]

    # --- Check 1: per-tool ordering (and check 3: fail closed).
    violations = []
    unattributed = []
    for task in tasks:
        if not task["is_fetch"]:
            continue
        body = "\n".join(task["body"])
        cands = {fact_role[f] for f in task["facts"] if f in fact_role}
        if not cands:
            match = INCLUDE_ROLE.search(body)
            if match:
                cands = {r for r in first_write if r == match.group(1).replace("-", "_")}
        if not cands:
            # fail closed: an apply-phase fetch we cannot attribute is a gap,
            # not a pass (Principle XII).
            unattributed.append((task["line"], task["name"]))
            continue
        for role in cands:
            first = first_write.get(role)
            if first is not None and task["line"] > first:
                violations.append((task["line"], task["name"], role, first))

    # --- Check 2: every consumer of the shared `fetched_checksum` fact must be
    # the task immediately following its own fetch-checksum-from-file include.
    # The fact is play-scoped and overwritten by each include, so any separation
    # silently gives the consumer a different tool's checksum.
    adjacency = []
    for idx, task in enumerate(tasks):
        body = "\n".join(task["body"])
        if re.search(r"\bfetched_checksum\b", body):
            prev = tasks[idx - 1] if idx else None
            prev_body = "\n".join(prev["body"]) if prev else ""
            if not re.search(r"include_tasks:\s*tasks/fetch-checksum-from-file\.yml",
                             prev_body):
                adjacency.append((task["line"], task["name"],
                                  prev["name"] if prev else "<start of phase>"))

    # --- Check 5: platform-token pairing.
    # A `replace` writing a per-arch pin must interpolate a value whose own name
    # carries the SAME platform token. Catches a transposed register/alias pair,
    # which every positional check passes.
    pairing = []
    for task in tasks:
        match = PIN.search("\n".join(task["body"]))
        if not match:
            continue
        pin, src = match.group(1), match.group(2)
        pin_tokens, src_tokens = _tokens(pin), _tokens(src)
        if pin_tokens and src_tokens and not (pin_tokens & src_tokens):
            pairing.append((task["line"], task["name"], pin, src,
                            "/".join(sorted(pin_tokens)),
                            "/".join(sorted(src_tokens))))
            continue
        # A checksum pin fed from a `fetched_*` alias must be fed from its OWN
        # alias. Platform tokens alone do not catch a cross-tool swap: bd's
        # amd64 digest written into bv's amd64 pin agrees on platform and
        # fails only at role install time.
        if src.startswith("fetched_") and "_sha256" in src:
            expected = "fetched_" + pin
            if src != expected:
                pairing.append((task["line"], task["name"], pin, src,
                                expected, "cross-tool"))

    return {
        "violations": sorted(violations),
        "adjacency": adjacency,
        "unattributed": unattributed,
        "pairing": pairing,
        "roles": first_write,
        "expected": expected_role_count(path),
    }


def _tokens(name):
    return {t for t in TOKENS if t in name}


def report(path, result):
    """Print the findings and return the process exit code."""
    for line, name, role, first in result["violations"]:
        print(f"{path}:{line}: fetch for '{role}' runs after its first write "
              f"at :{first} -- {name}")

    for line, name, prev in result["adjacency"]:
        print(f"{path}:{line}: '{name}' reads {SHARED} but does not immediately "
              f"follow its include (previous task: '{prev}')")

    for line, name in result["unattributed"]:
        print(f"{path}:{line}: cannot attribute apply-phase fetch to a role -- {name}"
              f" (add a fetched_<role>_* fact or name the file"
              f" tasks/fetch-<role>-version.yml)")

    for line, name, pin, src, left, right in result["pairing"]:
        if right == "cross-tool":
            print(f"{path}:{line}: PAIRING: '{pin}' is written from '{src}' but "
                  f"its own alias is '{left}' -- another tool's checksum -- {name}")
        else:
            print(f"{path}:{line}: PAIRING: '{pin}' ({left}) is written from "
                  f"'{src}' ({right}) -- transposed platform values -- {name}")

    analysed, expected = len(result["roles"]), result["expected"]
    scope_ok = analysed == expected
    if analysed < expected:
        print(f"{path}: SCOPE ERROR: analysed {analysed} roles, expected "
              f"{expected} -- the apply-phase marker moved or a tool was "
              f"dropped; violations below are NOT trustworthy")
    elif analysed > expected:
        print(f"{path}: SCOPE ERROR: analysed {analysed} roles, expected "
              f"{expected} -- a tool was added here but not to "
              f"query-versions.yml's stale check; register it there "
              f"(Constitution II)")

    print(f"\n{len(result['violations'])} ordering violation(s), "
          f"{len(result['adjacency'])} adjacency violation(s), "
          f"{len(result['unattributed'])} unattributable fetch(es), "
          f"{len(result['pairing'])} pairing violation(s); {analysed} roles written")
    print(f"analysed {analysed}/{expected} roles")

    failed = (result["violations"] or result["adjacency"]
              or result["unattributed"] or result["pairing"] or not scope_ok)
    return 1 if failed else 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: check-apply-order.py <perform-updates.yml>", file=sys.stderr)
        return 2
    path = argv[0]
    return report(path, analyse(path))


if __name__ == "__main__":
    sys.exit(main())
