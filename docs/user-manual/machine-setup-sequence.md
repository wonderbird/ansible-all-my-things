# Fresh Machine Setup Sequence

When provisioning a new machine, steps must run in this order:

1. **`ansible-playbook restore.yml`** — restores per-project memories and keybindings. Run before provisioning so role-managed content is never overwritten by stale backup state.
2. **`ansible-playbook configure.yml`** — installs all role-managed content: Claude Code binary, plugins, skills symlinks, `settings.json` merge, `rtk init -g`.
3. **`claude login`** — interactive authentication; cannot be automated.
4. **`omc setup`** — interactive OMC configuration; cannot be automated.

Steps 1 and 2 can be scripted. Steps 3 and 4 are always manual.

## What the backup covers

The claude backup archives only irreplaceable user state:

- `~/.claude/projects/` — per-project accumulated memories. Not reproducible from any role.
- `~/.claude/keybindings.json` — custom keybindings.

Everything else under `~/.claude` (plugins, skills, settings, CLAUDE.md, RTK.md) is role-managed and reproduced by step 2.

## Notes

- `~/.claude.json` is not backed up. Re-authenticate via `claude login` (step 3).
- `~/.claude/CLAUDE.md` is not backed up. Verified safe: `omc setup` preserves the user section (including `@RTK.md`) on an existing file.
- Re-running `rtk init -g` after `omc setup` is not required — the user section survives intact.

---

Previous: [Work with a Virtual Machine](./work-with-vm.md)
