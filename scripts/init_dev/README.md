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

Every change follows the section "Python Scripts" of the
[constitution](../../.specify/memory/constitution.md). The rules below add
what is specific to init_dev.

### Add a step

1. Create the step module, with its entry point as its only public function.
2. Create its `test_<module>.py`.
3. Call the function from `main()` in [`__main__.py`](__main__.py), at the
   point in the sequence where its prerequisites exist.
4. If the step automates a manual instruction in
   [`CONTRIBUTING.md`](../../CONTRIBUTING.md), remove that instruction there;
   its "Initialize a Fresh Clone" section already covers it.
5. Extend the acceptance test with the outcome the new step promises, and
   run it (see below).

### Design rules

- **Standard library only.** The package runs on the system `python3` before
  the venv and its packages exist.
- **One module per step**, with its tests in a sibling `test_<module>.py`.
  Test support that several test modules share, such as the fake executables
  in [`fakes.py`](fakes.py), lives in its own module.
- **Re-runnable.** A second run must leave the clone unchanged and succeed.
- **Fail with `InitError`.** A step raises `InitError` with a message that
  names the cause and the fix; `main()` reports it and exits with 1.

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

The acceptance test needs a provisioned VM and network access and takes about
two minutes, so the default test run skips it. Run it explicitly:

```shell
pytest scripts/init_dev/acceptance_init_dev.py
```

The test modules use relative imports, so a single test file cannot be run
directly with `python3 test_<module>.py`. Select tests through pytest instead,
for example `pytest scripts/init_dev/test_<module>.py`.

[Python Script Tests](../../docs/architecture/concepts/testing.md#python-script-tests)
explains the unit tests, the acceptance test and how CI runs them. When a step
needs a new tool, add the role that installs it to
[`ci_prerequisites.yml`](ci_prerequisites.yml), which provisions the CI
runner.
