# Feature Specification: Version Update Playbooks

**Feature Branch**: `007-version-update-playbooks`
**Created**: 2026-05-12
**Status**: Draft
**Input**: User description: "As the maintainer of this ansible automation project I want to check for updates of installed software packages periodically so that the provisioned machines don't show security vulnerabilities and the users can use up-to-date features."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See What Moved (Priority: P1)

The maintainer sees which pinned tool versions were behind upstream. This was originally a separate query playbook that reported drift without changing anything; it is now the update run itself, which names every tool it updated, skipped or failed, plus `git diff` on the working tree, which shows exactly which pins moved and to what. The separate preview was removed: it could not be acted on differently, and it doubled the cost of a maintenance cycle against the hourly limit of the unauthenticated GitHub API.

**Why this priority**: Knowing what changed is the foundation. A maintainer who cannot see which pins moved cannot review them before committing.

**Independent Test**: Run the update playbook against a repository where at least one version pin is known to be outdated. Verify that the run names that tool and that `git diff` shows the new version.

**Acceptance Scenarios**:

1. **Given** all pinned versions are current, **When** the update playbook runs, **Then** it reports every tool as updated, exits with code 0, and `git diff` is empty.
2. **Given** one or more pinned versions are outdated, **When** the update playbook runs, **Then** `git diff` shows the new version for each stale tool and the run names every tool it updated.
3. **Given** an upstream source is unreachable, **When** the update playbook runs, **Then** that tool is reported as an upstream failure with the message the source produced, every other tool is still updated, and the run exits with a non-zero code.

---

### User Story 2 - Apply Version Updates (Priority: P2)

The maintainer runs a single command to update all stale version pins across role defaults files. The playbook fetches the latest version and paired checksum for each tool and writes both values into the correct defaults file. The maintainer then reviews the changes and commits manually.

**Why this priority**: Closing the loop from detection to remediation. Eliminates error-prone manual lookup of version strings and checksums across multiple upstream sources.

**Independent Test**: Run the update playbook against a repository with at least one known stale pin. Verify that the defaults file contains the new version value and the new checksum value, and that the file structure and comments are preserved.

**Acceptance Scenarios**:

1. **Given** a stale version pin exists, **When** the update playbook runs, **Then** the defaults file for that role contains the latest version string from upstream.
2. **Given** a tool version requires a paired checksum, **When** the update playbook runs, **Then** both the version value and the checksum value are updated together in the same file.
3. **Given** a version pin is already current, **When** the update playbook runs, **Then** the defaults file is not modified.
4. **Given** the update playbook completes, **When** the maintainer inspects the defaults files, **Then** all comments and unrelated content in the files are preserved.
5. **Given** the update playbook completes, **Then** no git commit is created automatically — the maintainer retains full control over committing.

---

### User Story 3 - Understand the Update Mechanism (Priority: P3)

The maintainer reads concept documentation that explains the purpose of the update playbooks, which tools are tracked, where their upstream versions come from, known constraints, and how to run the playbooks.

**Why this priority**: Documentation prevents future maintainers from needing to reverse-engineer the mechanism and ensures known limitations (such as HTML scraping fragility) are visible.

**Independent Test**: A new maintainer unfamiliar with the feature can read the concept document and successfully run the update playbook without additional guidance.

**Acceptance Scenarios**:

1. **Given** the concept document exists, **When** a maintainer reads it, **Then** they can identify the upstream source for every tracked tool.
2. **Given** the concept document exists, **When** a maintainer reads it, **Then** they understand which constraints apply (unauthenticated API limits, HTML scraping risk, SHA-1 vs SHA-256 per tool) and that the Android SHA-1 risk is tracked in `docs/architecture/technical-debt/technical-debt.md` as TD-009.

---

### Edge Cases

