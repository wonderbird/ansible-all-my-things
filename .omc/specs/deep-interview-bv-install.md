# Deep Interview Spec: Install beads viewer (bv) in claude_code role

## Metadata
- Interview ID: bv-install-2026-04-26
- Rounds: 3
- Final Ambiguity Score: 8%
- Type: brownfield
- Generated: 2026-04-26
- Threshold: 0.20
- Initial Context Summarized: no
- Status: PASSED

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.95 | 35% | 0.332 |
| Constraint Clarity | 0.90 | 25% | 0.225 |
| Success Criteria | 0.90 | 25% | 0.225 |
| Context Clarity | 0.90 | 15% | 0.135 |
| **Total Clarity** | | | **0.917** |
| **Ambiguity** | | | **8%** |

## Goal
Add a task to `roles/claude_code/tasks/main.yml` that installs the `bv` (beads viewer) binary
via curl-pipe install script, mirroring the existing `bd` (beads) task, and add a verification
assertion for `bv` to `molecule/default/verify.yml`.

## Constraints
- Install method: `curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/beads_viewer/main/install.sh" | bash`
- Binary lands at `~/.local/bin/bv` (script default; `~/.local/bin` already exists in the role)
- Idempotency guard: `creates: /home/{{ item }}/.local/bin/bv`
- Runs as each desktop user (`become: true`, `become_user: "{{ item }}"`, `loop: "{{ desktop_users }}"`)
- Same `environment:` block as the `bd` task (HOME + PATH)
- No extra dependencies or config needed on Linux
- PATH already covered by existing `.bashrc` blockinfile tasks in the role

## Non-Goals
- No binary tarball approach (curl-pipe install.sh chosen for simplicity)
- No Homebrew / package manager install
- No arch-specific URL construction (upstream install.sh handles arch detection)
- No changes to `defaults/main.yml`, `meta/main.yml`, or `prepare.yml`

## Acceptance Criteria
- [ ] New Ansible task "Install beads viewer" exists in `roles/claude_code/tasks/main.yml`
- [ ] Task uses `ansible.builtin.shell` with curl-pipe to the beads_viewer install.sh
- [ ] Task has `creates: /home/{{ item }}/.local/bin/bv` idempotency guard
- [ ] Task loops over `desktop_users` with `become_user: "{{ item }}"` (same as bd task)
- [ ] `molecule/default/verify.yml` asserts `/home/testuser/.local/bin/bv` exists
- [ ] Molecule idempotence check passes (task is skipped on second run)

## Technical Context

**Existing beads (bd) task in `roles/claude_code/tasks/main.yml`:**
```yaml
- name: Install beads issue tracker
  ansible.builtin.shell:
    cmd: curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
    creates: /home/{{ item }}/.local/bin/bd
  become: true
  become_user: "{{ item }}"
  loop: "{{ desktop_users }}"
  environment:
    HOME: /home/{{ item }}
    PATH: /home/{{ item }}/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

**New task to add immediately after (mirror the above):**
```yaml
- name: Install beads viewer
  ansible.builtin.shell:
    cmd: curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/beads_viewer/main/install.sh" | bash
    creates: /home/{{ item }}/.local/bin/bv
  become: true
  become_user: "{{ item }}"
  loop: "{{ desktop_users }}"
  environment:
    HOME: /home/{{ item }}
    PATH: /home/{{ item }}/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

**Existing bd verification in `molecule/default/verify.yml`:**
```yaml
- name: Check beads binary
  ansible.builtin.stat:
    path: /home/testuser/.local/bin/bd
  register: bd_binary

- name: Assert beads is installed
  ansible.builtin.assert:
    that: bd_binary.stat.exists
    fail_msg: "beads (bd) binary not found"
```

**New bv verification to add immediately after (mirror the above):**
```yaml
- name: Check beads viewer binary
  ansible.builtin.stat:
    path: /home/testuser/.local/bin/bv
  register: bv_binary

- name: Assert beads viewer is installed
  ansible.builtin.assert:
    that: bv_binary.stat.exists
    fail_msg: "beads viewer (bv) binary not found"
```

## Ontology (Key Entities)
| Entity | Type | Fields | Relationships |
|--------|------|--------|---------------|
| beads (bd) | core domain | install_script, binary_path, install_method | installed alongside bv |
| beads viewer (bv) | core domain | install_script, binary_path, install_method | depends on beads data |
| desktop_users | supporting | list of usernames | both bd and bv install per-user |
| molecule verify.yml | external system | stat tasks, assert tasks | verifies both bd and bv |

## Ontology Convergence
| Round | Entity Count | New | Changed | Stable | Stability Ratio |
|-------|-------------|-----|---------|--------|----------------|
| 1 | 2 | 2 | - | - | N/A |
| 2 | 3 | 1 | 0 | 2 | 67% |
| 3 | 4 | 1 | 0 | 3 | 75% |

## Interview Transcript
<details>
<summary>Full Q&A (3 rounds)</summary>

### Round 1
**Q:** Where does the `bv` binary come from — same beads install script, separate binary download, or something else?
**A:** Separate repo (Dicklesworthstone/beads_viewer); README suggests downloading from release page for arm64/amd64 support.
**Ambiguity:** 32% (Goal: 0.80, Constraints: 0.50, Criteria: 0.60, Context: 0.85)

### Round 2
**Q:** The README offers curl-pipe install.sh vs binary tarball. Which should the role use?
**A:** curl-pipe install.sh (same pattern as bd).
**Ambiguity:** 20% (Goal: 0.90, Constraints: 0.80, Criteria: 0.60, Context: 0.90)

### Round 3
**Q:** Should molecule verify.yml assert that bv is installed?
**A:** Yes, add bv verification mirroring the bd check.
**Ambiguity:** 8% (Goal: 0.95, Constraints: 0.90, Criteria: 0.90, Context: 0.90)

</details>
