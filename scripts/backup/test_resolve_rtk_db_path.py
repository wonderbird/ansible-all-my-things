"""pytest suite for resolve_rtk_db_path.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from resolve_rtk_db_path import resolve  # noqa: E402


def _write_config(tmp_path: Path, content: str) -> None:
    config_dir = tmp_path / ".config" / "rtk"
    config_dir.mkdir(parents=True)
    (config_dir / "config.toml").write_text(content)


def test_default_when_config_absent(tmp_path: Path) -> None:
    assert resolve(str(tmp_path)) == str(
        tmp_path / ".local" / "share" / "rtk" / "history.db"
    )


def test_default_when_key_missing(tmp_path: Path) -> None:
    _write_config(tmp_path, "[other]\nfoo = 'bar'\n")
    assert resolve(str(tmp_path)) == str(
        tmp_path / ".local" / "share" / "rtk" / "history.db"
    )


def test_custom_path_under_home_double_quoted(tmp_path: Path) -> None:
    db = tmp_path / ".local" / "share" / "myrtk" / "db.sqlite"
    _write_config(tmp_path, f'[tracking]\ndatabase_path = "{db}"\n')
    assert resolve(str(tmp_path)) == str(db)


def test_custom_path_under_home_single_quoted(tmp_path: Path) -> None:
    db = tmp_path / ".local" / "share" / "myrtk" / "db.sqlite"
    _write_config(tmp_path, f"[tracking]\ndatabase_path = '{db}'\n")
    assert resolve(str(tmp_path)) == str(db)


def test_path_outside_home_fails(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    _write_config(tmp_path, "[tracking]\ndatabase_path = '/var/lib/rtk/history.db'\n")
    with pytest.raises(SystemExit) as exc:
        resolve(str(tmp_path))
    assert exc.value.code == 1
    assert "outside the user's home directory" in capsys.readouterr().err


def test_path_under_config_fails(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    db = tmp_path / ".config" / "rtk" / "history.db"
    _write_config(tmp_path, f"[tracking]\ndatabase_path = '{db}'\n")
    with pytest.raises(SystemExit) as exc:
        resolve(str(tmp_path))
    assert exc.value.code == 1
    assert "under ~/.config" in capsys.readouterr().err


def test_missing_config_file_falls_back_to_default(tmp_path: Path) -> None:
    (tmp_path / ".config" / "rtk").mkdir(parents=True)
    assert resolve(str(tmp_path)) == str(
        tmp_path / ".local" / "share" / "rtk" / "history.db"
    )


def test_relative_path_fails(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    _write_config(tmp_path, "[tracking]\ndatabase_path = 'relative/path/db'\n")
    with pytest.raises(SystemExit) as exc:
        resolve(str(tmp_path))
    assert exc.value.code == 1
    assert "not an absolute path" in capsys.readouterr().err
