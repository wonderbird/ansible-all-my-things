# Tests

## Manual Tests

Automatic tests are missing. Since 2025-07-12, the project has been
transitioning from a "proof of concept" stage toward a more mature stage
[wardley2020], [harrer2023]. For local VM-based role isolation testing, see
[role-development-workflow.md](../docs/architecture/concepts/role-development-workflow.md).

## Host architecture map

For the architecture and provider of each host, see the infrastructure table
in [README.md](../README.md#overview).

ARM64 hosts skip AMD64-only roles via `--skip-tags not-supported-on-vagrant-arm64`.
Docker hosts skip roles needing a full desktop environment via
`--skip-tags not-supported-on-vagrant-docker` (the Docker Ubuntu image has no
XFCE desktop; the Tart provider does).

## AWS Instance Type Guidelines

### Recommended Instance Types for Testing

**t3.micro**: Default choice for all AWS tests

- Free tier eligible (subject to account limits)
- Sufficient for most testing scenarios
- Minimum costs, if free tier limit exceeded

### Cost Considerations

- Always destroy AWS and Hetzner Cloud instances after testing
- Monitor corresponding billing dashboards for unexpected charges

## References

[wardley2020] S. Wardley, “Wardley Maps,” Learn Wardley Mapping. Accessed: Sep. 29, 2022. [Online]. Available: [https://learnwardleymapping.com/book/](https://learnwardleymapping.com/book/)

[harrer2023] M. Harrer, “Evolutionäre Softwarequalität,” presented at the OOP Konferenz, Feb. 09, 2023. [Online]. Available: [https://sigs-new.scoocs.co/event/63/stage/206/session/1729](https://sigs-new.scoocs.co/event/63/stage/206/session/1729)
