#!/usr/bin/env bash
# SPDX-License-Identifier: MIT-0
#
# Generic command-runner wrapper that serializes execution against a
# host-wide lock. Solves the cross-worktree `molecule test` container-name
# collision: all roles' molecule.yml hardcode the podman container name
# `instance`, which is a single shared resource per host (not scoped to a
# git worktree), so two concurrent `molecule test` runs for different roles
# can stomp each other's container mid-converge.
#
# Lock dir is a fixed absolute path under /tmp - deliberately NOT
# ${TMPDIR:-/tmp}, because $TMPDIR is per-user on macOS, which would put
# different sessions on different lock paths and silently defeat
# cross-session serialization on that platform.
#
# Usage: ./scripts/with-molecule-lock.sh <command> [args...]
#
# Env:
#   MOLECULE_LOCK_MAX_WAIT  Seconds to wait for the lock before failing
#                           loud. Default 1800 (30min).

set -uo pipefail

if [ "$#" -eq 0 ]; then
  echo "Usage: $(basename "$0") <command> [args...]" >&2
  exit 1
fi

# LOCK_DIR and its .stale.$$ reclaim path below must stay on the same
# filesystem (both hardcoded under /tmp) - atomic rename(2) only holds
# across a single filesystem.
LOCK_DIR="/tmp/ansible-all-my-things-molecule.lock"
MAX_WAIT="${MOLECULE_LOCK_MAX_WAIT:-1800}"
POLL_INTERVAL=1

waited=0

while true; do
  if mkdir "${LOCK_DIR}" 2>/dev/null; then
    # Acquired. Write pid+timestamp atomically (tmp file then mv, never a
    # torn write), then install the cleanup trap - only now that we
    # genuinely hold the lock, never before acquire, so a Ctrl-C during
    # the wait loop below can't delete someone else's lock.
    pid_tmp="${LOCK_DIR}/pid.tmp"
    printf '%s\n%s\n' "$$" "$(date +%s)" >"${pid_tmp}"
    mv "${pid_tmp}" "${LOCK_DIR}/pid"
    trap 'rm -rf "${LOCK_DIR}"' EXIT INT TERM

    "$@"
    exit_code=$?
    exit "${exit_code}"
  fi

  # mkdir failed - the lock is held by someone, or stale.
  if [ ! -f "${LOCK_DIR}/pid" ]; then
    # Narrow window: another process just mkdir'd but hasn't written its
    # pid file yet. Treat as held-not-stale, never attempt reclaim on
    # incomplete info - just fall through to the wait/sleep below.
    :
  else
    holder_pid="$(head -n1 "${LOCK_DIR}/pid" 2>/dev/null || true)"
    if [ -n "${holder_pid}" ] && ! kill -0 "${holder_pid}" 2>/dev/null; then
      # Holder PID is dead - reclaim immediately. No age check, ever:
      # liveness is the only signal that can authorize a reclaim.
      # Atomic rename: only one racing waiter's mv can succeed (rename(2)
      # on an existing path is atomic); the rest get ENOENT here and
      # re-loop to re-read current state.
      stale_dir="${LOCK_DIR}.stale.$$"
      if mv "${LOCK_DIR}" "${stale_dir}" 2>/dev/null; then
        rm -rf "${stale_dir}"
      fi
      continue
    fi
    # Holder PID is alive (or unreadable) - never reclaim, regardless of
    # how long it has held the lock. Liveness is authoritative; age can
    # never override it. Just sleep+retry below.
  fi

  if [ "${waited}" -ge "${MAX_WAIT}" ]; then
    holder_pid="$(head -n1 "${LOCK_DIR}/pid" 2>/dev/null || echo "unknown")"
    echo "ERROR: timed out after ${MAX_WAIT}s waiting for lock ${LOCK_DIR}" >&2
    echo "  Held by PID ${holder_pid}." >&2
    echo "  If that process is gone (e.g. a PID-recycled orphan), clean up manually with:" >&2
    echo "    rm -rf ${LOCK_DIR}" >&2
    exit 1
  fi

  sleep "${POLL_INTERVAL}"
  waited=$((waited + POLL_INTERVAL))
done
