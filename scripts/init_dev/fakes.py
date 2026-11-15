"""Fake executables that stand in for external tools in the unit tests.

A test states what its fake does; these helpers do the plumbing that every
fake shares: writing the script, logging its calls, and putting it on PATH.
"""

import os
import textwrap


def write_fake(path, behaviour="", log=None):
    # A shell script that logs the arguments of each call, if given a log,
    # then runs the behaviour.
    script = "#!/bin/sh\n"
    if log is not None:
        script += f'echo "$@" >> "{log}"\n'
    script += textwrap.dedent(behaviour)

    return write_executable(path, script)


def write_executable(path, script):
    path.write_text(script)
    path.chmod(0o755)
    return path


def logged_calls(log):
    # One line per call. No log means no call.
    return log.read_text().splitlines() if log.exists() else []


def first_on_path(bin_dir):
    # The environment that makes the fakes in bin_dir win over the real tools.
    return {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
