from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class InitError(Exception):
    pass
