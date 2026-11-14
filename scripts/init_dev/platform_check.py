"""Refuse to run anywhere but on an Ubuntu VM as a regular user."""
import os
from pathlib import Path

from .common import InitError


def check(os_release=Path("/etc/os-release")):
    ids = set()
    if os_release.is_file():
        ids = {
            line.partition("=")[2].strip('"')
            for line in os_release.read_text().splitlines()
            if line.startswith("ID=")
        }
    if ids != {"ubuntu"}:
        raise InitError(
            f"Ubuntu required; {os_release} reports ID={ids or 'none'}."
        )
    if os.geteuid() == 0:
        raise InitError(
            "Do not run as root: sm would link skills from "
            "/root/.skill-manager."
        )
