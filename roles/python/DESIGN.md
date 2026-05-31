<!-- SPDX-License-Identifier: MIT-0 -->

# python role — Design Notes

## Package name: `pipx` not `python3-pipx`

Ubuntu 24.04 (Noble) ships the pipx tool as the `pipx` package. The name
`python3-pipx` does not exist in the Noble repositories. The package is in
the `universe` component, which is enabled by default in Ubuntu 24.04 images.

## `python3-full` rather than `python3`

`python3-full` includes `python3-venv` and `ensurepip`, required for tools
that create isolated virtual environments. The minimal `python3` package omits
these, which causes failures in pipx and related tooling. This role preserves
the `python3-full` install that previously lived inline in `setup-desktop.yml`.

## `uv` rejected

`uv` requires a curl-pipe-to-shell installer with no apt package, which
violates Principle I (Idempotency). `pipx` is available via apt and installs
idempotently.

## No universe repository manipulation

Ubuntu 24.04 enables the `universe` component by default. No `apt_repository`
task is needed. Adding one would introduce an architecture-sensitive URL
(amd64 uses `archive.ubuntu.com`, arm64 uses `ports.ubuntu.com`) with no
benefit on an already-configured system.
