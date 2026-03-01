# Technical Debt Register

This document collects known technical debt and accepted risks in the project.
Each entry records the context, the risk, and why it was accepted or deferred.

New entries are appended as they are identified, typically during code reviews.

## Entry format

Each entry uses the following fields:

- **ID** — sequential identifier, e.g. `TD-001`
- **Title** — short description
- **Category** — `Accepted Risk` or `Technical Debt`
- **Severity** — `Critical`, `High`, `Medium`, or `Low`
- **Affected file(s)** — file references
- **Description** — what the issue is and why it matters
- **Mitigation** — controls that reduce the risk today
- **Status** — `Open`, `Resolved`, or `Wont-fix`
- **Date added**

---

## TD-001 — No integrity check on the Claude Code installer script

- **Category:** Accepted Risk
- **Severity:** High
- **Affected file(s):** [roles/claude_code/tasks/main.yml](../../roles/claude_code/tasks/main.yml)
- **Date added:** 2026-02-27

### Description

The Claude Code installer script is downloaded from `https://claude.ai/install.sh` and
executed directly via the `shell` module without any checksum verification.
A compromise of Anthropic's CDN or a supply-chain attack on the install script endpoint
could deliver a malicious script that runs under the target user's account.

The binary integrity verification that follows catches post-installation tampering of the
`claude` binary itself, but it does not protect against harm done by a malicious installer
before the binary is written to disk.

### Mitigation

HTTPS transport provides the primary protection: the TLS connection to `claude.ai`
prevents in-transit modification and authenticates the server's identity.
This is the same trust model used by widely accepted installers such as Homebrew,
rustup, and the official Node.js installer.

Additionally, the subsequent binary checksum verification (comparing the installed binary
against the manifest published by Anthropic) limits the damage a compromised installer
could do to the binary itself.

### Ideas for solution

Use VirusTotal:

- [VirusTotal: URL Scan of https://claude.ai/install.sh](https://www.virustotal.com/gui/url/128ceb81537736671e63bc2d1c028b5cd6cf1749c4a940fcc0646e41be7e0aec/details)

### Status

Open — accepted risk. Revisit if Anthropic publishes installer checksums.
