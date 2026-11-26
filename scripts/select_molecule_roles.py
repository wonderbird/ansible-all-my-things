# SPDX-License-Identifier: MIT-0
"""Print the default Molecule scenarios affected by differences from a base."""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Final

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

_RUNNER: Final = "scripts/test-molecule-all.sh"
_SHARED_INPUTS: Final = frozenset(
    {
        ".github/workflows/molecule.yml",
        "requirements.txt",
        "requirements.yml",
        _RUNNER,
        "scripts/with-molecule-lock.sh",
        "scripts/select_molecule_roles.py",
    }
)
_ROLE_NAME: Final = re.compile(r"[\w-]+(?:\.[\w-]+)*", re.ASCII)


class _SelectionError(Exception):
    """An input prevents accurate scenario selection."""


def _field(node: Node, key: str) -> Node | None:
    if isinstance(node, MappingNode):
        for name, value in node.value:
            if isinstance(name, ScalarNode) and name.value == key:
                return value
    return None


def _role_name(node: Node | None, path: Path) -> str:
    if isinstance(node, ScalarNode) and _ROLE_NAME.fullmatch(node.value) is not None:
        return node.value
    raise _SelectionError(f"{path}: use a literal role name for Molecule selection")


def _role_list(node: Node, key: str, path: Path) -> set[str]:
    entries = _field(node, key)
    if entries is None:
        return set()
    if not isinstance(entries, SequenceNode):
        raise _SelectionError(f"{path}: expected a list under {key}")
    return {
        _role_name(
            _field(entry, "role") if isinstance(entry, MappingNode) else entry, path
        )
        for entry in entries.value
    }


def _task_roles(task: Node, path: Path) -> set[str]:
    roles = set()
    for module in ("include_role", "import_role"):
        for name in (module, f"ansible.builtin.{module}", f"ansible.legacy.{module}"):
            arguments = _field(task, name)
            if arguments is not None:
                roles.add(_role_name(_field(arguments, "name"), path))
    for key in (
        "pre_tasks",
        "tasks",
        "post_tasks",
        "handlers",
        "block",
        "rescue",
        "always",
    ):
        children = _field(task, key)
        if isinstance(children, SequenceNode):
            for child in children.value:
                roles.update(_task_roles(child, path))
    return roles


def _declared_roles(path: Path) -> set[str]:
    # Inspect YAML nodes without constructing Ansible-tagged values or rendering Jinja.
    with path.open(encoding="utf-8") as stream:
        document = yaml.compose(stream, Loader=yaml.SafeLoader)
    if document is None:
        return set()
    if not isinstance(document, SequenceNode):
        return _role_list(document, "dependencies", path)

    # Scenario YAML can contain a playbook or a task list included by a playbook.
    roles = set()
    for entry in document.value:
        roles.update(_role_list(entry, "roles", path))
        roles.update(_task_roles(entry, path))
    return roles


def _yaml_files(directory: Path) -> list[Path]:
    return [path for path in directory.rglob("*") if path.suffix in {".yml", ".yaml"}]


def _affected_roles(root: Path, scenarios: list[str], changed: set[str]) -> list[str]:
    # Treat a renamed path as a deletion plus an addition, including old role names.
    changed_roles = set()
    for path in changed:
        parts = Path(path).parts
        if len(parts) < 3 or parts[0] != "roles":
            continue
        if len(parts) == 3 and Path(path).suffix.lower() == ".md":
            continue
        changed_roles.add(parts[1])
    if len(changed_roles) == 0:
        return []

    # Keep references to absent roles so deletion still selects surviving consumers.
    role_dependencies: dict[str, set[str]] = {}
    selected = []
    for scenario in scenarios:
        pending = {scenario}
        for path in _yaml_files(root / "roles" / scenario / "molecule" / "default"):
            pending.update(_declared_roles(path))

        visited: set[str] = set()
        while len(pending) > 0:
            role = pending.pop()
            if role in visited:
                continue
            visited.add(role)
            if role not in role_dependencies:
                directory = root / "roles" / role
                paths = [
                    directory / "meta" / filename
                    for filename in ("main.yml", "main.yaml", "main")
                ]
                for kind in ("tasks", "handlers"):
                    paths.extend(_yaml_files(directory / kind))
                role_dependencies[role] = {
                    dependency
                    for path in paths
                    if path.is_file()
                    for dependency in _declared_roles(path)
                }
            pending.update(role_dependencies[role] - visited)
        if not changed_roles.isdisjoint(visited):
            selected.append(scenario)
    return selected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Compare this commit with the checked-out HEAD")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent.parent

    try:
        # Keep the runner as the only authority on which scenarios are runnable.
        discovery = subprocess.run(
            [str(root / _RUNNER), "--list"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
        )
        scenarios = os.fsdecode(discovery.stdout).splitlines()
        if len(scenarios) == 0 or any(
            _ROLE_NAME.fullmatch(role) is None for role in scenarios
        ):
            raise _SelectionError(f"{_RUNNER} --list returned invalid scenario names")

        # Compare the exact trees GitHub will test, rather than only the latest push.
        if args.base is not None:
            diff = subprocess.run(
                [
                    "git",
                    "diff",
                    "--name-only",
                    "--no-renames",
                    "-z",
                    args.base,
                    "HEAD",
                    "--",
                ],
                cwd=root,
                check=True,
                stdout=subprocess.PIPE,
            )
            changed = set(os.fsdecode(diff.stdout).split("\0")) - {""}
            if _SHARED_INPUTS.isdisjoint(changed):
                scenarios = _affected_roles(root, scenarios, changed)
    except (
        _SelectionError,
        OSError,
        subprocess.CalledProcessError,
        yaml.YAMLError,
    ) as error:
        print(f"Molecule selection failed: {error}", file=sys.stderr)
        return 1

    print(" ".join(scenarios))
    return 0


if __name__ == "__main__":
    sys.exit(main())
