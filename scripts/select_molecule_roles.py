# SPDX-License-Identifier: MIT-0
"""Print the default Molecule scenarios affected by differences from a base."""

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Final

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

_RUNNER: Final = "scripts/test-molecule-all.sh"
_SHARED_INPUTS: Final = frozenset(
    {
        ".github/workflows/molecule.yml",
        "ansible.cfg",
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


def _actions(task: Node) -> Iterator[tuple[str, Node]]:
    for module in (
        "include_role",
        "import_role",
        "import_playbook",
        "include_tasks",
        "import_tasks",
    ):
        for name in (module, f"ansible.builtin.{module}", f"ansible.legacy.{module}"):
            arguments = _field(task, name)
            if arguments is not None:
                yield module, arguments
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
                yield from _actions(child)


def _declared_dependencies(path: Path) -> Iterator[tuple[str, str]]:
    # Inspect YAML nodes without constructing Ansible-tagged values or rendering Jinja.
    with path.open(encoding="utf-8") as stream:
        document = yaml.compose(stream, Loader=yaml.SafeLoader)
    if document is None:
        return
    if not isinstance(document, SequenceNode):
        yield from (
            ("role", role) for role in _role_list(document, "dependencies", path)
        )
        return

    # Scenario YAML can contain a playbook or a task list included by a playbook.
    for entry in document.value:
        yield from (("role", role) for role in _role_list(entry, "roles", path))
        for module, arguments in _actions(entry):
            if module in {"include_role", "import_role"}:
                yield "role", _role_name(_field(arguments, "name"), path)
                continue
            target = (
                arguments
                if isinstance(arguments, ScalarNode)
                else _field(arguments, "file")
            )
            if not isinstance(target, ScalarNode) or not re.fullmatch(
                r"[\w./-]+", target.value
            ):
                raise _SelectionError(f"{path}: use a literal file path for {module}")
            yield module, target.value


def _yaml_files(directory: Path) -> list[Path]:
    return [
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix in {".yml", ".yaml"}
    ]


def _import_path(source: Path, target: str, directories: tuple[Path, ...]) -> Path:
    # Do not guess Ansible's precedence if multiple search locations match.
    matches = {
        Path(os.path.abspath(directory / target))
        for directory in directories
        if (directory / target).is_file()
    }
    if len(matches) != 1:
        raise _SelectionError(f"{source}: cannot uniquely resolve import {target!r}")
    return matches.pop()


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
    if len(changed) == 0:
        return []

    # Keep references to absent roles so deletion still selects surviving consumers.
    selected = []
    for scenario in scenarios:
        scenario_dir = root / "roles" / scenario / "molecule" / "default"
        files = [(path, (scenario_dir,)) for path in _yaml_files(scenario_dir)]
        pending_roles = {scenario}
        visited_roles: set[str] = set()
        visited_files: set[tuple[Path, tuple[Path, ...]]] = set()
        input_paths: set[str] = set()

        # Walk files and roles until neither introduces an unvisited dependency.
        while len(files) > 0 or len(pending_roles) > 0:
            if len(pending_roles) > 0:
                role = pending_roles.pop()
                visited_roles.add(role)
                directory = root / "roles" / role
                paths = [
                    directory / "meta" / filename
                    for filename in ("main.yml", "main.yaml", "main")
                ]
                for kind in ("tasks", "handlers"):
                    paths.extend(_yaml_files(directory / kind))
                search = (directory / "tasks", directory, scenario_dir)
                files.extend((path, search) for path in paths if path.is_file())
                continue

            path, search = files.pop()
            if (path, search) in visited_files:
                continue
            visited_files.add((path, search))
            resolved = path.resolve()
            if not path.is_relative_to(root) or not resolved.is_relative_to(root):
                raise _SelectionError(f"{path}: imports must stay inside the checkout")
            input_paths.update(str(file.relative_to(root)) for file in (path, resolved))
            for kind, target in _declared_dependencies(path):
                if kind == "role":
                    if target not in visited_roles:
                        pending_roles.add(target)
                elif kind == "import_playbook":
                    imported = _import_path(path, target, (path.parent,))
                    files.append((imported, (imported.parent,)))
                else:
                    imported = _import_path(path, target, (path.parent, *search))
                    files.append((imported, search))

        if not changed_roles.isdisjoint(visited_roles) or not changed.isdisjoint(
            input_paths
        ):
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
