"""Refuse to run anywhere but on an Ubuntu VM as a regular user."""
import os
import platform

from .common import InitError


def check():
    try:
        distro = platform.freedesktop_os_release().get("ID")
    except OSError:
        distro = None
    if distro != "ubuntu":
        raise InitError(f"Ubuntu required; os-release reports ID={distro!r}.")
    if os.geteuid() == 0:
        raise InitError(
            "Do not run as root: sm would link skills from "
            "/root/.skill-manager."
        )
