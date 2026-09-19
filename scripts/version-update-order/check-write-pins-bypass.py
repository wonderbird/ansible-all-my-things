#!/usr/bin/env python3
"""Fail if a version-update task edits a file without going through write-pins.

Every pin write must go through `tasks/write-pins.yml`, which checks that the
pin it is about to change exists exactly once. A task that edits a role defaults
file directly skips that check, so a renamed pin silently stops being updated --
the defect this ban exists to prevent.

The rule cannot be enforced at runtime: a task that never calls write-pins.yml
simply never runs anything that could object. It is therefore checked
statically, here.

Scope: every YAML file under the given directory, except `tasks/write-pins.yml`
itself, which is where the editing belongs, and `tests/`, whose fixtures write
files on purpose.

Usage: check-write-pins-bypass.py <directory>
"""
import os
import re
import sys

# a file-editing module at key position, FQCN or short name
EDITOR = re.compile(
    r'^\s*(?:-\s+)?(?:ansible\.builtin\.)?'
    r'(replace|lineinfile|blockinfile|copy|template):',
    re.MULTILINE,
)
EXCLUDED_FILES = ("write-pins.yml",)
EXCLUDED_DIRS = ("tests",)


def offending_lines(path):
    """Return (line number, line) for every file-editing module in `path`."""
    with open(path) as handle:
        lines = handle.read().splitlines()
    return [(number, line.strip())
            for number, line in enumerate(lines, start=1)
            if EDITOR.match(line)]


def scan(root):
    """Return every bypass finding under `root`, as (path, line number, line)."""
    findings = []
    for directory, subdirectories, files in os.walk(root):
        subdirectories[:] = [d for d in subdirectories if d not in EXCLUDED_DIRS]
        for name in sorted(files):
            if not name.endswith((".yml", ".yaml")) or name in EXCLUDED_FILES:
                continue
            path = os.path.join(directory, name)
            findings.extend((path, number, line)
                            for number, line in offending_lines(path))
    return findings


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(f"usage: {os.path.basename(__file__)} <directory>", file=sys.stderr)
        return 2

    findings = scan(argv[0])
    for path, number, line in findings:
        print(f"{path}:{number}: BYPASS: edits a file outside tasks/write-pins.yml "
              f"-- {line}")

    print(f"\n{len(findings)} bypass violation(s)")
    if findings:
        print("Every pin write goes through tasks/write-pins.yml, which checks "
              "that the pin exists exactly once. A direct edit skips that check.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