- What happens when an upstream source returns an unexpected version format that cannot be parsed?
- What happens when the Android developer page changes its structure and HTML scraping breaks?
- What happens when all pinned versions are already current — does the update playbook complete cleanly without modifying files?
- What happens when the SDKMAN API returns multiple patch versions for the same major — is the highest patch correctly selected?
- What happens when a GitHub API rate limit is hit during a run?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-003**: The update playbook MUST fetch the latest version for each tracked tool from its upstream source and write the updated value to the role defaults file.
- **FR-004**: When a tool version requires a paired checksum, the update playbook MUST update both the version value and the checksum value together in a single operation.
- **FR-005**: The update playbook MUST NOT create git commits or make any changes to version control state.
- **FR-006**: The tracked tools MUST be enumerated in exactly one place, and each kind of upstream source MUST be implemented by exactly one fetch task file, reused by every tool that shares that shape. Duplication of either the enumeration or the fetch logic is not permitted.
- **FR-007**: The update logic for Android SDK command-line tools MUST be isolated in a separate task file, distinct from the shared fetch tasks, to contain the risk of HTML scraping fragility.
- **FR-008**: The update playbook MUST run on the control node (localhost) without requiring a connection to any managed host.
- **FR-009**: Concept documentation MUST be created in `docs/architecture/` covering: purpose, directory structure, per-tool upstream sources, known constraints, and usage instructions.
- **FR-010**: The update playbook MUST preserve all comments and unrelated content in defaults files when writing updated values.
- **FR-011**: When the GitHub API rate limit is reached (HTTP 403 with rate-limit response headers), the affected tool MUST be recorded as an upstream failure with an explicit message identifying GitHub as the source and the rate-limit window, and MUST have none of its pins written. The run MUST continue with the remaining tools, MUST report every failure it collected, and MUST exit with a non-zero exit code. Silently skipping a tool, or writing a version without the checksums that belong with it, is not permitted.
- **FR-012**: All upstream-fetch task files MUST fail with an explicit error message identifying the upstream source when the response cannot be parsed (e.g. unexpected format, missing field, regex no-match). Silent fallthrough or empty fact values are not permitted.

FR-001 and FR-002 were removed with the query playbook they described; the
surviving requirements keep their original numbers, because a stable identifier
is worth more to anyone citing one than a gapless sequence.

### Key Entities

- **Version Pin**: A key-value pair in a role defaults file that specifies the exact version of a tool to install. May be paired with a checksum.
- **Checksum**: A hash value paired with a version pin, used to verify download integrity. The hash algorithm varies by upstream source (SHA-256 for Flutter, SHA-1 for Android cmdline-tools per TD-009).
- **Upstream Source**: The authoritative external location from which the latest version of a tool is fetched. Each tool has exactly one upstream source (structured API or HTML page).
- **Tracked Tool**: A tool whose version pin is managed by the update playbook. Declared as one entry of the tool registry, which names the role, the upstream source, the digests the tool needs and the pins it writes. The registry is the authoritative enumeration; the first increment covered Flutter SDK, gitmux, Nerd Fonts (Hack), Android SDK command-line tools and Java (Temurin via SDKMAN).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The maintainer can see which pins moved, and which tools failed, from a single command and the `git diff` it leaves behind.
- **SC-002**: The maintainer can update all stale version pins and their paired checksums across all tracked tools by running a single command.
- **SC-003**: After running the update playbook, every updated defaults file passes an idempotency check — running the update playbook a second time makes no further changes.
- **SC-004**: One unavailable upstream source leaves every other tool updated and reported, rather than hiding them.
- **SC-005**: No manual lookup of version strings or checksum values is required from the maintainer during an update run.

## Assumptions

- First increment scope: no GitHub Actions integration, no per-role targeting, no automatic commits.
- GitHub API is accessed without authentication. The 60-requests-per-hour unauthenticated rate limit is sufficient for manual maintenance runs.
- Java tracking follows same-major patch strategy: latest patch release of the currently pinned major version (Java 21). Major version upgrades remain a manual decision.
- Android SDK command-line tools version and checksum are sourced from the Android developer HTML page. This is an accepted risk documented in TD-009.
- The SDKMAN REST API is used for Java version discovery — the `sdk` CLI is not required on the control node.
