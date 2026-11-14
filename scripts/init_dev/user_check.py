"""Refuse to run as root."""
import os

from .common import InitError


def check():
    if os.geteuid() == 0:
        raise InitError(
            "Do not run as root: the clone's .venv and .envrc would belong "
            "to root, and sm and direnv would use root's configuration. "
            "Run as your regular user."
        )
