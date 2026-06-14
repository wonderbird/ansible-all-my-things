# ADR-003: SSH Host-Key Verification Policy for VM Providers

Date: 2026-06-13
Status: Accepted
Deciders: Stefan (Product Owner)

## Context and Problem Statement

`create-vm.yml` and `destroy-vm.yml` provision disposable machines through
pluggable providers: `tart` (laptop-local macOS VMs), `docker` (laptop-local
containers), and `hcloud` (Hetzner Cloud servers). Each provider's inventory
entry sets `ansible_ssh_common_args`, which controls how Ansible treats the
target's SSH host key.

The laptop-local providers disable host-key verification entirely:

```text
-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
```

Every connection is treated as first contact, so a *changed* host key is never
detected. For a laptop-local target that is unremarkable. The new `hcloud`
provider, however, creates a server with a **public IPv4 address reachable over
SSH from the entire internet**. Modelling it on the existing providers — as the
provider pattern invites — would carry the laptop-local "trust any key, never
check" setting onto a path that is no longer trusted.

The subject here is the `create-vm.yml`/`destroy-vm.yml` providers. The
separate, pre-existing developer-server workflow
(`provisioners/hcloud-linux.yml`, `destroy-hcloud-tasks.yml`) already pins host
keys with `ssh-keyscan` into the operator's global `~/.ssh/known_hosts` and
removes them with a bare `ssh-keygen -R`; that workflow is out of scope and
unchanged. So the real choice for the new provider is between disabled
verification, keyscan-pin-to-global, and the policy below — not merely
"`/dev/null` vs verify".

Decision: **should host-key verification be uniform across providers, or depend
on the target's network exposure — and if exposure-based, what policy should
cloud providers use?**

### Scope

The `ansible_ssh_common_args` host-key policy for every `create-vm.yml` /
`destroy-vm.yml` provider (current `tart`, `docker`, `hcloud`; future cloud
providers such as AWS), and the matching `known_hosts` lifecycle on create and
destroy.

Out of scope: SSH authentication method (key vs password, already decided per
provider), and network attack-surface controls (firewalls, source-IP scoping).

### Blast Radius

Single-maintainer repository for personal VM setup. Cloud targets are
short-lived disposable test servers, not multi-tenant production. The worst
case of a successful man-in-the-middle on a cloud connection: an attacker
observes and rewrites one Ansible run against one disposable box — but that run
may push Ansible Vault secrets, so data-plane exposure is real even when the
host is throwaway. The policy is sized to that: meaningful protection on the
exposed path, minimal machinery on the local path.

## Threat Model

Host-key verification detects **man-in-the-middle (MITM)**: an attacker on the
network path who presents a substitute host key and proxies or tampers with the
session. The relevant variables are the network path and the consequence of a
successful MITM.

**Laptop-local (`tart`, `docker`).** The path is `127.0.0.1` or a host-only /
NAT bridge; traffic never leaves the machine. A MITM requires prior code
execution on the laptop, at which point host-key checking is moot. Fresh
clones/rebuilds rotate the host key every create, so persisting it yields only
`REMOTE HOST IDENTIFICATION HAS CHANGED` noise. **MITM risk negligible;
verification value near zero.**

**Cloud (`hcloud`, future AWS).** The path traverses LAN, ISP, and the public
internet. Rogue Wi-Fi, ARP/DNS spoofing, a compromised router, BGP hijack, or a
malicious ISP can attempt MITM. `hcloud` authenticates with an SSH **key pair**,
which limits the damage — a MITM cannot replay the key-auth signature to the
real host and never sees the private key, so it cannot steal the key or pivot.
But it still owns the data plane: it can read and rewrite every command and
harvest any secret the run pushes. **MITM risk real; confidentiality/integrity
impact high.**

**First-contact (TOFU) limit.** A fresh cloud server has a host key never seen
before, so the first connection is unavoidably Trust-On-First-Use unless the
key is obtained out-of-band (Option D). Any in-band policy protects against
MITM *after* first contact and against later key changes, not at the first
handshake.

## Decision Drivers

