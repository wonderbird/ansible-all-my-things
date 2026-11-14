"""Names shared by the initialization steps."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class InitError(Exception):
    """A step failed; the message names the cause and the fix."""
