# SPDX-License-Identifier: MIT-0
"""Read static Ansible file and role references without executing playbooks."""

import re
import shlex
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

ROLE_NAME: Final = re.compile(r"[\w-]+(?:\.[\w-]+)*", re.ASCII)
_ROLE_MODULES: Final = frozenset({"include_role", "import_role"})
_FILE_MODULES: Final = frozenset(
    {"import_playbook", "include_tasks", "import_tasks", "include_vars"}
)
_ROLE_PARTS: Final = ("tasks", "handlers", "defaults", "vars")
_LIFECYCLE: Final = (
    "create",
    "prepare",
    "converge",
    "side_effect",
    "verify",
    "cleanup",
    "destroy",
)


class SelectionError(Exception):
    """An input prevents accurate scenario selection."""


@dataclass(frozen=True, slots=True)
class RoleReference:
    name: str
    entries: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class FileReference:
    kind: str
    target: str


def _field(node: Node | None, key: str) -> Node | None:
    if isinstance(node, MappingNode):
        for name, value in node.value:
            if isinstance(name, ScalarNode) and name.value == key:
                return value
    return None


def _load(path: Path) -> Node | None:
    # Compose nodes without constructing Ansible-tagged values or rendering Jinja.
    with path.open(encoding="utf-8") as stream:
        return yaml.compose(stream, Loader=yaml.SafeLoader)


def _literal(node: Node | None, path: Path, label: str) -> str:
    if isinstance(node, ScalarNode) and re.fullmatch(
        r"(?:\{\{\s*playbook_dir\s*\}\}/)?[\w./-]+", node.value
    ):
        return node.value
    raise SelectionError(f"{path}: use a literal path or name for {label}")


def _role(name: str, options: Node | None, path: Path) -> RoleReference:
    if ROLE_NAME.fullmatch(name) is None:
        raise SelectionError(f"{path}: use a literal role name, got {name!r}")
    entries = []
    for part in _ROLE_PARTS:
        override = _field(options, f"{part}_from")
        if override is not None:
            entries.append((part, _literal(override, path, f"{part}_from")))
    return RoleReference(name, tuple(entries))


def _roles(node: Node, key: str, path: Path) -> Iterator[RoleReference]:
    entries = _field(node, key)
    if entries is None:
        return
    if not isinstance(entries, SequenceNode):
        raise SelectionError(f"{path}: expected a list under {key}")
    for entry in entries.value:
        name = _field(entry, "role") if isinstance(entry, MappingNode) else entry
        yield _role(_literal(name, path, key), entry, path)


def _module_name(name: str) -> str:
    return name.removeprefix("ansible.builtin.").removeprefix("ansible.legacy.")


def _actions(task: Node) -> Iterator[tuple[str, Node, Node | None]]:
    for module in _ROLE_MODULES | _FILE_MODULES:
        for name in (module, f"ansible.builtin.{module}", f"ansible.legacy.{module}"):
            arguments = _field(task, name)
            if arguments is not None:
                yield module, arguments, _field(task, "args")

    for key in ("action", "local_action", "module"):
        action = _field(task, key)
        command = (
            _field(action, "module") if isinstance(action, MappingNode) else action
        )
        if isinstance(command, ScalarNode) and command.value.strip() != "":
            words = command.value.split(maxsplit=1)
            module = _module_name(words[0])
            if module in _ROLE_MODULES | _FILE_MODULES:
                if len(words) == 2:
                    yield module, ScalarNode(command.tag, words[1]), action
                else:
                    yield (
                        module,
                        action
                        if isinstance(action, MappingNode)
                        else ScalarNode(command.tag, ""),
                        _field(task, "args"),
                    )


def _arguments(value: Node, options: Node | None, path: Path) -> MappingNode:
    fields = list(options.value) if isinstance(options, MappingNode) else []
    if isinstance(value, MappingNode):
        fields = value.value + fields
    elif isinstance(value, ScalarNode) and value.value != "":
        try:
            tokens = shlex.split(value.value)
        except ValueError as error:
            raise SelectionError(f"{path}: cannot parse action: {error}") from error
        for token in tokens:
            key, separator, argument = token.partition("=")
            key, argument = (key, argument) if separator == "=" else ("file", key)
            fields.insert(
                0, (ScalarNode(value.tag, key), ScalarNode(value.tag, argument))
            )
        # Preserve the repository's existing include_vars paths without rendering Jinja.
        if "{{" in value.value:
            fields.insert(0, (ScalarNode(value.tag, "file"), value))
    return MappingNode("tag:yaml.org,2002:map", fields)


def _vars_files(node: Node, path: Path) -> Iterator[FileReference]:
    entries = _field(node, "vars_files")
    if entries is None:
        return
    for entry in entries.value if isinstance(entries, SequenceNode) else [entries]:
        yield FileReference("vars", _literal(entry, path, "vars_files"))


def _task_references(task: Node, path: Path) -> Iterator[RoleReference | FileReference]:
    for module, value, options in _actions(task):
        args = _arguments(value, options, path)
        if module in _ROLE_MODULES:
            yield _role(_literal(_field(args, "name"), path, module), args, path)
        else:
            target = _literal(_field(args, "file"), path, module)
            yield FileReference("vars" if module == "include_vars" else module, target)

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
                yield from _task_references(child, path)


def references(path: Path) -> Iterator[RoleReference | FileReference]:
    document = _load(path)
    if isinstance(document, MappingNode):
        yield from _roles(document, "dependencies", path)
    elif isinstance(document, SequenceNode):
        for entry in document.value:
            yield from _roles(entry, "roles", path)
            yield from _vars_files(entry, path)
            yield from _task_references(entry, path)


def scenario_playbooks(config: Path) -> Iterator[str]:
    document = _load(config)
    configured: set[str] = set()
    for section in ("provisioner", "ansible"):
        playbooks = _field(_field(document, section), "playbooks")
        if playbooks is None:
            continue
        if not isinstance(playbooks, MappingNode):
            raise SelectionError(f"{config}: expected a mapping of playbooks")
        for name, value in playbooks.value:
            if isinstance(value, MappingNode):
                for _, driver_playbook in value.value:
                    yield _literal(driver_playbook, config, "driver playbook")
            else:
                configured.add(_literal(name, config, "playbook action"))
                yield _literal(value, config, "playbook")
    for action in _LIFECYCLE:
        if action not in configured and (config.parent / f"{action}.yml").is_file():
            yield f"{action}.yml"
    scenario = _field(document, "scenario")
    for sequence in (
        "test_sequence",
        "check_sequence",
        "destroy_sequence",
        "converge_sequence",
    ):
        steps = _field(scenario, sequence)
        if isinstance(steps, SequenceNode):
            for step in steps.value:
                if isinstance(step, ScalarNode):
                    words = step.value.split()
                    if len(words) > 1 and words[0] in {"verify", "side_effect"}:
                        for target in words[1:]:
                            yield _literal(
                                ScalarNode(step.tag, target), config, sequence
                            )
