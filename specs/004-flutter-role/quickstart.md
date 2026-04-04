# Quickstart: Flutter Ansible Role

**Branch**: `004-flutter-role` | **Date**: 2026-04-04

## Prerequisites

Before implementing, confirm:

1. You are on branch `004-flutter-role`.
2. The `android_studio` role exists at `roles/android_studio/` (it is
   the structural template).
3. The `claude_code` role exists at `roles/claude_code/` (it shows the
   `blockinfile` PATH pattern).
4. `configure-linux-roles.yml` exists and contains the `android_studio`
   entry with `tags: not-supported-on-vagrant-arm64`.

## Key Reference Files

| File | Purpose |
| --- | --- |
| `roles/android_studio/tasks/main.yml` | Template for task structure and `get_url` + `unarchive` patterns |
| `roles/android_studio/defaults/main.yml` | Template for checksum variable naming |
| `roles/android_studio/meta/main.yml` | Template for `meta/main.yml` with `dependencies: []` |
| `roles/android_studio/README.md` | Template for role README |
| `roles/android_studio/DESIGN.md` | Template for DESIGN.md |
| `roles/claude_code/tasks/main.yml` | `blockinfile` PATH pattern |
| `configure-linux-roles.yml` | Shows `not-supported-on-vagrant-arm64` tag at role level |

## Implementation Steps (high level)

1. Create `roles/flutter/` directory tree:
   `defaults/`, `meta/`, `tasks/`, plus `README.md` and `DESIGN.md`.

2. Write `defaults/main.yml` with `flutter_version: "3.41.6"` and
   `flutter_sha256`.

3. Write `meta/main.yml` (copy `android_studio` pattern; update
   description).

4. Write `tasks/main.yml` following the task sequence in
   `data-model.md`.

5. Write `README.md` — include `android_studio` as a prerequisite under
   the **Dependencies** section.

6. Write `DESIGN.md` — document the version-file idempotency approach
   and other non-obvious decisions.

7. Add the `flutter` entry to `configure-linux-roles.yml` after
   `android_studio`, with `tags: not-supported-on-vagrant-arm64`.

8. Test locally on an AMD64 Vagrant VM (isolate the `flutter` role per
   `CONTRIBUTING.md`).

9. Test idempotency: run the playbook twice and confirm no `changed`
   tasks on the second run.

10. Test ARM64 skip: run on ARM64 Vagrant VM; confirm all tasks skipped.

## Flutter Version Upgrade Procedure

To upgrade Flutter:

1. Find the new stable version and SHA-256 at
   `https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json`.
2. Update `flutter_version` and `flutter_sha256` in
   `roles/flutter/defaults/main.yml`.
3. Re-run the playbook. The version mismatch triggers re-download and
   re-extraction automatically.
