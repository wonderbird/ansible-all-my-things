"""Find the gates that pytest discovery would miss.

pytest discovery is the only list of fast gates. Each public function here
finds one way a gate can drop out of that list, so a test can fail on it:

- `find_harnesses`: the version-update harness playbooks; none is an error.
- `find_orphan_harness_files`: harness-directory files that no harness runs.
- `collect_test_files`: the test files a plain `pytest` run collects.
- `find_uncollected_test_files`: test files that run is missing.

Every function takes its directories as parameters, raises `GateDiscoveryError`
on input it cannot read, and never prints.
"""

import ast
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path

import yaml

HARNESS_GLOB = "test-*.yml"
_YAML_SUFFIXES = (".yml", ".yaml")
_INCLUDE_KEYS = (
    "include_tasks",
    "import_tasks",
    "ansible.builtin.include_tasks",
    "ansible.builtin.import_tasks",
)
_TEMPLATE_EXPRESSION = re.compile(r"\{\{(.*?)\}\}")
_DOTTED_VARIABLE = re.compile(r"\s*[A-Za-z_]\w*\.([A-Za-z_]\w*)\s*")


class GateDiscoveryError(Exception):
    """A discovery input cannot be read; the message names it and the fix."""


def find_harnesses(tests_dir):
    """Return the sorted top-level `test-*.yml` files of `tests_dir`.

    Raises when there is none, because a loop over zero harnesses passes.
    """
    harnesses = sorted(tests_dir.glob(HARNESS_GLOB))
    if len(harnesses) == 0:
        raise GateDiscoveryError(
            f"{tests_dir / HARNESS_GLOB} matches no harness playbook; "
            f"name each harness test-<name>.yml in {tests_dir}"
        )
    return harnesses


def find_orphan_harness_files(tests_dir):
    """Return the sorted paths, relative to `tests_dir`, that no harness runs.

    Reported are:

    - each top-level `*.yml` or `*.yaml` file that is neither a harness nor
      reachable from one through `include_tasks` or `import_tasks` (short or
      `ansible.builtin.` names, a string or a mapping with `file:`), followed
      from helper to helper. A target resolves relative to `tests_dir`, so
      `../tasks/...` is not an edge. In a templated target each
      `{{ <var>.<key> }}` is a wildcard that a file fills only with a value of
      that same key somewhere in a harness; a value of another key, such as
      `hosts: localhost`, never counts.
    - each YAML file in a subdirectory that contains a play (a top-level list
      item with `hosts:`), because a play there never runs.

    Not followed: `vars_files`, `include_vars`, `import_playbook`, roles,
    lookups and plain path values. A top-level file used only through one of
    them is reported, so the guard learns the form or the file moves.
    Non-YAML files are ignored.
    """
    # Parse every top-level YAML file, so unreadable input fails loud.
    harnesses = find_harnesses(tests_dir)
    top_level = sorted(
        path
        for path in tests_dir.iterdir()
        if path.is_file() and path.suffix in _YAML_SUFFIXES
    )
    parsed = {path.name: _load_yaml(path) for path in top_level}

    # Follow includes from the harnesses until no new file is reached.
    values_by_key = {}
    for harness in harnesses:
        _collect_values_by_key(parsed[harness.name], values_by_key)
    reached = {harness.name for harness in harnesses}
    pending = list(reached)
    while len(pending) > 0:
        name = pending.pop()
        for target in _include_targets(parsed[name]):
            for used in _resolve_include(
                target, tests_dir / name, parsed, values_by_key
            ):
                if used not in reached:
                    reached.add(used)
                    pending.append(used)

    # Add every play hidden in a subdirectory.
    orphans = [path.name for path in top_level if path.name not in reached]
    for path in tests_dir.rglob("*"):
        nested = path.parent != tests_dir and path.suffix in _YAML_SUFFIXES
        if nested and path.is_file() and _contains_play(_load_yaml(path)):
            orphans.append(path.relative_to(tests_dir).as_posix())
    return sorted(orphans)


def collect_test_files(repo_root):
    """Return the absolute paths of the test files a plain `pytest` collects.

    Runs pytest from `repo_root` without a path argument, so it sees what a
    plain run, and therefore `scripts/ci-local.sh`, sees. `PYTEST_ADDOPTS` is
    dropped so a developer's options cannot change the set.
    """
    # Ask pytest for its collected node IDs.
    command = [
        sys.executable,
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        "-p",
        "no:cacheprovider",
    ]
    child_env = dict(os.environ)
    child_env.pop("PYTEST_ADDOPTS", None)
    result = subprocess.run(
        command,
        cwd=repo_root,
        env=child_env,
        capture_output=True,
        text=True,
        check=False,
    )

    # Keep the file part of each node ID; an empty set is an error.
    node_ids = [line for line in result.stdout.splitlines() if "::" in line]
    if result.returncode != 0 or len(node_ids) == 0:
        raise GateDiscoveryError(
            f"`{' '.join(command)}` in {repo_root} exited {result.returncode} "
            f"with {len(node_ids)} node IDs; fix the collection error it "
            f"reports:\n{result.stdout}{result.stderr}"
        )
    return {(repo_root / node_id.split("::")[0]).resolve() for node_id in node_ids}