1. **MITM resistance on internet-exposed paths** — protect confidentiality and
   integrity of runs that may carry secrets.
2. **No alert fatigue** — a control that cries wolf (spurious
   identification-changed warnings from recycled IPs) gets ignored; warnings
   must be rare and meaningful.
3. **Fail loud (Principle XII)** — a genuine host-key *change* must stop the
   run, never be silently re-trusted.
4. **Proportionality / simplicity (Principle IV)** — single-operator
   disposable boxes; least machinery that delivers drivers 1–3.
5. **Idempotency & pattern consistency (Principle I)** — idempotent
   `known_hosts` management, aligned with existing repo conventions.

## Considered Options

- **A — Exposure-based split** *(chosen)*: cloud verifies
  (`StrictHostKeyChecking=accept-new` + project-scoped `UserKnownHostsFile`);
  laptop-local keeps `/dev/null`.
- **B — Verify everywhere**: `accept-new` + scoped known_hosts for all
  providers.
- **C — Disable everywhere**: `/dev/null` for all, including cloud.
- **D — Eliminate TOFU**: pin the cloud host key out-of-band (scrape the
  fingerprint from the provider console log, or inject a self-generated host
  key via cloud-init).
- **E — Manual operator workaround**: operator manages `known_hosts` by hand.
- **F — SSH certificate authority** (Teleport, HashiCorp Vault SSH engine,
  Smallstep `step-ca`): hosts present CA-signed certificates; clients trust the
  CA once.
- **G — Keyscan-pin to global known_hosts**: `ssh-keyscan` the fresh server and
  add it to the operator's `~/.ssh/known_hosts`, as the legacy developer-server
  workflow does.

### Pros and Cons

#### A — Exposure-based split (chosen)

- Good: matches protection to threat (driver 1) — verify where the path is
  untrusted, not where it is not.
- Good: `accept-new` trusts a fresh box on first contact but **refuses a
  changed key**, satisfying fail-loud (driver 3) without first-contact
  friction.
- Good: project-scoped, gitignored known_hosts keeps the operator's personal
  `~/.ssh/known_hosts` clean and matches the autogenerated-inventory convention
  (driver 5).
- Good: low machinery — two `ssh_common_args` strings and one destroy step
  (driver 4), reusing the `ssh-keygen -R` teardown primitive the legacy
  workflow already uses.
- Bad: does not close the first-contact TOFU window.
- Bad: relies on reliable key removal on destroy to avoid stale-IP false
  positives (driver 2).
- Bad: two behaviours to understand instead of one.

Mitigations: accept the first-contact gap as residual risk for disposable
boxes, with Option D as a documented opt-in for any non-disposable host; make
destroy's key removal idempotent and run it on the stale-entry path too, so a
recycled IP is clean first contact; document the rule once (this ADR) to offset
the two-behaviour cost.

#### B — Verify everywhere

- Good: one uniform rule.
- Bad: spends complexity on a negligible threat (driver 4); local VMs rotate
  host keys every rebuild, producing frequent failures that harm driver 2 and
  slow the inner dev loop.

Mitigation: per-create `ssh-keygen -R` for local providers would suppress
churn, but re-adds machinery to the path that needs it least — net worse than A.

#### C — Disable everywhere

- Good: zero work; never a host-key warning.
- Bad: leaves the internet-exposed connection with **no MITM protection**
  (violates driver 1) and silently re-trusts changed keys (violates driver 3);
  secrets a run pushes become harvestable by any on-path attacker.

Mitigation: none that preserves the only advantage (zero work) — any real
mitigation turns this into A or D.

#### D — Eliminate TOFU

- Good: closes the first-contact window — strongest protection (best on driver
  1); `StrictHostKeyChecking=yes` becomes safe with console-fingerprint pinning
  (the key-injection variant instead trades the TOFU gap for metadata-service
  exposure).
- Bad: materially more machinery (worst on driver 4); console-log scraping is
  provider-specific and timing-dependent; self-injected keys route the private
  host key through the provider metadata service.

Mitigation: adopt as an opt-in upgrade layered on A for high-value hosts;
prefer console-fingerprint pinning over key injection.

