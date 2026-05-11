# Solution Design: Unified Vagrant Docker Provisioning

## Approach

Extend the existing `provisioners/{{ provider }}-{{ platform }}.yml` naming
convention with a new file `provisioners/vagrant_docker-linux.yml`. The
`provision.yml` parameter-routing system already supports this pattern via:

```yaml
- include_tasks: provisioners/vagrant_docker-linux.yml
  when: provider == "vagrant_docker" and platform == "linux"
```

No changes to the `provision.yml` routing logic are expected. The only
production deliverable is the new provisioner file, followed by documentation
updates.

## Provisioner Design (`provisioners/vagrant_docker-linux.yml`)

Model after `provisioners/hcloud-linux.yml`. The key tasks are:

1. **Start the VM** using a `shell` task with a `creates:` guard for
   idempotency (Constitution Principle I):

   ```yaml
   - name: Start Vagrant Docker VM
     ansible.builtin.shell:
       cmd: vagrant up
       chdir: test/docker
       creates: test/docker/.vagrant/machines/default/docker/id
   ```

2. **Refresh inventory** so subsequent plays see the new host:

   ```yaml
   - name: Refresh inventory after vagrant up
     ansible.builtin.meta: refresh_inventory
   ```

3. **Reuse existing `configure-linux.yml`** — no new configure logic needed.

The provisioner MUST use hard-coded `chdir: test/docker` (not a variable)
to keep the implementation minimal (Constitution Principle IV — YAGNI).

**Key variable**: `admin_user_on_fresh_system` must be set to `"vagrant"` in
`inventories/group_vars/vagrant_docker/vars.yml` (already present; verify at
implementation time).

## Steps

1. Author `provisioners/vagrant_docker-linux.yml` (~2-3 h).
   Follow the structure of `provisioners/hcloud-linux.yml`.

2. Verify routing: dry-run `provision.yml` with
   `--extra-vars "provider=vagrant_docker platform=linux" --check`
   and confirm the correct provisioner is included.

3. End-to-end test on a clean environment:
   - Run full `provision.yml` command
   - SSH to dagorlad: `ssh vagrant@localhost -p 2223`
   - Confirm `whoami` via `ansible linux -m shell -a whoami`

4. Idempotency check: re-run `provision.yml` twice; no tasks should report
   `changed` for already-configured state.

5. Inventory integration check: `ansible-inventory --graph` must show
   dagorlad under `@linux` and `@vagrant_docker`.

6. Author acceptance tests based on `test/test_vagrant_linux_provisioning.md`
   (if the file does not exist, document the manual steps above as the test
   record).

7. Documentation updates:
   - `docs/user-manual/create-vm.md` — add Vagrant Docker section with
     unified command
   - `test/docker/README.md` — replace manual `vagrant up` + configure
     instructions with unified command

## Definition of Done

- `provisioners/vagrant_docker-linux.yml` exists and passes idempotency check
- `ansible-inventory --graph` shows dagorlad in correct groups
- `docs/user-manual/create-vm.md` documents the unified command
- `test/docker/README.md` updated
- Acceptance tests (manual or automated) recorded and passing

## Relevant Collections

- `hetzner.hcloud` — reference pattern for provisioner structure
- `community.general` — used by configure-linux tasks
