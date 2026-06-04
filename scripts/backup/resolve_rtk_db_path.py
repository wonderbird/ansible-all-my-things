#!/usr/bin/env python3
"""Resolve RTK database path from config.toml, or fall back to the default."""
import sys
import tomllib
from pathlib import Path


def _read_configured_db_path(config_file: Path) -> str | None:
    if not config_file.exists():
        return None
    with open(config_file, "rb") as fh:
        config = tomllib.load(fh)
    return config.get("tracking", {}).get("database_path")


def _validate_db_path(db_path: Path, db_path_str: str, home: Path) -> None:
    if not db_path.is_absolute():
        print(
            f"RTK database_path '{db_path_str}' is not an absolute path.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not db_path.is_relative_to(home):
        print(
            f"RTK database_path '{db_path_str}' is outside the user's home directory;"
            " backup not supported.",
            file=sys.stderr,
        )
        sys.exit(1)

    # ~/.config is a separate backup domain; a db there shifts the archive root.
    if db_path.is_relative_to(home / ".config"):
        print(
            f"RTK database_path '{db_path_str}' is under ~/.config, which shifts the"
            " backup arcroot; backup not supported from this location.",
            file=sys.stderr,
        )
        sys.exit(1)


def resolve(home_dir: str) -> str:
    home = Path(home_dir)
    default_db = home / ".local" / "share" / "rtk" / "history.db"
    config_file = home / ".config" / "rtk" / "config.toml"

    db_path_str = _read_configured_db_path(config_file)
    if db_path_str is None:
        return str(default_db)

    db_path = Path(db_path_str)
    _validate_db_path(db_path, db_path_str, home)
    return str(db_path)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <home_dir>", file=sys.stderr)
        sys.exit(1)
    print(resolve(sys.argv[1]))


if __name__ == "__main__":
    main()