#### E — Manual operator workaround

- Good: no playbook changes.
- Bad: not idempotent or repeatable (harms drivers 2 and 5); easy to forget;
  does not scale to further providers.

Mitigation: wrapping the manual steps into the playbook *is* Option A.

#### F — SSH certificate authority

- Good: eliminates TOFU and per-host key management at scale; auditable,
  supports rotation and short-lived certs; the standard answer for fleets.
- Bad: heavyweight for a single-operator disposable-box project (badly
  disproportionate on driver 4) — a CA to run and secure, host enrolment at
  boot, client trust config; SaaS adds cost and an external dependency.

Mitigation: defer; revisit only if the project grows to a persistent
multi-host fleet.

#### G — Keyscan-pin to global known_hosts

- Good: already implemented and working in the legacy workflow; in-band, no new
  primitive.
- Good: persists the key, so later key changes can be detected.
- Bad: still TOFU — it trusts whatever answers the scan, so it is no more
  MITM-resistant at first contact than `accept-new`.
- Bad: writes to the operator's global `~/.ssh/known_hosts`, the pollution the
  scoped-file approach avoids (driver 5); on disposable boxes that file fills
  with dead entries.
- Bad: a bare scan does not itself *refuse* a changed key on reconnect unless
  paired with strict checking — the protection is incidental, not enforced.

Mitigation: scope the keyscan to a per-provider file and pair it with strict
checking — at which point it converges on Option A but with an extra
`ssh-keyscan` round-trip and no first-contact benefit over `accept-new`.

## Decision Outcome

Chosen: **Option A — Exposure-based split**, with **Option D available as a
documented opt-in** for any future non-disposable cloud host.

| Provider class | `StrictHostKeyChecking` | `UserKnownHostsFile` | Destroy |
| --- | --- | --- | --- |
| Laptop-local (`tart`, `docker`) | `no` | `/dev/null` | no known_hosts step |
| Cloud (`hcloud`, future AWS) | `accept-new` | `inventories/<provider>_known_hosts` (gitignored) | idempotent `ssh-keygen -f <file> -R <ip>` |

Option A is the only choice that satisfies the top three drivers (MITM
resistance, no alert fatigue, fail-loud) while staying proportional to a
single-operator disposable-box project. It reuses the `ssh-keygen -R` mechanism
the legacy teardown already uses, retargeted from the operator's global
`~/.ssh/known_hosts` to the per-provider scoped file.

On a disposable box every create is a genuinely new server, so a changed key at
create time is expected, not an attack. The protection `accept-new` buys is
therefore primarily **within a run**: the key is pinned at first contact and
enforced for the remainder of that run (and any later connection to the same
persisted host), so a mid-session key swap fails loudly. Across separate
create/destroy cycles of throwaway boxes it protects little — accepted, since
the exposure window that matters is the configuring run that pushes secrets.

### Consequences

- Cloud providers verify the host key on an untrusted path; a changed key on a
  known address fails the run loudly.
- Laptop-local providers keep `/dev/null`; no host-key churn on the inner dev
  loop.
- Create MUST also run an idempotent `ssh-keygen -f <file> -R <ip>` against the
  scoped file *before* connecting, so a public IP reused after a failed or
  skipped teardown is clean first contact rather than a spurious
  `REMOTE HOST IDENTIFICATION HAS CHANGED` failure. Destroy runs the same
  removal, including on the stale-entry path.
- `accept-new` creates the scoped `known_hosts` file if absent; no pre-touch
  step is needed.
- `inventories/<provider>_known_hosts` files — and the `.old` backups
  `ssh-keygen -R` leaves beside them — are local state and must be gitignored.
- The policy assumes single-operator, serial create/destroy. The scoped file is
  rewritten wholesale by `ssh-keygen -R`, so concurrent provisioning could lose
  an append; a future multi-host or parallel-CI provider must revisit file
  locking or per-host files before relying on this.
- The chosen `accept-new` value requires OpenSSH 7.6+ (2017); modern
  macOS/Linux are unaffected.
- A future AWS provider inherits the cloud row of the table.
