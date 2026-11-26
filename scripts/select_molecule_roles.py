# SPDX-License-Identifier: MIT-0
"""Print the default Molecule scenarios affected by differences from a base."""

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import yaml
from molecule_references import (
    ROLE_NAME,
    RoleReference,
    SelectionError,
    references,
    scenario_playbooks,
)

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
        "scripts/molecule_references.py",
    }
)


@dataclass(frozen=True, slots=True)
class _Entry:
    path: Path
    playbook_dir: Path
    role_dir: Path | None = None


def _inside(root: Path, path: Path, source: Path) -> Path:
    resolved = path.resolve()
    if not path.is_relative_to(root) or not resolved.is_relative_to(root):
        raise SelectionError(f"{source}: {path} must stay inside the checkout")
    return resolved


def _file(root: Path, entry: _Entry, kind: str, target: str) -> Path:
    explicit = re.sub(r"^\{\{\s*playbook_dir\s*\}\}", str(entry.playbook_dir), target)
    directories = [entry.path.parent]
    if kind != "import_playbook":
        directories.append(entry.playbook_dir)
        if kind == "vars":
            directories.append(entry.playbook_dir / "vars")
        if entry.role_dir is not None:
            directories.extend(
                (
                    entry.role_dir,
                    entry.role_dir / ("vars" if kind == "vars" else "tasks"),
                )
            )

    # Do not guess Ansible's precedence if multiple search locations match.
    candidates = {
        Path(os.path.abspath(directory / explicit)) for directory in directories
    }
    matches = {path for path in candidates if path.is_file()}
    if len(matches) != 1:
        raise SelectionError(f"{entry.path}: cannot uniquely resolve {kind} {target!r}")
    path = matches.pop()
    _inside(root, path, entry.path)
    return path


def _role_directory(root: Path, entry: _Entry, name: str) -> Path | None:
    candidates = (entry.playbook_dir / "roles" / name, root / "roles" / name)
    matches = {path for path in candidates if path.is_dir()}
    if len(matches) == 0 and name.count(".") >= 2:
        return None  # External collection roles are installed through requirements.yml.
    if len(matches) != 1:
        raise SelectionError(f"{entry.path}: cannot uniquely resolve role {name!r}")
    directory = matches.pop()
    _inside(root, directory, entry.path)
    return directory


def _role_entries(directory: Path, entry: _Entry, role: RoleReference) -> list[_Entry]:
    files = []
    overrides = dict(role.entries)
    for kind in ("meta", "tasks", "handlers", "defaults", "vars"):
        name = overrides.get(kind, "main")
        base = directory / kind / name
        # An explicit suffix names one exact role entry, not another convention.
        candidates = (
            (base,)
            if base.suffix != ""
            else (base, base.with_suffix(".yml"), base.with_suffix(".yaml"))
        )
        matches = [path for path in candidates if path.is_file()]
        if len(matches) > 1 or (kind in overrides and len(matches) != 1):
            raise SelectionError(
                f"{entry.path}: cannot uniquely resolve role entry {base}"
            )
        if kind in {"meta", "tasks", "handlers"}:
            files.extend(
                _Entry(path, entry.playbook_dir, directory) for path in matches
            )
    return files


def _scenario_affected(root: Path, role_dir: Path, changed: set[Path]) -> bool:
    # Seed with Molecule's playbooks and the scenario role, not every YAML file.
    scenario = role_dir / "molecule" / "default"
    config = _Entry(scenario / "molecule.yml", scenario)
    _inside(root, config.path, config.path)
    pending = [
        _Entry(path, path.parent)
        for target in scenario_playbooks(config.path)
        for path in [_file(root, config, "import_playbook", target)]
    ]
    pending.extend(_role_entries(role_dir, config, RoleReference(role_dir.name)))
    directories = {_inside(root, role_dir, config.path), role_dir}
    inputs = {config.path}
    visited: set[_Entry] = set()

    # A file can resolve references differently under two playbook directories.
    while len(pending) > 0:
        entry = pending.pop()
        if entry in visited:
            continue
        visited.add(entry)
        inputs.update((entry.path, _inside(root, entry.path, entry.path)))
        for reference in references(entry.path):
            if isinstance(reference, RoleReference):
                directory = _role_directory(root, entry, reference.name)
                if directory is not None:
                    directories.update((directory, directory.resolve()))
                    pending.extend(_role_entries(directory, entry, reference))
            else:
                path = _file(root, entry, reference.kind, reference.target)
                if reference.kind == "vars":
                    inputs.update((path, path.resolve()))
                elif reference.kind == "import_playbook":
                    pending.append(_Entry(path, path.parent))
                else:
                    pending.append(_Entry(path, entry.playbook_dir, entry.role_dir))

    # Files, templates, defaults and vars of a reached role are scenario inputs.
    return any(
        path in inputs
        or any(
            path.is_relative_to(directory)
            and not (path.parent == directory and path.suffix.lower() == ".md")
            for directory in directories
        )
        for path in changed
    )


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
            ROLE_NAME.fullmatch(role) is None for role in scenarios
        ):
            raise SelectionError(f"{_RUNNER} --list returned invalid scenario names")

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
            if len(changed) == 0:
                scenarios = []
            elif _SHARED_INPUTS.isdisjoint(changed):
                paths = {root / path for path in changed}
                scenarios = [
                    scenario
                    for scenario in scenarios
                    if _scenario_affected(root, root / "roles" / scenario, paths)
                ]
    except (
        SelectionError,
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
