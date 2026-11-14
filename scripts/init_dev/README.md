# init_dev

Prepares a fresh clone of this repository for development on the Ubuntu VMs
the repository provisions. The steps and their order are listed in `main()` in
[`__main__.py`](__main__.py).

## Usage

Run from the repository root:

```shell
python3 -m scripts.init_dev
```

Every step is safe to re-run. A step that cannot complete stops the script
with a message that names the cause and the fix, for example a tool that the
VM provisioning should have installed.

## Development

### Design rules

- **Standard library only.** The package runs on the system `python3` before
  the venv and its packages exist.
- **Standard library before custom code.** If the standard library already
  solves a part of a step, use it instead of writing our own version.
- **One module per step**, with its tests in a sibling `test_<module>.py`.
- **Re-runnable.** A second run must leave the clone unchanged and succeed.
- **Fail loud.** A step raises `InitError` with a message that names the cause
  and the fix. It never skips silently.
- **Test our own logic.** Mock the standard library and external tools at
  their boundary instead of testing their behaviour.

### Add a step

1. Create the step module with one public function.
2. Create its `test_<module>.py`.
3. Call the function from `main()` in [`__main__.py`](__main__.py), at the
   point in the sequence where its prerequisites exist.
4. If the step automates a manual instruction in
   [`CONTRIBUTING.md`](../../CONTRIBUTING.md), remove that instruction there;
   its "Initialize a Fresh Clone" section already covers it.
5. Extend the acceptance test with the outcome the new step promises, and
   run it (see below).

### Run the tests

From the repository root, with the venv active:

```shell
pytest scripts/init_dev
ptw --now --clear scripts/init_dev    # re-runs the tests on every change
```

Without a venv, for example before the first initialization:

```shell
python3 -m unittest discover -s scripts/init_dev -t .
```

The acceptance test runs the real script twice on a fresh copy of the
working tree, with the real tools, and checks its outcomes. It needs a
provisioned VM and network access and takes about half a minute, so the
default test run skips it. Run it explicitly:

```shell
pytest scripts/init_dev/acceptance_init_dev.py
```

The test modules use relative imports, so a single test file cannot be run
directly with `python3 test_<module>.py`. Select tests through pytest instead,
for example `pytest scripts/init_dev/test_<module>.py`.

### Prove each guard

Before relying on a new or changed check, break it once and confirm that a
test turns red, then restore it (constitution Principle XV).
