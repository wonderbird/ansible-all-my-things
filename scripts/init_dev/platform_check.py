"""Refuse to run anywhere but on Ubuntu."""
import platform

from .common import InitError


def check():
    try:
        distro = platform.freedesktop_os_release().get("ID")
    except OSError:
        distro = None
    if distro != "ubuntu":
        raise InitError(f"Ubuntu required; os-release reports ID={distro!r}.")