def find_uncollected_test_files(scripts_dir, collected_files):
    """Return the sorted paths, relative to `scripts_dir`, of missed tests.

    A `*.py` file under `scripts_dir` defines a test when it has a function or
    method named `test_*`, or a class whose base name ends in `TestCase`,
    directly or through another class of the same file. It is reported when it
    defines a test, is not named `acceptance_*.py`, and its resolved path is
    not in `collected_files` (absolute paths, as `collect_test_files`
    returns). Directories starting with `.` and `__pycache__` are skipped, as
    pytest skips them.

    Limit: a base class imported from another module is not followed.
    """
    collected = {Path(path).resolve() for path in collected_files}
    uncollected = []
    for path in sorted(scripts_dir.rglob("*.py")):
        relative = path.relative_to(scripts_dir)
        skipped = any(
            part.startswith(".") or part == "__pycache__"
            for part in relative.parts[:-1]
        )
        if skipped or path.name.startswith("acceptance_"):
            continue
        if path.resolve() not in collected and _defines_test(path):
            uncollected.append(relative.as_posix())
    return uncollected


def _load_yaml(path):
    try:
        return yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise GateDiscoveryError(
            f"{path} is not valid YAML; fix its syntax: {e}"
        ) from e


def _walk_mappings(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_mappings(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_mappings(item)


def _collect_values_by_key(node, values_by_key):
    for mapping in _walk_mappings(node):
        for key, value in mapping.items():
            if isinstance(value, str):
                values_by_key.setdefault(key, set()).add(value)


def _include_targets(node):
    for mapping in _walk_mappings(node):
        for key in _INCLUDE_KEYS:
            value = mapping.get(key)
            if isinstance(value, dict):
                value = value.get("file")
            if isinstance(value, str):
                yield value


def _resolve_include(target, including_file, parsed, values_by_key):
    """Return the top-level file names that `target` can name."""
    # Turn each `{{ <var>.<key> }}` into a wildcard bound to its key.
    target = posixpath.normpath(target)
    pattern = ""
    keys = []
    position = 0
    for expression in _TEMPLATE_EXPRESSION.finditer(target):
        dotted = _DOTTED_VARIABLE.fullmatch(expression.group(1))
        if dotted is None:
            raise GateDiscoveryError(
                f"{including_file} includes {target!r}, whose "
                f"{expression.group(0)!r} is not a dotted variable; use "
                "{{ <var>.<key> }} or teach gate_discovery.py the form"
            )
        pattern += re.escape(target[position : expression.start()]) + "(.+?)"
        keys.append(dotted.group(1))
        position = expression.end()
    pattern += re.escape(target[position:])

    # A file is used when each wildcard holds a harness value of its key.
    used = []
    for name in parsed:
        match = re.fullmatch(pattern, name)
        if match is None:
            continue
        filled = zip(keys, match.groups(), strict=True)
        if all(part in values_by_key.get(key, set()) for key, part in filled):
            used.append(name)
    return used


def _contains_play(document):
    if not isinstance(document, list):
        return False
    return any(isinstance(item, dict) and "hosts" in item for item in document)


def _defines_test(path):
    # Parse the file, so unreadable input fails loud.
    try:
        tree = ast.parse(path.read_text(), filename=str(path))
    except SyntaxError as e:
        raise GateDiscoveryError(
            f"{path} does not parse as Python; fix its syntax: {e}"
        ) from e

    # A test function or method anywhere in the module or its classes.
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    scopes = [tree, *classes]
    for scope in scopes:
        for node in scope.body:
            is_function = isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
            if is_function and node.name.startswith("test_"):
                return True

    # A TestCase subclass, directly or through a class of this file.
    test_case_names = set()
    changed = True
    while changed:
        changed = False
        for node in classes:
            bases = {_base_name(base) for base in node.bases}
            is_test_case = any(
                name.endswith("TestCase") or name in test_case_names for name in bases
            )
            if is_test_case and node.name not in test_case_names:
                test_case_names.add(node.name)
                changed = True
    return len(test_case_names) > 0


def _base_name(base):
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return ""
